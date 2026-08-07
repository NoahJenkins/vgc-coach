#!/usr/bin/env python3
"""Generate the public site's trust/freshness facts from repository sources."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.render_source_registry_docs import (  # noqa: E402
    MINIMUM_STACK_ROLE_MAP,
    load_registry,
)


DEFAULT_OUTPUT = REPO_ROOT / "site/src/generated/trustData.ts"
REGISTRY_PATH = Path("docs/skills/shared/references/live-source-registry.yaml")
SNAPSHOTS_ROOT = Path("data/snapshots")


def _current_snapshot(repo_root: Path) -> dict[str, Any]:
    current: list[dict[str, Any]] = []
    for path in sorted((repo_root / SNAPSHOTS_ROOT).glob("*.json")):
        loaded = json.loads(path.read_text())
        if isinstance(loaded, dict) and loaded.get("temporal_status") == "current":
            loaded["_path"] = path.relative_to(repo_root).as_posix()
            current.append(loaded)
    if len(current) != 1:
        raise ValueError(
            "Site trust data requires exactly one current regulation snapshot; "
            f"found {len(current)}."
        )
    return current[0]


def _parse_rfc3339_utc(value: Any, *, label: str) -> datetime:
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", value
    ):
        raise ValueError(f"{label} must be an RFC 3339 UTC timestamp ending in Z.")
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00").astimezone(timezone.utc)
    except ValueError as exc:
        raise ValueError(f"{label} must be a valid RFC 3339 UTC timestamp.") from exc


def _utc_label(value: str, *, include_seconds: bool = False) -> str:
    instant = datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
        timezone.utc
    )
    month = instant.strftime("%B")
    time_format = "%H:%M:%S" if include_seconds else "%H:%M"
    return (
        f"{month} {instant.day}, {instant.year} at "
        f"{instant.strftime(time_format)} UTC"
    )


def collect_trust_facts(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    registry = load_registry(repo_root / REGISTRY_PATH)
    snapshot = _current_snapshot(repo_root)
    snapshot_format = snapshot.get("format")
    if not isinstance(snapshot_format, dict):
        raise ValueError("Current regulation snapshot is missing its format mapping.")
    active_window = snapshot_format.get("active_window")
    if not isinstance(active_window, dict):
        raise ValueError("Current regulation snapshot is missing its active window.")

    sources = registry["sources"]
    required_sources: list[dict[str, str]] = []
    required_role_counts: dict[str, int] = {}
    for stack_key, role in MINIMUM_STACK_ROLE_MAP.items():
        role_sources = [
            source
            for source in sources
            if source["role"] == role and source["required_for_minimum_stack"]
        ]
        required_count = registry["minimum_stack"][stack_key]
        if len(role_sources) < required_count:
            raise ValueError(
                f"minimum_stack.{stack_key} requires {required_count} sources, "
                f"but only {len(role_sources)} required {role} sources are configured"
            )
        required_role_counts[role] = len(role_sources)
        required_sources.extend(
            {
                "id": source["id"],
                "name": source["display_name"],
                "role": source["role"],
                "url": source["canonical_url"],
            }
            for source in role_sources
        )

    current_official_sources = [
        source
        for source in sources
        if source["role"] == "official_regulation"
        and source["temporal_status"] == "current"
    ]
    if len(current_official_sources) != 1:
        raise ValueError(
            "Site trust data requires exactly one current official registry source; "
            f"found {len(current_official_sources)}."
        )
    registry_official = current_official_sources[0]

    snapshot_sources = snapshot.get("sources")
    if not isinstance(snapshot_sources, list) or len(snapshot_sources) != 1:
        raise ValueError("Current regulation snapshot must name one official source.")
    official_source = snapshot_sources[0]
    if not isinstance(official_source, dict):
        raise ValueError("Current regulation source must be a mapping.")

    consistency_checks = (
        (
            "snapshot source id",
            official_source.get("source_id"),
            registry_official["id"],
        ),
        (
            "snapshot regulation id",
            snapshot_format.get("regulation_id"),
            registry_official["regulation_id"],
        ),
        (
            "snapshot official URL",
            official_source.get("url"),
            registry_official["canonical_url"],
        ),
        (
            "snapshot active window",
            active_window,
            registry_official["active_window"],
        ),
    )
    for label, snapshot_value, registry_value in consistency_checks:
        if snapshot_value != registry_value:
            raise ValueError(
                f"{label} does not match the current official registry entry."
            )

    verified_at = official_source.get("fetched_at") or snapshot.get("generated_at")
    _parse_rfc3339_utc(verified_at, label="snapshot verification timestamp")

    eval_paths = sorted((repo_root / "data/fixtures/evals").glob("*/case-*.md"))
    rubric_paths = sorted((repo_root / "data/rubrics").glob("*-rubric.md"))

    return {
        "version": (repo_root / "VERSION").read_text().strip(),
        "generated_from": [
            REGISTRY_PATH.as_posix(),
            snapshot["_path"],
            "data/fixtures/evals/*/case-*.md",
            "data/rubrics/*-rubric.md",
            "VERSION",
        ],
        "regulation": {
            "id": snapshot_format["regulation_id"],
            "name": official_source.get("label", snapshot_format["regulation_id"]),
            "source_url": official_source["url"],
            "starts_at": active_window["start"],
            "starts_label": _utc_label(active_window["start"]),
            "ends_at": active_window["end"],
            "ends_label": _utc_label(active_window["end"]),
            "verified_on": snapshot["verified_on"],
            "verified_at": verified_at,
            "verified_label": _utc_label(verified_at, include_seconds=True),
            "freshness_state": "current_snapshot",
            "freshness_note": (
                "Current repository snapshot; live recheck required before "
                "present-tense coaching."
            ),
        },
        "evaluation": {
            "fixture_count": len(eval_paths),
            "rubric_count": len(rubric_paths),
            "skill_count": len({path.parent.name for path in eval_paths}),
            "scope_note": (
                "These are committed structural test assets, not a claim that "
                "every case was freshly run against a live model."
            ),
        },
        "source_stack": {
            "status": "configured",
            "required_role_counts": required_role_counts,
            "required_sources": required_sources,
            "scope_note": (
                "The repository defines the minimum source roles. Live pages "
                "are checked again when current advice is requested."
            ),
        },
        "calculation_boundary": {
            "exact": ["damage", "KO", "survival"],
            "assumption_framed": ["speed"],
            "scope_note": (
                "Exact damage-family results require complete inputs and the "
                "local browser helper."
            ),
        },
    }


def render_generated_artifact(repo_root: Path = REPO_ROOT) -> str:
    facts = collect_trust_facts(repo_root)
    payload = json.dumps(facts, indent=2, ensure_ascii=False)
    return (
        "// Generated by tools/generate_site_trust_data.py. Do not edit.\n"
        f"export const trustData = {payload} as const;\n"
    )


def write_generated_artifact(
    repo_root: Path = REPO_ROOT, output: Path = DEFAULT_OUTPUT
) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_generated_artifact(repo_root))
    print(f"Wrote {output.relative_to(repo_root)}")
    return 0


def check_generated_artifact(
    repo_root: Path = REPO_ROOT, output: Path = DEFAULT_OUTPUT
) -> int:
    expected = render_generated_artifact(repo_root)
    if not output.is_file() or output.read_text() != expected:
        print(
            "Generated site trust data is stale. Run: "
            "python3 tools/generate_site_trust_data.py build",
            file=sys.stderr,
        )
        return 1
    print("Generated site trust data matches repository facts.")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("build", "check"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.mode == "build":
        return write_generated_artifact()
    return check_generated_artifact()


if __name__ == "__main__":
    raise SystemExit(main())
