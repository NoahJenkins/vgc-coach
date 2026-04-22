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
from autoresearch.evals import select_cases  # noqa: E402
from autoresearch.policy import is_path_allowed_for_write  # noqa: E402
from autoresearch.results import (  # noqa: E402
    SkillEvaluation,
    baseline_is_clean,
    estimate_premium_requests,
    estimate_prompt_count,
)


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

    def test_priority_skills_have_explicit_sentinel_cases(self):
        for skill_name in (
            "vgc-meta-research",
            "vgc-team-builder",
            "vgc-team-audit",
            "vgc-lead-planner",
            "vgc-battle-review",
        ):
            self.assertIsNotNone(get_skill_config(skill_name).sentinel_case_name)

    def test_daily_sentinel_profile_uses_configured_case(self):
        ctx = load_skill_context(get_skill_config("vgc-team-builder"))
        selected = select_cases(ctx=ctx, run_profile="daily_sentinel", case_limit=99)
        self.assertEqual(tuple(case.name for case in selected), ("case-04",))

    def test_manual_profile_still_honors_case_limit(self):
        ctx = load_skill_context(get_skill_config("vgc-team-builder"))
        selected = select_cases(ctx=ctx, run_profile="manual", case_limit=2)
        self.assertEqual(tuple(case.name for case in selected), ("case-01", "case-02"))

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

    def test_baseline_is_clean_requires_no_actionable_issues(self):
        clean_case = type(
            "CaseStub",
            (),
            {
                "case_name": "case-01",
                "matched_fail_triggers": (),
                "checks_failed": (),
                "failure_categories": (),
                "recommended_smallest_fix": "",
            },
        )()
        dirty_case = type(
            "CaseStub",
            (),
            {
                "case_name": "case-02",
                "matched_fail_triggers": (),
                "checks_failed": ("one",),
                "failure_categories": (),
                "recommended_smallest_fix": "",
            },
        )()
        self.assertTrue(
            baseline_is_clean(
                SkillEvaluation(
                    skill="vgc-team-builder",
                    average_score=80.0,
                    cases=(clean_case,),
                    failure_categories=(),
                    matched_fail_triggers=(),
                    summary="clean",
                )
            )
        )
        self.assertFalse(
            baseline_is_clean(
                SkillEvaluation(
                    skill="vgc-team-builder",
                    average_score=60.0,
                    cases=(dirty_case,),
                    failure_categories=(),
                    matched_fail_triggers=(),
                    summary="dirty",
                )
            )
        )

    def test_prompt_and_premium_estimates_match_branch_shape(self):
        self.assertEqual(
            estimate_prompt_count(
                mode="review",
                evaluated_case_count=1,
                skipped_improvement=False,
                candidate_evaluated=False,
            ),
            2,
        )
        self.assertEqual(
            estimate_prompt_count(
                mode="improve",
                evaluated_case_count=1,
                skipped_improvement=True,
                candidate_evaluated=False,
            ),
            2,
        )
        self.assertEqual(
            estimate_prompt_count(
                mode="improve",
                evaluated_case_count=1,
                skipped_improvement=False,
                candidate_evaluated=False,
            ),
            3,
        )
        self.assertEqual(
            estimate_prompt_count(
                mode="improve",
                evaluated_case_count=1,
                skipped_improvement=False,
                candidate_evaluated=True,
            ),
            5,
        )
        self.assertEqual(
            estimate_premium_requests(
                provider="github-token",
                model="gpt-5.4",
                prompt_count=5,
            ),
            5,
        )
        self.assertIsNone(
            estimate_premium_requests(
                provider="byok-openai",
                model="gpt-5.4",
                prompt_count=5,
            )
        )


if __name__ == "__main__":
    unittest.main()
