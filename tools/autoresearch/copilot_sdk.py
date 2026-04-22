from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from .config import REPO_ROOT, SkillConfig
from .policy import make_permission_handler


@dataclass
class SessionRecorder:
    tool_names: list[str] = field(default_factory=list)
    source_urls: list[str] = field(default_factory=list)
    read_paths: list[str] = field(default_factory=list)
    write_paths: list[str] = field(default_factory=list)
    shell_commands: list[str] = field(default_factory=list)
    event_types: list[str] = field(default_factory=list)

    async def on_pre_tool_use(self, input_data: dict[str, Any], invocation: dict[str, str]) -> dict[str, Any]:
        tool_name = input_data.get("toolName")
        if tool_name:
            self.tool_names.append(str(tool_name))
        return {"permissionDecision": "allow"}

    def on_event(self, event: Any) -> None:
        event_type = getattr(event, "type", None)
        if event_type:
            self.event_types.append(str(event_type))


@dataclass(frozen=True)
class CopilotRunResult:
    final_text: str
    tool_names: tuple[str, ...]
    source_urls: tuple[str, ...]


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
    from copilot import CopilotClient
    from copilot.client import SubprocessConfig

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
    client = CopilotClient(
        SubprocessConfig(
            cwd=str(REPO_ROOT),
            env=env,
            github_token=github_token,
            use_logged_in_user=use_logged_in_user,
        )
    )
    try:
        session = await client.create_session(
            on_permission_request=make_permission_handler(
                config=config,
                allow_writes=allow_writes,
                allow_eval_tightening=allow_eval_tightening,
                run_profile=run_profile,
                allow_live_research=allow_live_research,
                recorder=recorder,
            ),
            model=effective_model,
            provider=provider,
            working_directory=str(REPO_ROOT),
            system_message={"mode": "append", "content": system_message},
            hooks={"on_pre_tool_use": recorder.on_pre_tool_use},
            on_event=recorder.on_event,
        )
        final_event = await session.send_and_wait(
            prompt,
            attachments=attachments,
            timeout=timeout,
        )
        final_text = _extract_final_text(final_event)
        if not final_text:
            messages = await session.get_messages()
            for event in reversed(messages):
                if getattr(event, "type", None) == "assistant.message":
                    final_text = _extract_final_text(event)
                    if final_text:
                        break
        return CopilotRunResult(
            final_text=final_text.strip(),
            tool_names=tuple(recorder.tool_names),
            source_urls=tuple(sorted(set(recorder.source_urls))),
        )
    finally:
        await client.stop()


def _looks_like_auth_failure(exc: Exception) -> bool:
    message = str(exc).lower()
    return any(
        token in message
        for token in ("auth", "unauthorized", "forbidden", "token", "copilot", "401", "403")
    )


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
