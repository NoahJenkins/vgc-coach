import importlib.util
import pathlib
import sys
import unittest
import copy


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "tools" / "render_source_registry_docs.py"
REGISTRY_PATH = REPO_ROOT / "docs" / "skills" / "shared" / "references" / "live-source-registry.yaml"
SHARED_MAP_PATH = REPO_ROOT / "docs" / "skills" / "shared" / "references" / "live-source-map.md"
LEGACY_MAP_PATH = REPO_ROOT / "docs" / "skills" / "vgc-meta-research" / "references" / "current-source-map.md"


def load_module():
    spec = importlib.util.spec_from_file_location("render_source_registry_docs", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SourceRegistryTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_registry_contains_expected_sources_and_minimum_stack(self):
        registry = self.module.load_registry(REGISTRY_PATH)

        self.assertEqual(registry["minimum_stack"]["official"], 1)
        self.assertEqual(registry["minimum_stack"]["tournament_meta"], 1)
        self.assertEqual(registry["minimum_stack"]["broader_meta"], 1)

        by_id = {entry["id"]: entry for entry in registry["sources"]}
        self.assertEqual(
            tuple(by_id),
            (
                "regulation-set-m-b",
                "play-pokemon-transition-announcement",
                "championsmeta",
                "champions-lab",
                "pikalytics-champions",
                "victory-road",
            ),
        )
        self.assertFalse(by_id["pikalytics-champions"]["required_for_minimum_stack"])
        self.assertIn("set_tendencies", by_id["pikalytics-champions"]["allowed_claim_types"])
        regulation = by_id["regulation-set-m-b"]
        self.assertEqual(regulation["regulation_id"], "regulation-m-b")
        self.assertEqual(regulation["canonical_url"], "https://news.pokemon-home.com/en/page/776.html")
        self.assertEqual(regulation["temporal_status"], "current")
        self.assertEqual(regulation["active_window"]["start"], "2026-06-17T02:00:00Z")
        self.assertEqual(regulation["active_window"]["end"], "2026-09-09T01:59:00Z")
        self.assertIn("legality", regulation["allowed_claim_types"])

    def test_minimum_stack_sources_require_canonical_urls(self):
        registry = self.module.load_registry(REGISTRY_PATH)

        for source in registry["sources"]:
            if source["required_for_minimum_stack"]:
                self.assertRegex(source["canonical_url"], r"^https://")

    def test_current_meta_sources_require_freshness_rules(self):
        registry = self.module.load_registry(REGISTRY_PATH)

        by_id = {entry["id"]: entry for entry in registry["sources"]}
        self.assertEqual(by_id["championsmeta"]["freshness"]["max_age_days"], 7)
        self.assertEqual(by_id["champions-lab"]["freshness"]["max_age_days"], 7)
        self.assertIn("fetched_at", by_id["championsmeta"]["required_evidence_fields"])
        self.assertIn("source_url", by_id["champions-lab"]["required_evidence_fields"])

    def test_registry_rejects_missing_required_evidence_fields(self):
        payload = copy.deepcopy(self.module.load_registry(REGISTRY_PATH))
        del payload["sources"][0]["required_evidence_fields"]

        with self.assertRaisesRegex(ValueError, "required_evidence_fields"):
            self.module.validate_registry(payload)

    def test_official_regulation_requires_regulation_id(self):
        payload = copy.deepcopy(self.module.load_registry(REGISTRY_PATH))
        del payload["sources"][0]["regulation_id"]

        with self.assertRaisesRegex(ValueError, "regulation_id"):
            self.module.validate_registry(payload)

    def test_registry_rejects_missing_minimum_stack_url(self):
        payload = copy.deepcopy(self.module.load_registry(REGISTRY_PATH))
        payload["sources"][0]["canonical_url"] = ""

        with self.assertRaisesRegex(ValueError, "canonical_url"):
            self.module.validate_registry(payload)

    def test_registry_rejects_current_meta_source_without_freshness(self):
        payload = copy.deepcopy(self.module.load_registry(REGISTRY_PATH))
        del payload["sources"][2]["freshness"]

        with self.assertRaisesRegex(ValueError, "freshness"):
            self.module.validate_registry(payload)

    def test_rendered_shared_map_matches_generated_output(self):
        registry = self.module.load_registry(REGISTRY_PATH)
        rendered = self.module.render_markdown(registry)
        committed = SHARED_MAP_PATH.read_text()

        self.assertEqual(committed, rendered)
        self.assertIn("# Shared Live Source Map", committed)
        self.assertIn("## Recommended Minimum Live Stack", committed)
        self.assertIn("Pikalytics Champions", committed)
        self.assertIn("Role: `supporting_sets`", committed)
        self.assertIn("Canonical URL:", committed)
        self.assertIn("Freshness:", committed)
        self.assertIn("Required evidence fields:", committed)
        self.assertIn("- legality or mechanics claims", committed)
        self.assertIn("Regulation Set M-B", committed)
        self.assertIn("2026-09-09T01:59:00Z", committed)

    def test_legacy_meta_research_map_is_wrapper_to_shared_doc(self):
        content = LEGACY_MAP_PATH.read_text()

        self.assertIn("Compatibility wrapper", content)
        self.assertIn("../../shared/references/live-source-map.md", content)


if __name__ == "__main__":
    unittest.main()
