from __future__ import annotations

import asyncio
import importlib.util
import os
import re
from collections import Counter, deque
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from .config import REPO_ROOT, SkillConfig
from .policy import make_permission_handler


AUTORESEARCH_REQUIREMENTS_PATH = REPO_ROOT / "tools" / "requirements-autoresearch.txt"
AUTORESEARCH_INSTALL_COMMAND = (
    "python3 -m pip install -r "
    f"{AUTORESEARCH_REQUIREMENTS_PATH.relative_to(REPO_ROOT).as_posix()}"
)

_SUCCESS_EVENT_TYPES = {"session.idle", "session.task_complete"}
_FAILURE_EVENT_TYPES = {"session.error", "session.shutdown"}
_PROGRESS_EVENT_TYPES = {
    "assistant.intent",
    "assistant.message",
    "assistant.message_delta",
    "assistant.reasoning",
    "assistant.reasoning_delta",
    "assistant.streaming_delta",
    "assistant.turn_end",
    "assistant.turn_start",
    "assistant.usage",
    "permission.completed",
    "permission.requested",
    "session.task_complete",
    "session.usage_info",
    "skill.invoked",
    "tool.execution_complete",
    "tool.execution_partial_result",
    "tool.execution_progress",
    "tool.execution_start",
}

_WEB_TOOL_NAMES = {
    "click",
    "find",
    "open",
    "screenshot",
    "search_query",
    "view",
    "web_fetch",
}
_URL_PATTERN = re.compile(r"https?://[^\s<>'\"`]+")
_TRAILING_URL_PUNCTUATION = ".,);:!?]}>\"'"
_SDK_UNMEDIATED_WEB_TOOLS = ("web_fetch",)


@dataclass
class SessionRecorder:
    tool_names: list[str] = field(default_factory=list)
    requested_urls: list[str] = field(default_factory=list)
    attempted_urls: list[str] = field(default_factory=list)
    approved_urls: list[str] = field(default_factory=list)
    tool_arg_urls: list[str] = field(default_factory=list)
    event_urls: list[str] = field(default_factory=list)
    source_urls: list[str] = field(default_factory=list)
    read_paths: list[str] = field(default_factory=list)
    write_paths: list[str] = field(default_factory=list)
    shell_commands: list[str] = field(default_factory=list)
    event_types: list[str] = field(default_factory=list)

    async def on_pre_tool_use(
        self, input_data: dict[str, Any], invocation: dict[str, str]
    ) -> None:
        tool_name = input_data.get("toolName")
        if tool_name:
            normalized_tool_name = str(tool_name)
            self.tool_names.append(normalized_tool_name)
            if _is_web_facing_tool(normalized_tool_name):
                urls = _extract_urls_from_value(input_data.get("toolArgs"))
                if urls:
                    self.tool_arg_urls.extend(urls)
                    self.attempted_urls.extend(urls)

    def on_event(self, event: Any) -> None:
        event_type = _event_type_name(event)
        if event_type:
            self.event_types.append(event_type)
        if event_type not in {
            "permission.requested",
            "permission.completed",
            "tool.execution_start",
            "tool.execution_complete",
            "tool.execution_partial_result",
            "tool.execution_progress",
        }:
            return

        data = _as_mapping(getattr(event, "data", None))
        if not data:
            return

        if event_type.startswith("tool.execution"):
            tool_name = _extract_tool_name_from_payload(data)
            if tool_name and tool_name not in self.tool_names:
                self.tool_names.append(tool_name)
            urls: list[str] = []
            for payload in (
                data.get("arguments"),
                data.get("toolArgs"),
                data.get("url"),
                data.get("urls"),
                data.get("result"),
                data.get("toolTelemetry"),
                data.get("tool_telemetry"),
            ):
                urls.extend(_extract_urls_from_value(payload))
            if urls:
                self.event_urls.extend(urls)
                self.attempted_urls.extend(urls)
            if (
                event_type == "tool.execution_complete"
                and tool_name
                and _is_web_facing_tool(tool_name)
                and _tool_execution_succeeded(data)
            ):
                self.source_urls.extend(_extract_urls_from_value(data.get("result")))
            return

        urls: list[str] = []
        for payload in (
            data.get("request"),
            data.get("result"),
            data.get("url"),
            data.get("urls"),
        ):
            urls.extend(_extract_urls_from_value(payload))
        if urls:
            self.requested_urls.extend(urls)
            if event_type == "permission.completed":
                self.approved_urls.extend(urls)


@dataclass(frozen=True)
class CopilotRuntimeDiagnostics:
    last_event_type: str | None
    recent_event_counts: tuple[tuple[str, int], ...]
    assistant_message_received: bool
    last_assistant_text: str | None
    timeout_kind: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "last_event_type": self.last_event_type,
            "recent_event_counts": [
                {"event_type": event_type, "count": count}
                for event_type, count in self.recent_event_counts
            ],
            "assistant_message_received": self.assistant_message_received,
            "last_assistant_text": self.last_assistant_text,
            "timeout_kind": self.timeout_kind,
        }


@dataclass(frozen=True)
class CopilotRunResult:
    final_text: str
    tool_names: tuple[str, ...]
    requested_urls: tuple[str, ...]
    attempted_urls: tuple[str, ...]
    approved_urls: tuple[str, ...]
    tool_arg_urls: tuple[str, ...]
    event_urls: tuple[str, ...]
    source_urls: tuple[str, ...]
    read_paths: tuple[str, ...]
    write_paths: tuple[str, ...]
    shell_commands: tuple[str, ...]
    runtime_diagnostics: CopilotRuntimeDiagnostics


class CopilotSessionRuntimeError(RuntimeError):
    def __init__(self, message: str, *, diagnostics: CopilotRuntimeDiagnostics) -> None:
        super().__init__(message)
        self.diagnostics = diagnostics


class SessionProgressTracker:
    def __init__(self, *, loop: asyncio.AbstractEventLoop, recent_limit: int = 50) -> None:
        self._loop = loop
        self.started_at = loop.time()
        self.last_progress_at = self.started_at
        self.last_event_type: str | None = None
        self.last_assistant_text: str | None = None
        self.assistant_message_received = False
        self.completion_event = asyncio.Event()
        self.failure_message: str | None = None
        self.completion_event_type: str | None = None
        self.recent_event_types: deque[str] = deque(maxlen=recent_limit)

    def on_event(self, event: Any) -> None:
        event_type = _event_type_name(event)
        if not event_type:
            return

        self.last_event_type = event_type
        self.recent_event_types.append(event_type)

        if event_type in _PROGRESS_EVENT_TYPES:
            self.last_progress_at = self._loop.time()

        if event_type == "assistant.message":
            text = _extract_final_text(event).strip()
            self.assistant_message_received = True
            if text:
                self.last_assistant_text = text

        if event_type in _SUCCESS_EVENT_TYPES:
            self.completion_event_type = event_type
            self.completion_event.set()
            return

        if event_type in _FAILURE_EVENT_TYPES:
            self.failure_message = _extract_final_text(event).strip() or event_type
            self.completion_event.set()

    def build_diagnostics(self, *, timeout_kind: str | None = None) -> CopilotRuntimeDiagnostics:
        counts = Counter(self.recent_event_types)
        recent_event_counts = tuple(
            sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        )
        return CopilotRuntimeDiagnostics(
            last_event_type=self.last_event_type,
            recent_event_counts=recent_event_counts,
            assistant_message_received=self.assistant_message_received,
            last_assistant_text=self.last_assistant_text,
            timeout_kind=timeout_kind,
        )


def get_copilot_sdk_preflight_error() -> str | None:
    if importlib.util.find_spec("copilot") is not None:
        return None
    return (
        "Missing local autoresearch dependency `github-copilot-sdk`. "
        f"Install it with `{AUTORESEARCH_INSTALL_COMMAND}`."
    )


def create_copilot_client(
    *,
    env: dict[str, str],
    github_token: str | None,
    use_logged_in_user: bool,
    connection: Any | None = None,
) -> Any:
    from copilot import CopilotClient

    options: dict[str, Any] = {
        "working_directory": str(REPO_ROOT),
        "env": env,
        "github_token": github_token,
        "use_logged_in_user": use_logged_in_user,
    }
    if connection is not None:
        options["connection"] = connection
    return CopilotClient(**options)


def get_provider_config(provider_name: str, model: str | None) -> dict[str, Any] | None:
    if provider_name == "github-token":
        return None
    if provider_name != "byok-openai":
        raise ValueError(f"Unsupported provider '{provider_name}'")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required when provider=byok-openai")
    model = model or os.environ.get("OPENAI_MODEL")
    if not model:
        raise RuntimeError("A model must be provided when provider=byok-openai")

    return {
        "type": "openai",
        "wire_api": "responses",
        "base_url": os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        "api_key": api_key,
    }


def compute_hard_cap_timeout(inactivity_timeout: float) -> float:
    return max(inactivity_timeout + 120.0, min(inactivity_timeout * 4.0, 1800.0))


async def validate_github_token_auth(client: Any) -> None:
    auth = await client.get_auth_status()
    if auth.isAuthenticated:
        return
    detail = auth.statusMessage or "Not authenticated"
    raise RuntimeError(f"GitHub-token Copilot auth unavailable: {detail}")


async def wait_for_session_completion(
    *,
    session: Any,
    tracker: SessionProgressTracker,
    inactivity_timeout: float,
    hard_cap_timeout: float,
) -> None:
    loop = asyncio.get_running_loop()
    start_time = loop.time()
    tracker.last_progress_at = start_time

    while not tracker.completion_event.is_set():
        now = loop.time()
        inactivity_remaining = inactivity_timeout - (now - tracker.last_progress_at)
        hard_cap_remaining = hard_cap_timeout - (now - start_time)

        if inactivity_remaining <= 0:
            raise await _build_timeout_error(
                session=session,
                tracker=tracker,
                timeout_kind="inactivity",
                timeout_seconds=inactivity_timeout,
            )
        if hard_cap_remaining <= 0:
            raise await _build_timeout_error(
                session=session,
                tracker=tracker,
                timeout_kind="hard_cap",
                timeout_seconds=hard_cap_timeout,
            )

        wait_seconds = min(inactivity_remaining, hard_cap_remaining, 1.0)
        try:
            await asyncio.wait_for(tracker.completion_event.wait(), timeout=wait_seconds)
        except TimeoutError:
            continue

    if tracker.failure_message:
        diagnostics = tracker.build_diagnostics()
        raise CopilotSessionRuntimeError(
            _format_runtime_failure(
                f"Copilot session failed before completion: {tracker.failure_message}",
                diagnostics=diagnostics,
            ),
            diagnostics=diagnostics,
        )


async def run_session(
    *,
    prompt: str,
    attachments: list[dict[str, str]],
    provider_name: str,
    model: str | None,
    allow_writes: bool,
    allow_eval_tightening: bool,
    run_profile: str,
    allow_live_research: bool,
    config: SkillConfig,
    system_message: str,
    timeout: float = 900.0,
) -> CopilotRunResult:
    try:
        return await _run_session_once(
            prompt=prompt,
            attachments=attachments,
            provider_name=provider_name,
            model=model,
            allow_writes=allow_writes,
            allow_eval_tightening=allow_eval_tightening,
            run_profile=run_profile,
            allow_live_research=allow_live_research,
            config=config,
            system_message=system_message,
            timeout=timeout,
        )
    except Exception as exc:
        fallback_model = model or os.environ.get("OPENAI_MODEL")
        if (
            provider_name == "github-token"
            and os.environ.get("OPENAI_API_KEY")
            and fallback_model
            and _looks_like_auth_failure(exc)
        ):
            return await _run_session_once(
                prompt=prompt,
                attachments=attachments,
                provider_name="byok-openai",
                model=fallback_model,
                allow_writes=allow_writes,
                allow_eval_tightening=allow_eval_tightening,
                run_profile=run_profile,
                allow_live_research=allow_live_research,
                config=config,
                system_message=(
                    f"{system_message}\n\n"
                    "Note: this session fell back to the configured BYOK OpenAI provider because "
                    "GitHub-token Copilot auth was unavailable."
                ),
                timeout=timeout,
            )
        raise


async def _run_session_once(
    *,
    prompt: str,
    attachments: list[dict[str, str]],
    provider_name: str,
    model: str | None,
    allow_writes: bool,
    allow_eval_tightening: bool,
    run_profile: str,
    allow_live_research: bool,
    config: SkillConfig,
    system_message: str,
    timeout: float,
) -> CopilotRunResult:
    recorder = SessionRecorder()
    effective_model = model or (os.environ.get("OPENAI_MODEL") if provider_name == "byok-openai" else None)
    provider = get_provider_config(provider_name, effective_model)
    env = os.environ.copy()
    github_token = None
    use_logged_in_user = True
    if provider_name == "github-token":
        github_token = (
            env.get("COPILOT_GITHUB_TOKEN")
            or env.get("GITHUB_TOKEN")
            or env.get("GH_TOKEN")
        )
        use_logged_in_user = not bool(github_token)

    client = create_copilot_client(
        env=env,
        github_token=github_token,
        use_logged_in_user=use_logged_in_user,
    )
    session = None
    try:
        await client.start()
        if provider_name == "github-token":
            await validate_github_token_auth(client)

        loop = asyncio.get_running_loop()
        tracker = SessionProgressTracker(loop=loop)

        def on_event(event: Any) -> None:
            recorder.on_event(event)
            tracker.on_event(event)

        session = await client.create_session(
            on_permission_request=make_permission_handler(
                config=config,
                allow_writes=allow_writes,
                allow_eval_tightening=allow_eval_tightening,
                run_profile=run_profile,
                allow_live_research=allow_live_research,
                recorder=recorder,
                attachment_paths=tuple(
                    attachment["path"]
                    for attachment in attachments
                    if attachment.get("type") in {"file", "directory"}
                    and attachment.get("path")
                ),
            ),
            model=effective_model,
            provider=provider,
            working_directory=str(REPO_ROOT),
            system_message={"mode": "append", "content": system_message},
            hooks={"on_pre_tool_use": recorder.on_pre_tool_use},
            on_event=on_event,
            excluded_tools=list(_SDK_UNMEDIATED_WEB_TOOLS),
            streaming=True,
        )
        await session.send(prompt, attachments=attachments)
        await wait_for_session_completion(
            session=session,
            tracker=tracker,
            inactivity_timeout=timeout,
            hard_cap_timeout=compute_hard_cap_timeout(timeout),
        )

        final_text = tracker.last_assistant_text or ""
        if not final_text:
            events = await session.get_events()
            final_text = _extract_final_text_from_history(events)
            if final_text:
                tracker.last_assistant_text = final_text
                tracker.assistant_message_received = True
            if events and not tracker.last_event_type:
                tracker.last_event_type = _event_type_name(events[-1])

        return CopilotRunResult(
            final_text=final_text.strip(),
            tool_names=tuple(recorder.tool_names),
            requested_urls=tuple(sorted(set(recorder.requested_urls))),
            attempted_urls=tuple(sorted(set(recorder.attempted_urls))),
            approved_urls=tuple(sorted(set(recorder.approved_urls))),
            tool_arg_urls=tuple(sorted(set(recorder.tool_arg_urls))),
            event_urls=tuple(sorted(set(recorder.event_urls))),
            source_urls=tuple(sorted(set(recorder.source_urls))),
            read_paths=tuple(sorted(set(recorder.read_paths))),
            write_paths=tuple(sorted(set(recorder.write_paths))),
            shell_commands=tuple(dict.fromkeys(recorder.shell_commands)),
            runtime_diagnostics=tracker.build_diagnostics(),
        )
    finally:
        if session is not None:
            try:
                await session.disconnect()
            except Exception:
                pass
        await client.stop()


async def _build_timeout_error(
    *,
    session: Any,
    tracker: SessionProgressTracker,
    timeout_kind: str,
    timeout_seconds: float,
) -> CopilotSessionRuntimeError:
    await _abort_session_quietly(session)
    try:
        events = await session.get_events()
    except Exception:
        events = []

    final_text = _extract_final_text_from_history(events)
    if final_text:
        tracker.last_assistant_text = final_text
        tracker.assistant_message_received = True
    if events:
        tracker.last_event_type = _event_type_name(events[-1]) or tracker.last_event_type

    diagnostics = tracker.build_diagnostics(timeout_kind=timeout_kind)
    if timeout_kind == "inactivity":
        summary = (
            f"Copilot session timed out after {timeout_seconds:.1f}s of inactivity "
            "before reaching completion."
        )
    else:
        summary = (
            f"Copilot session hit the internal hard cap after {timeout_seconds:.1f}s "
            "before reaching completion."
        )
    return CopilotSessionRuntimeError(
        _format_runtime_failure(summary, diagnostics=diagnostics),
        diagnostics=diagnostics,
    )


async def _abort_session_quietly(session: Any) -> None:
    try:
        await session.abort()
    except Exception:
        return


def _looks_like_auth_failure(exc: Exception) -> bool:
    message = str(exc).lower()
    return any(
        token in message
        for token in (
            "auth unavailable",
            "authentication",
            "not authenticated",
            "unauthorized",
            "forbidden",
            "401",
            "403",
        )
    )


def _format_runtime_failure(
    prefix: str,
    *,
    diagnostics: CopilotRuntimeDiagnostics,
) -> str:
    detail_parts = []
    if diagnostics.last_event_type:
        detail_parts.append(f"last event `{diagnostics.last_event_type}`")
    detail_parts.append(
        "assistant message received"
        if diagnostics.assistant_message_received
        else "no assistant message received"
    )
    if diagnostics.last_assistant_text:
        detail_parts.append(
            f"last assistant text `{_truncate_text(diagnostics.last_assistant_text, 160)}`"
        )
    if diagnostics.recent_event_counts:
        detail_parts.append(
            "recent events "
            + ", ".join(
                f"`{event_type}` x{count}"
                for event_type, count in diagnostics.recent_event_counts[:8]
            )
        )
    return f"{prefix} ({'; '.join(detail_parts)})"


def _truncate_text(text: str, limit: int) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _extract_final_text(event: Any) -> str:
    if event is None:
        return ""
    data = getattr(event, "data", None)
    if data is None:
        return ""
    for field in ("content", "summary_content", "message"):
        value = getattr(data, field, None)
        if value:
            return str(value)
    return ""


def _extract_final_text_from_history(messages: list[Any]) -> str:
    for event in reversed(messages):
        if _event_type_name(event) == "assistant.message":
            text = _extract_final_text(event).strip()
            if text:
                return text
    return ""


def _event_type_name(event: Any) -> str | None:
    event_type = getattr(event, "type", None)
    if event_type is None:
        return None
    return getattr(event_type, "value", str(event_type))


def _is_web_facing_tool(tool_name: str) -> bool:
    normalized = tool_name.strip().lower()
    return normalized in _WEB_TOOL_NAMES or normalized.startswith("web_")


def _tool_execution_succeeded(payload: dict[str, Any]) -> bool:
    """Return true only for a completed web tool result without failure markers."""
    result = payload.get("result")
    if result is None:
        return False

    for candidate in (payload, _as_mapping(result)):
        for key in ("success", "ok", "isSuccess"):
            if key in candidate and candidate[key] is False:
                return False
        for key in ("error", "errors", "exception"):
            if candidate.get(key):
                return False
        status = candidate.get("status")
        if isinstance(status, str) and status.strip().lower() in {
            "cancelled",
            "canceled",
            "denied",
            "error",
            "failed",
        }:
            return False
    return True


def _extract_tool_name_from_payload(payload: dict[str, Any]) -> str | None:
    for key in ("toolName", "tool_name", "name"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _as_mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if hasattr(value, "__dict__"):
        return {
            str(key): item
            for key, item in vars(value).items()
            if not key.startswith("_")
        }
    return {}


def _extract_urls_from_value(value: Any, *, _seen: set[int] | None = None) -> list[str]:
    if _seen is None:
        _seen = set()

    if value is None or isinstance(value, (int, float, bool)):
        return []

    if isinstance(value, str):
        return _extract_urls_from_text(value)

    value_id = id(value)
    if value_id in _seen:
        return []
    _seen.add(value_id)

    if isinstance(value, dict):
        urls: list[str] = []
        for key, item in value.items():
            if isinstance(key, str):
                urls.extend(_extract_urls_from_text(key))
            urls.extend(_extract_urls_from_value(item, _seen=_seen))
        return urls

    if isinstance(value, (list, tuple, set)):
        urls: list[str] = []
        for item in value:
            urls.extend(_extract_urls_from_value(item, _seen=_seen))
        return urls

    if hasattr(value, "__dict__"):
        return _extract_urls_from_value(_as_mapping(value), _seen=_seen)

    return []


def _extract_urls_from_text(text: str) -> list[str]:
    urls: list[str] = []
    for match in _URL_PATTERN.findall(text):
        normalized = _normalize_url(match)
        if normalized:
            urls.append(normalized)
    return urls


def _normalize_url(candidate: str) -> str | None:
    trimmed = candidate.strip().rstrip(_TRAILING_URL_PUNCTUATION)
    if not trimmed:
        return None
    parsed = urlsplit(trimmed)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return urlunsplit(parsed)
