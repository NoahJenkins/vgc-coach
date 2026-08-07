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
        "    role: official_regulation\n"
        f"    regulation_id: regulation-{current_regulation}\n"
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

    fixtures = root / "data/fixtures"
    fixtures.mkdir(parents=True)
    (fixtures / "request.example.json").write_text(
        json.dumps(
            {
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


def write_empty_registry(root: Path) -> None:
    registry = root / "docs/skills/shared/references/live-source-registry.yaml"
    registry.parent.mkdir(parents=True)
    registry.write_text("sources: []\n")


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

        self.assertEqual(len(expired), 4)
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

        self.assertEqual(len(expired), 4)
        self.assertFalse(any("historical" in item for item in expired))

    def test_runtime_wrapper_cannot_route_current_coaching_to_historical_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_designated_artifacts(root, current_end="2026-09-09T01:59:00Z")
            wrapper = root / ".opencode/skills/opencode-vgc-team-builder/SKILL.md"
            wrapper.parent.mkdir(parents=True)
            wrapper.write_text(
                "Read `docs/skills/shared/references/champions-reg-m-a-legality.md`.\n"
            )

            issues = self.module.find_expired_current_artifacts(
                root, now=datetime(2026, 8, 6, 12, tzinfo=timezone.utc)
            )

        self.assertEqual(len(issues), 1)
        self.assertIn("historical regulation reference", issues[0])
        self.assertIn("champions-reg-m-b-legality.md", issues[0])

    def test_regulation_bearing_paths_require_temporal_status(self):
        scenarios = {
            "registry": (
                "docs/skills/shared/references/live-source-registry.yaml",
                "sources:\n"
                "  - id: regulation-set-future\n"
                "    role: official_regulation\n"
                "    active_window:\n"
                "      start: '2027-01-01T00:00:00Z'\n"
                "      end: '2027-02-01T00:00:00Z'\n",
            ),
            "snapshot": (
                "data/snapshots/future/nested/future-format.json",
                json.dumps(
                    {
                        "format": {
                            "regulation_id": "regulation-future",
                            "active_window": {
                                "start": "2027-01-01T00:00:00Z",
                                "end": "2027-02-01T00:00:00Z",
                            },
                        }
                    }
                ),
            ),
            "reference": (
                "docs/skills/shared/references/future-format.md",
                "---\n"
                "regulation_id: regulation-future\n"
                "active_window:\n"
                "  start: '2027-01-01T00:00:00Z'\n"
                "  end: '2027-02-01T00:00:00Z'\n"
                "---\n# Future format\n",
            ),
            "ambiguous fixture": (
                "data/fixtures/future/nested/anything.example.json",
                json.dumps(
                    {
                        "format": {
                            "regulation_id": "regulation-future",
                            "active_window": {
                                "start": "2027-01-01T00:00:00Z",
                                "end": "2027-02-01T00:00:00Z",
                            },
                        }
                    }
                ),
            ),
            "ambiguous provenance fixture": (
                "data/fixtures/future/nested/provenance.example.json",
                json.dumps(
                    {
                        "schema_version": "future-state-v1",
                        "format_provenance": {
                            "regulation_id": "regulation-future",
                            "active_window": {
                                "start": "2027-01-01T00:00:00Z",
                                "end": "2027-02-01T00:00:00Z",
                            },
                        },
                    }
                ),
            ),
        }

        for label, (relative, content) in scenarios.items():
            with self.subTest(path=label), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                write_empty_registry(root)
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)

                with self.assertRaisesRegex(ValueError, "temporal_status"):
                    self.module.find_expired_current_artifacts(
                        root, now=datetime(2026, 8, 6, 12, tzinfo=timezone.utc)
                    )

    def test_regulation_bearing_snapshot_and_fixture_require_active_window(self):
        for relative in (
            "data/snapshots/future/nested/future-format.json",
            "data/fixtures/future/nested/anything.example.json",
        ):
            with self.subTest(path=relative), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                write_empty_registry(root)
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    json.dumps(
                        {
                            "temporal_status": "historical",
                            "format": {"regulation_id": "regulation-future"},
                        }
                    )
                )

                with self.assertRaisesRegex(ValueError, "active_window"):
                    self.module.find_expired_current_artifacts(
                        root, now=datetime(2026, 8, 6, 12, tzinfo=timezone.utc)
                    )

    def test_checked_in_request_examples_use_current_m_b_provenance(self):
        for filename in (
            "team-build-request-v1.example.json",
            "battle-review-request-v1.example.json",
        ):
            with self.subTest(filename=filename):
                payload = json.loads((REPO_ROOT / "data/fixtures" / filename).read_text())
                self.assertEqual(payload["temporal_status"], "current")
                self.assertEqual(payload["format"]["regulation_id"], "regulation-m-b")
                self.assertEqual(
                    payload["format"]["active_window"]["end"],
                    "2026-09-09T01:59:00Z",
                )
                self.assertEqual(
                    payload["format_provenance"]["source_url"],
                    "https://news.pokemon-home.com/en/page/776.html",
                )

    def test_checked_in_battle_state_example_is_a_current_designation(self):
        designations = {
            label: (status, end)
            for label, status, end in self.module._iter_designations(REPO_ROOT)
        }

        status, end = designations["data/fixtures/battle-state-v1.example.json"]
        self.assertEqual(status, "current")
        self.assertEqual(end, datetime(2026, 9, 9, 1, 59, tzinfo=timezone.utc))

    def test_battle_state_example_fails_after_its_provenance_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_designated_artifacts(
                root,
                current_start="2026-01-01T00:00:00Z",
                current_end="2026-12-31T23:59:59Z",
            )
            fixture = root / "data/fixtures/battle-state-v1.example.json"
            fixture.parent.mkdir(parents=True, exist_ok=True)
            fixture.write_text(
                json.dumps(
                    {
                        "schema_version": "battle-state-v1",
                        "format_provenance": {
                            "regulation_id": "regulation-expired",
                            "active_window": {
                                "start": "2026-01-01T00:00:00Z",
                                "end": "2026-02-01T00:00:00Z",
                            },
                        },
                    }
                )
            )

            expired = self.module.find_expired_current_artifacts(
                root, now=datetime(2026, 2, 1, 0, 0, 1, tzinfo=timezone.utc)
            )

        self.assertEqual(len(expired), 1)
        self.assertIn("battle-state-v1.example.json", expired[0])
        self.assertIn("2026-02-01T00:00:00Z", expired[0])

    def test_checked_in_meta_snapshot_example_is_explicitly_historical(self):
        payload = json.loads(
            (REPO_ROOT / "data/snapshots/meta-snapshot-v1.example.json").read_text()
        )

        self.assertEqual(payload["temporal_status"], "historical")
        self.assertEqual(payload["format"]["regulation_id"], "regulation-m-a")
        self.assertEqual(
            payload["format"]["active_window"],
            {
                "start": "2026-04-08T02:00:00Z",
                "end": "2026-06-17T01:59:00Z",
            },
        )
        self.assertTrue(any("historical" in note.lower() for note in payload["notes"]))

    def test_repository_current_designations_are_fresh_on_verified_date(self):
        expired = self.module.find_expired_current_artifacts(
            REPO_ROOT, now=datetime(2026, 8, 6, 12, tzinfo=timezone.utc)
        )

        self.assertEqual(expired, ())
