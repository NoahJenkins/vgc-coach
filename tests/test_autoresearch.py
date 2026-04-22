from __future__ import annotations

import datetime as dt
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from autoresearch.config import choose_skill, get_skill_config  # noqa: E402
from autoresearch.context import (  # noqa: E402
    diff_snapshots,
    extract_rubric_fail_triggers,
    load_skill_context,
    restore_snapshot,
    snapshot_paths,
)
from autoresearch.policy import is_path_allowed_for_write  # noqa: E402


class AutoresearchTests(unittest.TestCase):
    def test_priority_rotation_is_deterministic(self):
        first = choose_skill("auto", dt.date(2026, 1, 1))
        sixth = choose_skill("auto", dt.date(2026, 1, 6))
        self.assertEqual(first.name, sixth.name)
        self.assertEqual(first.name, "vgc-meta-research")

    def test_skill_context_loads_cases_and_shared_refs(self):
        ctx = load_skill_context(get_skill_config("vgc-meta-research"))
        self.assertGreaterEqual(len(ctx.cases), 1)
        self.assertEqual(
            ctx.config.docs_dir,
            REPO_ROOT / "docs" / "skills" / "vgc-meta-research",
        )

    def test_rubric_fail_trigger_extraction_supports_both_formats(self):
        text = "\n".join(
            [
                "Failure triggers:",
                "",
                "- one",
                "- two",
            ]
        )
        self.assertEqual(extract_rubric_fail_triggers(text), ("one", "two"))

    def test_snapshot_diff_and_restore_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "docs" / "skills" / "example"
            target.mkdir(parents=True)
            file_path = target / "note.md"
            file_path.write_text("before")

            import autoresearch.context as context_module

            original_root = context_module.REPO_ROOT
            context_module.REPO_ROOT = root
            try:
                before = snapshot_paths((target,))
                file_path.write_text("after")
                after = snapshot_paths((target,))
                self.assertEqual(diff_snapshots(before, after), ("docs/skills/example/note.md",))
                restore_snapshot(before, (target,))
                self.assertEqual(file_path.read_text(), "before")
            finally:
                context_module.REPO_ROOT = original_root

    def test_write_policy_stays_inside_skill_scope(self):
        config = get_skill_config("vgc-team-builder")
        allowed = config.docs_dir / "examples" / "good-example.md"
        denied = REPO_ROOT / "plugins" / "vgc-coach-codex" / "README.md"
        self.assertTrue(is_path_allowed_for_write(str(allowed), config, allow_eval_tightening=False))
        self.assertFalse(is_path_allowed_for_write(str(denied), config, allow_eval_tightening=False))


if __name__ == "__main__":
    unittest.main()
