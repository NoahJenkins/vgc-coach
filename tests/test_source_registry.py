import importlib.util
import pathlib
import sys
import unittest


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
                "regulation-set-m-a",
                "play-pokemon-transition-announcement",
                "championsmeta",
                "champions-lab",
                "pikalytics-champions",
                "victory-road",
            ),
        )
        self.assertFalse(by_id["pikalytics-champions"]["required_for_minimum_stack"])
        self.assertIn("set_tendencies", by_id["pikalytics-champions"]["allowed_claim_types"])
        self.assertIn("legality", by_id["regulation-set-m-a"]["allowed_claim_types"])

    def test_rendered_shared_map_matches_generated_output(self):
        registry = self.module.load_registry(REGISTRY_PATH)
        rendered = self.module.render_markdown(registry)
        committed = SHARED_MAP_PATH.read_text()

        self.assertEqual(committed, rendered)
        self.assertIn("# Shared Live Source Map", committed)
        self.assertIn("## Recommended Minimum Live Stack", committed)
        self.assertIn("Pikalytics Champions", committed)
        self.assertIn("Role: `supporting_sets`", committed)
        self.assertIn("- legality or mechanics claims", committed)

    def test_legacy_meta_research_map_is_wrapper_to_shared_doc(self):
        content = LEGACY_MAP_PATH.read_text()

        self.assertIn("Compatibility wrapper", content)
        self.assertIn("../../shared/references/live-source-map.md", content)


if __name__ == "__main__":
    unittest.main()
