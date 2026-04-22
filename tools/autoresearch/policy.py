from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from .config import REPO_ROOT, RunProfile, SkillConfig

if TYPE_CHECKING:
    from copilot.generated.session_events import PermissionRequest
    from copilot.session import PermissionRequestResult

SAFE_GIT_PREFIXES = (
    "git status",
    "git diff",
    "git show",
    "git log",
    "git rev-parse",
    "git branch --show-current",
    "git ls-files",
)


def get_allowed_write_roots(
    config: SkillConfig,
    *,
    allow_eval_tightening: bool,
    run_profile: RunProfile,
) -> tuple[Path, ...]:
    roots = [config.skill_file]
    if run_profile != "daily_sentinel":
        roots.append(config.docs_dir)
    if allow_eval_tightening:
        roots.extend((config.fixture_dir, config.rubric_file))
    return tuple(roots)


def is_path_allowed_for_write(
    path: str | None,
    config: SkillConfig,
    allow_eval_tightening: bool,
    *,
    run_profile: RunProfile = "manual",
) -> bool:
    if not path:
        return False
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = (REPO_ROOT / candidate).resolve()
    else:
        candidate = candidate.resolve()

    allowed_roots = get_allowed_write_roots(
        config,
        allow_eval_tightening=allow_eval_tightening,
        run_profile=run_profile,
    )

    for root in allowed_roots:
        root = root.resolve()
        if candidate == root:
            return True
        if root.is_dir() and candidate.is_relative_to(root):
            return True
    return False


def make_permission_handler(
    *,
    config: SkillConfig,
    allow_writes: bool,
    allow_eval_tightening: bool,
    run_profile: RunProfile,
    allow_live_research: bool,
    recorder: Any,
):
    def handler(request: "PermissionRequest", invocation: dict[str, str]) -> "PermissionRequestResult":
        from copilot.session import PermissionRequestResult

        kind = getattr(request.kind, "value", str(request.kind))
        if kind == "read":
            recorder.read_paths.extend(_paths_from_request(request))
            return PermissionRequestResult(kind="approved")

        if kind == "write":
            paths = _paths_from_request(request)
            if not allow_writes:
                return PermissionRequestResult(
                    kind="denied-by-rules",
                    message="This session is read-only.",
                )
            if paths and all(
                is_path_allowed_for_write(
                    path,
                    config,
                    allow_eval_tightening,
                    run_profile=run_profile,
                )
                for path in paths
            ):
                recorder.write_paths.extend(paths)
                return PermissionRequestResult(kind="approved")
            return PermissionRequestResult(
                kind="denied-by-rules",
                message="Writes are restricted to the skill write scope.",
            )

        if kind == "url":
            urls = _urls_from_request(request)
            if allow_live_research and all(url.startswith("https://") for url in urls):
                recorder.source_urls.extend(urls)
                return PermissionRequestResult(kind="approved")
            return PermissionRequestResult(
                kind="denied-by-rules",
                message="Live web access is disabled for this session.",
            )

        if kind == "shell":
            command = (request.full_command_text or "").strip()
            if (
                command
                and not request.has_write_file_redirection
                and any(command.startswith(prefix) for prefix in SAFE_GIT_PREFIXES)
            ):
                recorder.shell_commands.append(command)
                return PermissionRequestResult(kind="approved")
            return PermissionRequestResult(
                kind="denied-by-rules",
                message="Shell access is limited to read-only git inspection.",
            )

        return PermissionRequestResult(
            kind="denied-by-rules",
            message=f"Permission kind '{kind}' is not allowed for autoresearch runs.",
        )

    return handler


def _paths_from_request(request: Any) -> list[str]:
    paths = []
    if getattr(request, "possible_paths", None):
        paths.extend(request.possible_paths)
    if getattr(request, "path", None):
        paths.append(request.path)
    if getattr(request, "file_name", None):
        paths.append(request.file_name)
    return [path for path in paths if path]


def _urls_from_request(request: Any) -> list[str]:
    urls = []
    if getattr(request, "url", None):
        urls.append(request.url)
    for possible_url in getattr(request, "possible_urls", None) or []:
        url = getattr(possible_url, "url", None)
        if url:
            urls.append(url)
    return urls
