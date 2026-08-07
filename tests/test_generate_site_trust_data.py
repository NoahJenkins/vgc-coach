from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml


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

    def source(
        source_id: str,
        role: str,
        priority: int,
        *,
        url: str,
    ) -> dict:
        item = {
            "id": source_id,
            "display_name": source_id.replace("-", " ").title(),
            "role": role,
            "source_kind": "official" if role == "official_regulation" else "community",
            "canonical_url": url,
            "priority": priority,
            "allowed_claim_types": [
                "legality" if role == "official_regulation" else "current_snapshot"
            ],
            "required_for_minimum_stack": True,
            "freshness": {
                "max_age_days": 7,
                "policy": "Re-check live before current claims.",
            },
            "required_evidence_fields": ["source_url", "fetched_at"],
            "use_for": ["test claims"],
            "do_not_use_for": ["unsupported claims"],
            "fallback_if_unavailable": ["label the evidence gap"],
        }
        if role == "official_regulation":
            item.update(
                {
                    "regulation_id": "regulation-test",
                    "temporal_status": "current",
                    "active_window": {
                        "start": "2026-01-01T00:00:00Z",
                        "end": "2026-12-31T23:59:59Z",
                    },
                }
            )
        return item

    registry.write_text(
        yaml.safe_dump(
            {
                "version": "1",
                "summary": "Test source registry.",
                "usage": "Use test sources for generator validation.",
                "minimum_stack": {
                    "official": 1,
                    "tournament_meta": 1,
                    "broader_meta": 1,
                },
                "sources": [
                    source(
                        "regulation-test",
                        "official_regulation",
                        1,
                        url="https://example.com/rules",
                    ),
                    source(
                        "tournament-test",
                        "tournament_meta",
                        2,
                        url="https://example.com/tournament",
                    ),
                    source(
                        "broader-test",
                        "broader_meta",
                        3,
                        url="https://example.com/meta",
                    ),
                ],
            },
            sort_keys=False,
        )
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
                        "fetched_at": "2026-08-06T12:34:56Z",
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

            facts = self.module.collect_trust_facts(
                root, now=datetime(2026, 8, 7, 12, 34, 56, tzinfo=timezone.utc)
            )

        self.assertEqual(facts["version"], "0.2.0")
        self.assertEqual(facts["evaluation"]["fixture_count"], 3)
        self.assertEqual(facts["evaluation"]["rubric_count"], 1)
        self.assertEqual(facts["evaluation"]["skill_count"], 2)
        self.assertEqual(facts["regulation"]["id"], "regulation-test")
        self.assertEqual(facts["regulation"]["verified_on"], "2026-08-06")
        self.assertEqual(
            facts["regulation"]["verified_at"], "2026-08-06T12:34:56Z"
        )
        self.assertEqual(
            facts["regulation"]["verified_label"],
            "August 6, 2026 at 12:34:56 UTC",
        )
        self.assertEqual(facts["regulation"]["freshness_state"], "fresh")
        self.assertEqual(facts["regulation"]["freshness_max_age_days"], 7)
        self.assertEqual(
            facts["regulation"]["fresh_until"], "2026-08-13T12:34:56Z"
        )
        self.assertEqual(
            facts["regulation"]["fresh_label"], "Source snapshot fresh"
        )
        self.assertEqual(len(facts["source_stack"]["required_sources"]), 3)
        self.assertEqual(facts["source_stack"]["status"], "configured")
        self.assertEqual(
            facts["calculation_boundary"]["exact"],
            ["damage", "KO", "survival"],
        )
        self.assertEqual(
            facts["calculation_boundary"]["assumption_framed"], ["speed"]
        )

    def test_freshness_state_is_fresh_through_exact_max_age_boundary(self):
        verified_at = datetime(2026, 8, 6, 12, 34, 56, tzinfo=timezone.utc)
        boundary = verified_at + timedelta(days=7)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_repo_facts(root)
            facts = self.module.collect_trust_facts(root, now=boundary)

        self.assertEqual(facts["regulation"]["freshness_state"], "fresh")

    def test_freshness_state_is_stale_after_max_age_boundary(self):
        verified_at = datetime(2026, 8, 6, 12, 34, 56, tzinfo=timezone.utc)
        after_boundary = verified_at + timedelta(days=7, microseconds=1)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_repo_facts(root)
            facts = self.module.collect_trust_facts(root, now=after_boundary)

        self.assertEqual(facts["regulation"]["freshness_state"], "stale")
        self.assertEqual(
            facts["regulation"]["stale_label"], "Source snapshot stale"
        )
        self.assertIn("live recheck", facts["regulation"]["freshness_note"])

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

    def test_rejects_wrong_required_source_distribution_by_role(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_repo_facts(root)
            registry_path = (
                root / "docs/skills/shared/references/live-source-registry.yaml"
            )
            registry = yaml.safe_load(registry_path.read_text())
            registry["sources"][1]["role"] = "broader_meta"
            registry_path.write_text(yaml.safe_dump(registry, sort_keys=False))

            with self.assertRaisesRegex(ValueError, "minimum_stack.tournament_meta"):
                self.module.collect_trust_facts(root)

    def test_rejects_snapshot_and_current_registry_mismatches(self):
        mutations = {
            "regulation id": lambda snapshot: snapshot["format"].__setitem__(
                "regulation_id", "regulation-wrong"
            ),
            "official URL": lambda snapshot: snapshot["sources"][0].__setitem__(
                "url", "https://example.com/wrong"
            ),
            "active window": lambda snapshot: snapshot["format"][
                "active_window"
            ].__setitem__("end", "2026-11-30T23:59:59Z"),
        }

        for label, mutate in mutations.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                write_repo_facts(root)
                snapshot_path = root / "data/snapshots/reg-test.json"
                snapshot = json.loads(snapshot_path.read_text())
                mutate(snapshot)
                snapshot_path.write_text(json.dumps(snapshot))

                with self.assertRaisesRegex(ValueError, "does not match"):
                    self.module.collect_trust_facts(root)

    def test_uses_snapshot_generated_at_when_source_fetch_time_is_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_repo_facts(root)
            snapshot_path = root / "data/snapshots/reg-test.json"
            snapshot = json.loads(snapshot_path.read_text())
            del snapshot["sources"][0]["fetched_at"]
            snapshot_path.write_text(json.dumps(snapshot))

            facts = self.module.collect_trust_facts(root)

        self.assertEqual(
            facts["regulation"]["verified_at"], "2026-08-06T12:00:00Z"
        )

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

    def test_check_rejects_artifact_after_freshness_boundary(self):
        verified_at = datetime(2026, 8, 6, 12, 34, 56, tzinfo=timezone.utc)
        fresh_check = verified_at + timedelta(days=7)
        stale_check = fresh_check + timedelta(microseconds=1)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_repo_facts(root)
            output = root / "site/src/generated/trustData.ts"
            output.parent.mkdir(parents=True)

            self.assertEqual(
                self.module.write_generated_artifact(root, output, now=fresh_check),
                0,
            )
            self.assertEqual(
                self.module.check_generated_artifact(root, output, now=stale_check),
                1,
            )


if __name__ == "__main__":
    unittest.main()
