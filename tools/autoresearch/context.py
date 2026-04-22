from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from .config import REPO_ROOT, SkillConfig

_MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)#]+)(?:#[^)]+)?\)")


@dataclass(frozen=True)
class CaseFile:
    name: str
    path: Path
    raw_text: str
    request: str
    checks: tuple[str, ...]
    failure_triggers: tuple[str, ...]


@dataclass(frozen=True)
class SkillContext:
    config: SkillConfig
    skill_text: str
    rubric_text: str
    cases: tuple[CaseFile, ...]
    shared_reference_files: tuple[Path, ...]

    @property
    def writable_roots(self) -> tuple[Path, ...]:
        return (self.config.skill_file, self.config.docs_dir)


@dataclass(frozen=True)
class SnapshotEntry:
    digest: str
    text: str


def load_skill_context(config: SkillConfig) -> SkillContext:
    skill_text = config.skill_file.read_text()
    rubric_text = config.rubric_file.read_text()
    cases = tuple(load_case_file(path) for path in sorted(config.fixture_dir.glob("case-*.md")))
    shared_reference_files = tuple(sorted(_collect_shared_reference_files(config)))
    return SkillContext(
        config=config,
        skill_text=skill_text,
        rubric_text=rubric_text,
        cases=cases,
        shared_reference_files=shared_reference_files,
    )


def load_case_file(path: Path) -> CaseFile:
    raw_text = path.read_text()
    request = _extract_request(raw_text)
    if not request:
        raise ValueError(f"Fixture {path} has an empty Request block.")
    checks = tuple(_extract_bullets_after_label(raw_text, "Checks:"))
    failure_triggers = tuple(_extract_bullets_after_label(raw_text, "Failure triggers:"))
    return CaseFile(
        name=path.stem,
        path=path,
        raw_text=raw_text,
        request=request,
        checks=checks,
        failure_triggers=failure_triggers,
    )


def extract_rubric_fail_triggers(rubric_text: str) -> tuple[str, ...]:
    for label in ("Fail the response if any of these happen:", "Failure triggers:"):
        bullets = tuple(_extract_bullets_after_label(rubric_text, label))
        if bullets:
            return bullets
    return ()


def snapshot_paths(roots: tuple[Path, ...]) -> dict[str, SnapshotEntry]:
    entries: dict[str, SnapshotEntry] = {}
    for path in iter_files(roots):
        relative = path.relative_to(REPO_ROOT).as_posix()
        text = path.read_text()
        entries[relative] = SnapshotEntry(
            digest=hashlib.sha256(text.encode("utf-8")).hexdigest(),
            text=text,
        )
    return entries


def diff_snapshots(
    before: dict[str, SnapshotEntry], after: dict[str, SnapshotEntry]
) -> tuple[str, ...]:
    changed = []
    keys = sorted(set(before) | set(after))
    for key in keys:
        if before.get(key) != after.get(key):
            changed.append(key)
    return tuple(changed)


def restore_snapshot(snapshot: dict[str, SnapshotEntry], roots: tuple[Path, ...]) -> None:
    existing = {path.relative_to(REPO_ROOT).as_posix(): path for path in iter_files(roots)}
    for relative, path in existing.items():
        if relative not in snapshot:
            path.unlink()

    for relative, entry in snapshot.items():
        path = REPO_ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(entry.text)


def iter_files(roots: tuple[Path, ...]) -> tuple[Path, ...]:
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
            continue
        if root.is_dir():
            files.extend(sorted(path for path in root.rglob("*") if path.is_file()))
    return tuple(sorted(set(files)))


def _collect_shared_reference_files(config: SkillConfig) -> set[Path]:
    referenced = set(resolve_markdown_links(config.skill_file))
    docs_dir = config.docs_dir
    for path in list(referenced):
        if path.is_relative_to(docs_dir):
            continue
        if path == config.skill_file:
            continue
    return {path for path in referenced if path.is_file() and not path.is_relative_to(docs_dir)}


def resolve_markdown_links(path: Path) -> tuple[Path, ...]:
    referenced: list[Path] = []
    for raw_link in _MARKDOWN_LINK_RE.findall(path.read_text()):
        if "://" in raw_link:
            continue
        resolved = (path.parent / raw_link).resolve()
        try:
            resolved.relative_to(REPO_ROOT)
        except ValueError:
            continue
        if resolved.exists():
            referenced.append(resolved)
    return tuple(sorted(set(referenced)))


def _extract_request(text: str) -> str:
    lines = text.splitlines()
    collecting = False
    request_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not collecting:
            if line.startswith("Request:"):
                collecting = True
                initial = line.partition(":")[2].strip()
                if initial:
                    request_lines.append(initial)
            continue

        if stripped in ("Checks:", "Failure triggers:"):
            break
        request_lines.append(line)

    while request_lines and not request_lines[0].strip():
        request_lines.pop(0)
    while request_lines and not request_lines[-1].strip():
        request_lines.pop()
    return "\n".join(request_lines).strip()


def _extract_bullets_after_label(text: str, label: str) -> list[str]:
    lines = text.splitlines()
    collecting = False
    bullets: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not collecting:
            if stripped == label:
                collecting = True
            continue

        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
            continue

        if not stripped:
            if bullets:
                continue
            continue

        if bullets:
            break

    return bullets
