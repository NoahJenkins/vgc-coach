from __future__ import annotations

import ipaddress
import re
import shlex
import socket
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import urlsplit

from .config import REPO_ROOT, RunProfile, SkillConfig

if TYPE_CHECKING:
    from copilot.generated.session_events import PermissionRequest
    from copilot.session import PermissionRequestResult

_UNSAFE_SHELL_CHARACTERS = frozenset(";&|<>`$\n\r\0(){}*?[]~#!")
_METADATA_HOSTS = frozenset(
    {
        "instance-data",
        "metadata",
        "metadata.aws.internal",
        "metadata.google.internal",
    }
)

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
            if allow_live_research and urls and all(is_public_https_url(url) for url in urls):
                recorder.approved_urls.extend(urls)
                return PermissionRequestResult(kind="approved")
            return PermissionRequestResult(
                kind="denied-by-rules",
                message="Live web access requires an approved public HTTPS destination.",
            )

        if kind == "shell":
            command = (request.full_command_text or "").strip()
            if (
                command
                and not getattr(request, "has_write_file_redirection", False)
                and is_safe_read_only_git_command(command)
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


def is_public_https_url(url: str) -> bool:
    if not isinstance(url, str) or not url:
        return False
    try:
        parsed = urlsplit(url)
        hostname = parsed.hostname
        port = parsed.port
    except (TypeError, ValueError):
        return False

    if parsed.scheme.lower() != "https" or not hostname:
        return False
    if parsed.username is not None or parsed.password is not None:
        return False
    if port not in (None, 443):
        return False

    normalized_host = hostname.rstrip(".").lower()
    if (
        normalized_host == "localhost"
        or normalized_host.endswith(".localhost")
        or normalized_host in _METADATA_HOSTS
    ):
        return False

    try:
        literal_address = ipaddress.ip_address(normalized_host)
    except ValueError:
        addresses = _resolve_host_addresses(normalized_host)
        return bool(addresses) and all(_is_public_address(address) for address in addresses)
    return _is_public_address(literal_address)


def is_safe_read_only_git_command(command: str) -> bool:
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
        return _options_are_allowed(
            arguments,
            exact=_STATUS_OPTIONS,
            patterns=(r"--porcelain=v[12]", r"--untracked-files=(?:no|normal|all)"),
        )
    if subcommand == "diff":
        return _options_are_allowed(
            arguments,
            exact=_DIFF_OPTIONS,
            patterns=(
                r"-U\d+",
                r"--color=(?:always|auto|never)",
                r"--diff-filter=[ACDMRTUXB]+",
                r"--unified=\d+",
            ),
        )
    if subcommand in {"log", "show"}:
        return _options_are_allowed(
            arguments,
            exact=_HISTORY_OPTIONS,
            patterns=(
                r"-\d+",
                r"--format=.+",
                r"--max-count=\d+",
                r"--pretty=.+",
            ),
        )
    if subcommand == "rev-parse":
        return _options_are_allowed(
            arguments,
            exact=_REV_PARSE_OPTIONS,
            patterns=(r"--short(?:=\d+)?",),
        )
    if subcommand == "ls-files":
        return _options_are_allowed(arguments, exact=_LS_FILES_OPTIONS)
    return False


def _options_are_allowed(
    arguments: list[str],
    *,
    exact: frozenset[str],
    patterns: tuple[str, ...] = (),
) -> bool:
    options_ended = False
    for argument in arguments:
        if argument == "--" and not options_ended:
            options_ended = True
            continue
        if options_ended or not argument.startswith("-"):
            continue
        if argument in exact or any(re.fullmatch(pattern, argument) for pattern in patterns):
            continue
        return False
    return True


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


def _resolve_host_addresses(hostname: str) -> tuple[ipaddress.IPv4Address | ipaddress.IPv6Address, ...]:
    try:
        address_info = socket.getaddrinfo(
            hostname,
            443,
            type=socket.SOCK_STREAM,
        )
    except (OSError, UnicodeError):
        return ()

    addresses: set[ipaddress.IPv4Address | ipaddress.IPv6Address] = set()
    for entry in address_info:
        try:
            addresses.add(ipaddress.ip_address(entry[4][0].split("%", 1)[0]))
        except (IndexError, TypeError, ValueError):
            return ()
    return tuple(addresses)


def _is_public_address(address: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return bool(
        address.is_global
        and not address.is_link_local
        and not address.is_loopback
        and not address.is_multicast
        and not address.is_private
        and not address.is_reserved
        and not address.is_unspecified
    )


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
