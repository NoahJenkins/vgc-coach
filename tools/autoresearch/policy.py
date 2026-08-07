from __future__ import annotations

import re
import shlex
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .config import REPO_ROOT, RunProfile, SkillConfig

if TYPE_CHECKING:
    from copilot.generated.session_events import PermissionRequest
    from copilot.session import PermissionRequestResult

_UNSAFE_SHELL_CHARACTERS = frozenset(";&|<>`$\n\r\0(){}*?[]~#!")
_STATUS_OPTIONS = frozenset(
    {
        "-b",
        "-s",
        "--ahead-behind",
        "--branch",
        "--no-ahead-behind",
        "--porcelain",
        "--short",
        "--show-stash",
        "--untracked-files",
    }
)
_DIFF_OPTIONS = frozenset(
    {
        "--binary",
        "--cached",
        "--check",
        "--name-only",
        "--name-status",
        "--no-color",
        "--no-ext-diff",
        "--no-textconv",
        "--numstat",
        "--relative",
        "--shortstat",
        "--staged",
        "--stat",
        "--summary",
    }
)
_HISTORY_OPTIONS = frozenset(
    {
        "-s",
        "--all",
        "--branches",
        "--decorate",
        "--name-only",
        "--name-status",
        "--no-decorate",
        "--no-patch",
        "--oneline",
        "--remotes",
        "--reverse",
        "--shortstat",
        "--stat",
    }
)
_REV_PARSE_OPTIONS = frozenset(
    {
        "--abbrev-ref",
        "--git-common-dir",
        "--git-dir",
        "--is-bare-repository",
        "--is-inside-git-dir",
        "--is-inside-work-tree",
        "--show-cdup",
        "--show-prefix",
        "--show-superproject-working-tree",
        "--show-toplevel",
        "--verify",
    }
)
_LS_FILES_OPTIONS = frozenset(
    {
        "-c",
        "-d",
        "-f",
        "-i",
        "-m",
        "-o",
        "-s",
        "-t",
        "-u",
        "-v",
        "--cached",
        "--deduplicate",
        "--deleted",
        "--directory",
        "--error-unmatch",
        "--exclude-standard",
        "--full-name",
        "--ignored",
        "--modified",
        "--no-empty-directory",
        "--others",
        "--stage",
        "--unmerged",
    }
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


def is_path_allowed_for_read(path: str | None, attachment_paths: tuple[str, ...]) -> bool:
    candidate = _resolve_existing_path(path)
    if candidate is None:
        return False

    repo_root = REPO_ROOT.resolve()
    if candidate == repo_root or candidate.is_relative_to(repo_root):
        return True

    for raw_attachment in attachment_paths:
        attachment = _resolve_existing_path(raw_attachment)
        if attachment is None:
            continue
        if candidate == attachment:
            return True
        if attachment.is_dir() and candidate.is_relative_to(attachment):
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
    attachment_paths: tuple[str, ...] = (),
):
    def handler(request: "PermissionRequest", invocation: dict[str, str]) -> "PermissionRequestResult":
        from copilot.session import PermissionRequestResult

        kind = getattr(request.kind, "value", str(request.kind))
        if kind == "read":
            paths = _paths_from_request(request)
            if paths and all(is_path_allowed_for_read(path, attachment_paths) for path in paths):
                recorder.read_paths.extend(paths)
                return PermissionRequestResult(kind="approved")
            return PermissionRequestResult(
                kind="denied-by-rules",
                message="Reads are restricted to the repository and explicit attachments.",
            )

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
            recorder.requested_urls.extend(urls)
            return PermissionRequestResult(
                kind="denied-by-rules",
                message=(
                    "Live web access is unavailable because this repository has no "
                    "end-to-end mediated fetch connector."
                    if allow_live_research
                    else "Live web access is disabled for this session."
                ),
            )

        if kind == "shell":
            command = (request.full_command_text or "").strip()
            possible_paths = tuple(getattr(request, "possible_paths", None) or ())
            if (
                command
                and not getattr(request, "has_write_file_redirection", False)
                and all(
                    is_path_allowed_for_read(path, attachment_paths)
                    for path in possible_paths
                )
                and is_safe_read_only_git_command(
                    command,
                    attachment_paths=attachment_paths,
                )
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


def is_safe_read_only_git_command(
    command: str,
    *,
    attachment_paths: tuple[str, ...] = (),
) -> bool:
    if any(character in _UNSAFE_SHELL_CHARACTERS for character in command):
        return False
    try:
        argv = shlex.split(command, posix=True)
    except ValueError:
        return False
    if len(argv) < 2 or argv[0] != "git":
        return False

    subcommand = argv[1]
    arguments = argv[2:]
    if subcommand == "branch":
        return arguments == ["--show-current"]
    if subcommand == "status":
        parsed = _parse_allowed_arguments(
            arguments,
            exact=_STATUS_OPTIONS,
            patterns=(r"--porcelain=v[12]", r"--untracked-files=(?:no|normal|all)"),
        )
        return parsed is not None and _paths_are_allowed(
            (*parsed[0], *parsed[1]),
            attachment_paths,
        )
    if subcommand == "diff":
        parsed = _parse_allowed_arguments(
            arguments,
            exact=_DIFF_OPTIONS,
            patterns=(
                r"-U\d+",
                r"--color=(?:always|auto|never)",
                r"--diff-filter=[ACDMRTUXB]+",
                r"--unified=\d+",
            ),
        )
        if parsed is None:
            return False
        positional_arguments, pathspecs = parsed
        implicit_paths = tuple(
            argument
            for argument in positional_arguments
            if _looks_like_path_operand(argument)
        )
        if any(not _is_repo_path(path) for path in implicit_paths):
            return False
        return _paths_are_allowed(
            (*implicit_paths, *pathspecs),
            attachment_paths,
        )
    if subcommand in {"log", "show"}:
        parsed = _parse_allowed_arguments(
            arguments,
            exact=_HISTORY_OPTIONS,
            patterns=(
                r"-\d+",
                r"--format=.+",
                r"--max-count=\d+",
                r"--pretty=.+",
            ),
        )
        if parsed is None:
            return False
        positional_arguments, pathspecs = parsed
        path_operands = tuple(
            argument
            for argument in positional_arguments
            if _looks_like_path_operand(argument)
        )
        return _paths_are_allowed(
            (*path_operands, *pathspecs),
            attachment_paths,
        )
    if subcommand == "rev-parse":
        parsed = _parse_allowed_arguments(
            arguments,
            exact=_REV_PARSE_OPTIONS,
            patterns=(r"--short(?:=\d+)?",),
        )
        if parsed is None:
            return False
        positional_arguments, pathspecs = parsed
        path_operands = tuple(
            argument
            for argument in positional_arguments
            if _looks_like_path_operand(argument)
        )
        return _paths_are_allowed(
            (*path_operands, *pathspecs),
            attachment_paths,
        )
    if subcommand == "ls-files":
        parsed = _parse_allowed_arguments(arguments, exact=_LS_FILES_OPTIONS)
        return parsed is not None and _paths_are_allowed(
            (*parsed[0], *parsed[1]),
            attachment_paths,
        )
    return False


def _parse_allowed_arguments(
    arguments: list[str],
    *,
    exact: frozenset[str],
    patterns: tuple[str, ...] = (),
) -> tuple[tuple[str, ...], tuple[str, ...]] | None:
    options_ended = False
    positional_arguments: list[str] = []
    pathspecs: list[str] = []
    for argument in arguments:
        if argument == "--" and not options_ended:
            options_ended = True
            continue
        if options_ended:
            pathspecs.append(argument)
            continue
        if not argument.startswith("-"):
            positional_arguments.append(argument)
            continue
        if argument in exact or any(re.fullmatch(pattern, argument) for pattern in patterns):
            continue
        return None
    return tuple(positional_arguments), tuple(pathspecs)


def _paths_are_allowed(paths: tuple[str, ...], attachment_paths: tuple[str, ...]) -> bool:
    return all(is_path_allowed_for_read(path, attachment_paths) for path in paths)


def _looks_like_path_operand(argument: str) -> bool:
    raw_path = Path(argument)
    if raw_path.is_absolute() or "." in raw_path.parts or ".." in raw_path.parts:
        return True
    candidate = REPO_ROOT / raw_path
    return candidate.exists() or candidate.is_symlink()


def _is_repo_path(path: str) -> bool:
    candidate = _resolve_existing_path(path)
    if candidate is None:
        return False
    repo_root = REPO_ROOT.resolve()
    return candidate == repo_root or candidate.is_relative_to(repo_root)


def _resolve_existing_path(path: str | None) -> Path | None:
    if not isinstance(path, str) or not path.strip():
        return None
    try:
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = REPO_ROOT / candidate
        return candidate.resolve(strict=True)
    except (OSError, RuntimeError, ValueError):
        return None


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
