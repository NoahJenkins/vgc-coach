#!/usr/bin/env python3
"""Generate the public site's trust/freshness facts from repository sources."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "site/src/generated/trustData.ts"
REGISTRY_PATH = Path("docs/skills/shared/references/live-source-registry.yaml")
SNAPSHOTS_ROOT = Path("data/snapshots")


def _read_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text())
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected a YAML mapping in {path}")
    return loaded


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


def _utc_label(value: str) -> str:
    instant = datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
        timezone.utc
    )
    month = instant.strftime("%B")
    return f"{month} {instant.day}, {instant.year} at {instant:%H:%M} UTC"


def _date_label(value: str) -> str:
    day = datetime.fromisoformat(value).date()
    return f"{day:%B} {day.day}, {day.year}"


def collect_trust_facts(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    registry = _read_yaml(repo_root / REGISTRY_PATH)
    snapshot = _current_snapshot(repo_root)
    snapshot_format = snapshot.get("format")
    if not isinstance(snapshot_format, dict):
        raise ValueError("Current regulation snapshot is missing its format mapping.")
    active_window = snapshot_format.get("active_window")
    if not isinstance(active_window, dict):
        raise ValueError("Current regulation snapshot is missing its active window.")

    sources = registry.get("sources")
    if not isinstance(sources, list):
        raise ValueError("Live-source registry is missing its sources list.")
    required_sources = [
        {
            "id": source["id"],
            "name": source["display_name"],
            "role": source["role"],
            "url": source["canonical_url"],
        }
        for source in sources
        if isinstance(source, dict) and source.get("required_for_minimum_stack") is True
    ]
    minimum_stack = registry.get("minimum_stack")
    if not isinstance(minimum_stack, dict) or len(required_sources) != sum(
        int(count) for count in minimum_stack.values()
    ):
        raise ValueError(
            "Live-source registry minimum_stack does not match its required sources."
        )

    snapshot_sources = snapshot.get("sources")
    if not isinstance(snapshot_sources, list) or len(snapshot_sources) != 1:
        raise ValueError("Current regulation snapshot must name one official source.")
    official_source = snapshot_sources[0]
    if not isinstance(official_source, dict):
        raise ValueError("Current regulation source must be a mapping.")

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
            "verified_label": _date_label(snapshot["verified_on"]),
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
