from __future__ import annotations

import datetime as dt
import importlib.util
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
    load_case_file,
    load_skill_context,
    restore_snapshot,
    snapshot_paths,
)
from autoresearch.evals import _normalize_evaluation_payload, select_cases  # noqa: E402
from autoresearch.policy import (  # noqa: E402
    get_allowed_write_roots,
    is_path_allowed_for_write,
)
from autoresearch.results import (  # noqa: E402
    SkillEvaluation,
    baseline_is_clean,
    estimate_premium_requests,
    estimate_prompt_count,
)

AUTORESEARCH_SCRIPT_SPEC = importlib.util.spec_from_file_location(
    "autoresearch_cli_module",
    REPO_ROOT / "tools" / "autoresearch.py",
)
AUTORESEARCH_SCRIPT = importlib.util.module_from_spec(AUTORESEARCH_SCRIPT_SPEC)
assert AUTORESEARCH_SCRIPT_SPEC.loader is not None
AUTORESEARCH_SCRIPT_SPEC.loader.exec_module(AUTORESEARCH_SCRIPT)


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

    def test_rubric_fail_trigger_extraction_tolerates_missing_section(self):
        rubric = (REPO_ROOT / "data" / "rubrics" / "lead-planner-rubric.md").read_text()
        self.assertEqual(extract_rubric_fail_triggers(rubric), ())

    def test_load_case_file_supports_inline_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "case-inline.md"
            path.write_text(
                "\n".join(
                    [
                        "# Case",
                        "",
                        "Request: build around Mega Venusaur",
                        "",
                        "Checks:",
                        "- one",
                    ]
                )
            )
            case = load_case_file(path)
            self.assertEqual(case.request, "build around Mega Venusaur")

    def test_load_case_file_supports_multiline_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "case-multiline.md"
            path.write_text(
                "\n".join(
                    [
                        "# Case",
                        "",
                        "Request:",
                        "",
                        "`Build me an anti-meta Mega Venusaur team for current Champions.`",
                        "",
                        "Checks:",
                        "- one",
                    ]
                )
            )
            case = load_case_file(path)
            self.assertEqual(
                case.request,
                "`Build me an anti-meta Mega Venusaur team for current Champions.`",
            )

    def test_load_case_file_rejects_empty_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "case-empty.md"
            path.write_text(
                "\n".join(
                    [
                        "# Case",
                        "",
                        "Request:",
                        "",
                        "Checks:",
                        "- one",
                    ]
                )
            )
            with self.assertRaisesRegex(ValueError, "empty Request block"):
                load_case_file(path)

    def test_real_multiline_team_builder_request_parses(self):
        case = load_case_file(REPO_ROOT / "data" / "fixtures" / "evals" / "team-builder" / "case-04.md")
        self.assertIn("Mega Venusaur", case.request)
        self.assertIn("community sources might be missing or down", case.request)

    def test_real_multiline_meta_research_request_parses(self):
        case = load_case_file(REPO_ROOT / "data" / "fixtures" / "evals" / "meta-research" / "case-02.md")
        self.assertIn("Terastallization", case.request)
        self.assertIn("current Pokemon Champions regulation", case.request)

    def test_real_multiline_team_audit_request_parses(self):
        case = load_case_file(REPO_ROOT / "data" / "fixtures" / "evals" / "team-audit" / "case-02.md")
        self.assertIn("too many fast attackers", case.request)
        self.assertIn("positioning tools", case.request)

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

    def test_daily_sentinel_write_scope_is_skill_only_by_default(self):
        config = get_skill_config("vgc-team-builder")
        roots = get_allowed_write_roots(
            config,
            allow_eval_tightening=False,
            run_profile="daily_sentinel",
        )
        self.assertEqual(roots, (config.skill_file,))
        self.assertFalse(
            is_path_allowed_for_write(
                str(config.docs_dir / "references" / "build-principles.md"),
                config,
                allow_eval_tightening=False,
                run_profile="daily_sentinel",
            )
        )

    def test_manual_write_scope_still_allows_skill_docs(self):
        config = get_skill_config("vgc-team-builder")
        roots = get_allowed_write_roots(
            config,
            allow_eval_tightening=False,
            run_profile="manual",
        )
        self.assertEqual(roots, (config.skill_file, config.docs_dir))

    def test_baseline_is_clean_requires_no_actionable_issues(self):
        clean_case = type(
            "CaseStub",
            (),
            {
                "case_name": "case-01",
                "matched_fail_triggers": (),
                "checks_failed": (),
                "failure_categories": (),
                "recommended_smallest_fix": "tighten item verification if possible",
                "evaluation_valid": True,
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
                "evaluation_valid": True,
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
        self.assertEqual(
            estimate_premium_requests(
                provider="github-token",
                model="gpt-5.4-mini",
                prompt_count=5,
            ),
            1.65,
        )
        self.assertEqual(
            estimate_premium_requests(
                provider="github-token",
                model="GPT-5.4-MINI",
                prompt_count=3,
            ),
            0.99,
        )
        self.assertIsNone(
            estimate_premium_requests(
                provider="byok-openai",
                model="gpt-5.4",
                prompt_count=5,
            )
        )

    def test_improvement_prompt_requires_preserving_passing_checks(self):
        weakest_case = type(
            "CaseStub",
            (),
            {
                "case_name": "case-04",
                "overall_score": 43,
                "recommended_smallest_fix": "verify non-Mega held items",
                "checks_passed": (
                    "uses `inference-heavy early read` if the minimum live source stack is incomplete",
                ),
                "checks_failed": (),
            },
        )()
        baseline = type(
            "BaselineStub",
            (),
            {
                "summary": "Strong pass.",
                "failure_categories": (),
                "matched_fail_triggers": (),
            },
        )()
        prompt = AUTORESEARCH_SCRIPT._build_improvement_prompt(
            "vgc-team-builder",
            baseline,
            weakest_case,
        )
        self.assertIn("Preserve all currently passing checks", prompt)
        self.assertIn("Currently passing checks:", prompt)
        self.assertIn("do not upgrade an `inference-heavy early read`", prompt)

    def test_candidate_outcome_rejected_only_for_failed_candidate(self):
        pr_candidate, decision = AUTORESEARCH_SCRIPT._determine_candidate_outcome(
            accepted_candidate=False,
            open_pr=False,
        )
        self.assertFalse(pr_candidate)
        self.assertEqual(decision, "rejected")

    def test_candidate_outcome_accepts_without_pr_when_open_pr_disabled(self):
        pr_candidate, decision = AUTORESEARCH_SCRIPT._determine_candidate_outcome(
            accepted_candidate=True,
            open_pr=False,
        )
        self.assertFalse(pr_candidate)
        self.assertEqual(decision, "accepted_no_pr")

    def test_candidate_outcome_opens_pr_when_enabled(self):
        pr_candidate, decision = AUTORESEARCH_SCRIPT._determine_candidate_outcome(
            accepted_candidate=True,
            open_pr=True,
        )
        self.assertTrue(pr_candidate)
        self.assertEqual(decision, "pr_opened")

    def test_invalid_grading_payload_fails_closed(self):
        payload = _normalize_evaluation_payload(
            {
                "dimension_scores": [
                    {"name": "", "score": 5, "rationale": "x"},
                    {"name": "two", "score": 4, "rationale": "y"},
                ],
                "checks_passed": [],
                "checks_failed": [],
                "failure_categories": [],
                "matched_fail_triggers": [],
                "summary": "bad total",
                "recommended_smallest_fix": "none",
            },
            "case-04",
        )
        self.assertFalse(payload["evaluation_valid"])
        self.assertEqual(payload["overall_score"], 0)
        self.assertIn("name is empty", payload["grading_errors"][0])

    def test_valid_dimension_only_payload_computes_total(self):
        payload = _normalize_evaluation_payload(
            {
                "dimension_scores": [
                    {"name": "one", "score": 20, "rationale": "x"},
                    {"name": "two", "score": 23, "rationale": "y"},
                ],
                "checks_passed": [],
                "checks_failed": [],
                "failure_categories": [],
                "matched_fail_triggers": [],
                "summary": "valid total",
                "recommended_smallest_fix": "none",
            },
            "case-04",
        )
        self.assertTrue(payload["evaluation_valid"])
        self.assertEqual(payload["overall_score"], 43)
        self.assertIsNone(payload["reported_overall_score"])

    def test_valid_fail_trigger_payload_caps_after_validation(self):
        payload = _normalize_evaluation_payload(
            {
                "dimension_scores": [
                    {"name": "one", "score": 20, "rationale": "x"},
                    {"name": "two", "score": 23, "rationale": "y"},
                ],
                "checks_passed": [],
                "checks_failed": [],
                "failure_categories": [],
                "matched_fail_triggers": ["one"],
                "summary": "valid total",
                "recommended_smallest_fix": "none",
            },
            "case-04",
        )
        self.assertTrue(payload["evaluation_valid"])
        self.assertEqual(payload["overall_score"], 40)

    def test_normalizes_scalar_list_fields(self):
        payload = _normalize_evaluation_payload(
            {
                "dimension_scores": [
                    {"name": "one", "score": 2, "rationale": "x"},
                ],
                "checks_passed": "first check",
                "checks_failed": None,
                "failure_categories": [" alpha ", ""],
                "matched_fail_triggers": "trigger",
                "summary": "ok",
                "recommended_smallest_fix": "none",
            },
            "case-04",
        )
        self.assertTrue(payload["evaluation_valid"])
        self.assertEqual(payload["checks_passed"], ["first check"])
        self.assertEqual(payload["checks_failed"], [])
        self.assertEqual(payload["failure_categories"], ["alpha"])
        self.assertEqual(payload["matched_fail_triggers"], ["trigger"])

    def test_grading_prompt_no_longer_requests_overall_score(self):
        source = (REPO_ROOT / "tools" / "autoresearch" / "evals.py").read_text()
        self.assertIn('"dimension_scores"', source)
        self.assertNotIn('"overall_score": 0,', source)


if __name__ == "__main__":
    unittest.main()
