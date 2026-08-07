from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "tools" / "generate_site_trust_data.py"


def load_module():
    spec = importlib.util.spec_from_file_location("generate_site_trust_data", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_repo_facts(root: Path) -> None:
    (root / "VERSION").write_text("0.2.0\n")
    eval_root = root / "data/fixtures/evals"
    for skill, cases in (("meta", 2), ("team", 1)):
        skill_root = eval_root / skill
        skill_root.mkdir(parents=True, exist_ok=True)
        for index in range(cases):
            (skill_root / f"case-{index + 1:02}.md").write_text("# Case\n")
    rubric_root = root / "data/rubrics"
    rubric_root.mkdir(parents=True)
    (rubric_root / "meta-rubric.md").write_text("# Rubric\n")
    (rubric_root / "human-review.md").write_text("# Human review\n")

    registry = root / "docs/skills/shared/references/live-source-registry.yaml"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        "minimum_stack:\n"
        "  official: 1\n"
        "  tournament_meta: 1\n"
        "sources:\n"
        "  - id: regulation-test\n"
        "    display_name: Regulation Test\n"
        "    role: official_regulation\n"
        "    canonical_url: https://example.com/rules\n"
        "    required_for_minimum_stack: true\n"
        "    temporal_status: current\n"
        "    active_window:\n"
        "      start: '2026-01-01T00:00:00Z'\n"
        "      end: '2026-12-31T23:59:59Z'\n"
        "  - id: tournament-test\n"
        "    display_name: Tournament Test\n"
        "    role: tournament_meta\n"
        "    canonical_url: https://example.com/meta\n"
        "    required_for_minimum_stack: true\n"
    )

    snapshot_root = root / "data/snapshots"
    snapshot_root.mkdir(parents=True)
    (snapshot_root / "reg-test.json").write_text(
        json.dumps(
            {
                "snapshot_id": "reg-test",
                "temporal_status": "current",
                "generated_at": "2026-08-06T12:00:00Z",
                "verified_on": "2026-08-06",
                "format": {
                    "regulation_id": "regulation-test",
                    "active_window": {
                        "start": "2026-01-01T00:00:00Z",
                        "end": "2026-12-31T23:59:59Z",
                    },
                },
                "sources": [
                    {
                        "source_id": "regulation-test",
                        "label": "Regulation Test",
                        "url": "https://example.com/rules",
                    }
                ],
            }
        )
    )


class GenerateSiteTrustDataTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_collects_only_fixed_eval_cases_and_scoring_rubrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_repo_facts(root)

            facts = self.module.collect_trust_facts(root)

        self.assertEqual(facts["version"], "0.2.0")
        self.assertEqual(facts["evaluation"]["fixture_count"], 3)
        self.assertEqual(facts["evaluation"]["rubric_count"], 1)
        self.assertEqual(facts["evaluation"]["skill_count"], 2)
        self.assertEqual(facts["regulation"]["id"], "regulation-test")
        self.assertEqual(facts["regulation"]["verified_on"], "2026-08-06")
        self.assertEqual(facts["regulation"]["freshness_state"], "current_snapshot")
        self.assertEqual(len(facts["source_stack"]["required_sources"]), 2)
        self.assertEqual(facts["source_stack"]["status"], "configured")
        self.assertEqual(
            facts["calculation_boundary"]["exact"],
            ["damage", "KO", "survival"],
        )
        self.assertEqual(
            facts["calculation_boundary"]["assumption_framed"], ["speed"]
        )

    def test_requires_one_unambiguous_current_regulation_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_repo_facts(root)
            snapshot = root / "data/snapshots/second.json"
            snapshot.write_text(
                json.dumps(
                    {
                        "snapshot_id": "second",
                        "temporal_status": "current",
                        "verified_on": "2026-08-06",
                        "format": {
                            "regulation_id": "regulation-second",
                            "active_window": {
                                "start": "2026-01-01T00:00:00Z",
                                "end": "2026-12-31T23:59:59Z",
                            },
                        },
                        "sources": [{"url": "https://example.com/second"}],
                    }
                )
            )

            with self.assertRaisesRegex(ValueError, "exactly one current"):
                self.module.collect_trust_facts(root)

    def test_check_detects_committed_artifact_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_repo_facts(root)
            output = root / "site/src/generated/trustData.ts"
            output.parent.mkdir(parents=True)

            self.assertEqual(self.module.write_generated_artifact(root, output), 0)
            self.assertEqual(self.module.check_generated_artifact(root, output), 0)

            output.write_text(output.read_text().replace("0.2.0", "stale"))

            self.assertEqual(self.module.check_generated_artifact(root, output), 1)


if __name__ == "__main__":
    unittest.main()
