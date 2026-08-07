from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "tools" / "check_format_freshness.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_format_freshness", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_designated_artifacts(
    root: Path,
    *,
    current_end: str,
    current_start: str = "2026-06-17T02:00:00Z",
    current_regulation: str = "m-b",
) -> None:
    registry = root / "docs/skills/shared/references/live-source-registry.yaml"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        "sources:\n"
        f"  - id: regulation-set-{current_regulation}\n"
        "    temporal_status: current\n"
        "    active_window:\n"
        f"      start: '{current_start}'\n"
        f"      end: '{current_end}'\n"
    )

    current_ref = registry.parent / f"champions-reg-{current_regulation}-current-legality.md"
    current_ref.write_text(
        "---\n"
        "temporal_status: current\n"
        f"regulation_id: regulation-{current_regulation}\n"
        "active_window:\n"
        f"  start: '{current_start}'\n"
        f"  end: '{current_end}'\n"
        "---\n"
        "# Current reference\n"
    )

    historical_ref = registry.parent / "champions-reg-m-a-legality.md"
    historical_ref.write_text(
        "---\n"
        "temporal_status: historical\n"
        "regulation_id: regulation-m-a\n"
        "active_window:\n"
        "  start: '2026-04-08T02:00:00Z'\n"
        "  end: '2026-06-17T01:59:00Z'\n"
        "---\n"
        "# Historical reference\n"
    )

    snapshots = root / "data/snapshots"
    snapshots.mkdir(parents=True)
    (snapshots / "current.json").write_text(
        json.dumps(
            {
                "snapshot_id": "current",
                "temporal_status": "current",
                "format": {
                    "regulation_id": f"regulation-{current_regulation}",
                    "active_window": {
                        "start": current_start,
                        "end": current_end,
                    },
                },
            }
        )
    )
    (snapshots / "historical.json").write_text(
        json.dumps(
            {
                "snapshot_id": "historical-m-a",
                "temporal_status": "historical",
                "format": {
                    "regulation_id": "regulation-m-a",
                    "active_window": {
                        "start": "2026-04-08T02:00:00Z",
                        "end": "2026-06-17T01:59:00Z",
                    },
                },
            }
        )
    )


class FormatFreshnessTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_current_designations_pass_inside_window_and_at_exact_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_designated_artifacts(root, current_end="2026-09-09T01:59:00Z")

            inside = self.module.find_expired_current_artifacts(
                root, now=datetime(2026, 8, 6, 12, tzinfo=timezone.utc)
            )
            boundary = self.module.find_expired_current_artifacts(
                root, now=datetime(2026, 9, 9, 1, 59, tzinfo=timezone.utc)
            )

        self.assertEqual(inside, ())
        self.assertEqual(boundary, ())

    def test_current_designations_fail_after_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_designated_artifacts(root, current_end="2026-09-09T01:59:00Z")

            expired = self.module.find_expired_current_artifacts(
                root, now=datetime(2026, 9, 9, 1, 59, 1, tzinfo=timezone.utc)
            )

        self.assertEqual(len(expired), 3)
        self.assertTrue(all("2026-09-09T01:59:00Z" in item for item in expired))

    def test_stale_current_m_a_fails_while_historical_m_a_is_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_designated_artifacts(
                root,
                current_regulation="m-a",
                current_start="2026-04-08T02:00:00Z",
                current_end="2026-06-17T01:59:00Z",
            )

            expired = self.module.find_expired_current_artifacts(
                root, now=datetime(2026, 8, 6, 12, tzinfo=timezone.utc)
            )

        self.assertEqual(len(expired), 3)
        self.assertFalse(any("historical" in item for item in expired))

    def test_repository_current_designations_are_fresh_on_verified_date(self):
        expired = self.module.find_expired_current_artifacts(
            REPO_ROOT, now=datetime(2026, 8, 6, 12, tzinfo=timezone.utc)
        )

        self.assertEqual(expired, ())
