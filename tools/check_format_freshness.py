#!/usr/bin/env python3
"""Fail when an artifact designated current is past its official format window."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = Path("docs/skills/shared/references/live-source-registry.yaml")
REFERENCE_ROOT = Path("docs/skills/shared/references")
SNAPSHOT_ROOT = Path("data/snapshots")


def _parse_utc(value: Any, *, label: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{label} must be an ISO-8601 UTC timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(f"{label} must be a valid ISO-8601 UTC timestamp") from exc
    return parsed.astimezone(timezone.utc)


def _front_matter(path: Path) -> dict[str, Any] | None:
    text = path.read_text()
    if not text.startswith("---\n"):
        return None
    _, separator, remainder = text.partition("\n---\n")
    if not separator:
        raise ValueError(f"{path}: unterminated YAML front matter")
    payload = yaml.safe_load(text[4 : len(text) - len(remainder) - len(separator)])
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: YAML front matter must be a mapping")
    return payload


def _designation(
    payload: dict[str, Any],
    *,
    label: str,
    window_path: tuple[str, ...],
) -> tuple[str, datetime] | None:
    status = payload.get("temporal_status")
    if status is None:
        return None
    if status not in {"current", "historical"}:
        raise ValueError(f"{label}: temporal_status must be current or historical")

    window: Any = payload
    for component in window_path:
        if not isinstance(window, dict) or component not in window:
            raise ValueError(f"{label}: designated artifacts require an active_window")
        window = window[component]
    if not isinstance(window, dict):
        raise ValueError(f"{label}: active_window must be a mapping")
    start = _parse_utc(window.get("start"), label=f"{label}.active_window.start")
    end = _parse_utc(window.get("end"), label=f"{label}.active_window.end")
    if start > end:
        raise ValueError(f"{label}: active_window.start must not be after end")
    return status, end


def _iter_designations(repo_root: Path) -> Iterable[tuple[str, str, datetime]]:
    registry_path = repo_root / REGISTRY_PATH
    registry = yaml.safe_load(registry_path.read_text())
    if not isinstance(registry, dict) or not isinstance(registry.get("sources"), list):
        raise ValueError(f"{registry_path}: sources must be a list")
    for index, source in enumerate(registry["sources"]):
        if not isinstance(source, dict):
            raise ValueError(f"{registry_path}: sources[{index}] must be a mapping")
        result = _designation(
            source,
            label=f"{REGISTRY_PATH}:sources[{index}]",
            window_path=("active_window",),
        )
        if result:
            status, end = result
            yield f"{REGISTRY_PATH}:sources[{index}]", status, end

    snapshot_root = repo_root / SNAPSHOT_ROOT
    for path in sorted(snapshot_root.glob("*.json")):
        payload = json.loads(path.read_text())
        if not isinstance(payload, dict):
            raise ValueError(f"{path}: snapshot must be a mapping")
        relative = path.relative_to(repo_root).as_posix()
        result = _designation(
            payload,
            label=relative,
            window_path=("format", "active_window"),
        )
        if result:
            status, end = result
            yield relative, status, end

    reference_root = repo_root / REFERENCE_ROOT
    for path in sorted(reference_root.glob("*.md")):
        payload = _front_matter(path)
        if payload is None:
            continue
        relative = path.relative_to(repo_root).as_posix()
        result = _designation(
            payload,
            label=relative,
            window_path=("active_window",),
        )
        if result:
            status, end = result
            yield relative, status, end


def find_expired_current_artifacts(
    repo_root: Path = REPO_ROOT,
    *,
    now: datetime | None = None,
) -> tuple[str, ...]:
    checked_at = now or datetime.now(timezone.utc)
    if checked_at.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    checked_at = checked_at.astimezone(timezone.utc)

    expired = []
    for label, status, end in _iter_designations(repo_root):
        if status == "current" and checked_at > end:
            expired.append(
                f"{label} is designated current but its active window ended "
                f"{end.isoformat().replace('+00:00', 'Z')}"
            )
    return tuple(expired)


def main() -> int:
    try:
        expired = find_expired_current_artifacts()
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"Format freshness check could not validate artifacts: {exc}")
        return 2
    if not expired:
        return 0
    print("Current-format artifacts are stale:")
    for item in expired:
        print(f"- {item}")
    print("Verify the active regulation live, replace current designations, and retain expired material only as historical.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
