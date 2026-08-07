#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
from datetime import date
from pathlib import Path

from autoresearch.config import DEFAULT_REPORT_ROOT, REPO_ROOT, choose_skill, parse_run_date
from autoresearch.context import diff_snapshots, load_skill_context, restore_snapshot, snapshot_paths
from autoresearch.copilot_sdk import run_session
from autoresearch.evals import evaluate_skill
from autoresearch.policy import get_allowed_write_roots
from autoresearch.results import (
    AutoresearchResult,
    StandaloneEvalResult,
    baseline_is_clean,
    estimate_premium_requests,
    estimate_prompt_count,
    score_scale_descriptor,
)
from autoresearch.standalone import run_standalone_eval


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local autoresearch harness for vgc-coach skills.")
    parser.add_argument("--skill", default="auto", help="Skill name or auto")
    parser.add_argument("--date", default=None, help="Run date override in YYYY-MM-DD format")
    parser.add_argument("--mode", choices=("review", "improve"), required=True)
    parser.add_argument(
        "--provider",
        choices=("github-token", "byok-openai"),
        default="github-token",
        help="Copilot SDK auth/provider mode",
    )
    parser.add_argument(
        "--profile",
        choices=("daily_sentinel", "manual"),
        default="manual",
        help="Run profile",
    )
    parser.add_argument("--model", default=None, help="Model override")
    parser.add_argument(
        "--case-limit",
        type=int,
        default=None,
        help="Limit evals to the first N cases for smoke testing",
    )
    parser.add_argument(
        "--session-timeout",
        type=float,
        default=900.0,
        help="Per-model-call timeout in seconds",
    )
    parser.add_argument(
        "--report-dir",
        default=str(DEFAULT_REPORT_ROOT),
        help="Base report directory",
    )
    parser.add_argument(
        "--open-pr",
        action="store_true",
        help="Mark successful candidates as PR-eligible for the caller",
    )
    parser.add_argument(
        "--allow-eval-tightening",
        action="store_true",
        help="Allow edits under the target fixture/rubric files in addition to skill/docs",
    )
    parser.add_argument(
        "--allow-dirty-write-scope",
        action="store_true",
        help="Allow improve mode even when the target write scope is already dirty",
    )
    return parser.parse_args()


async def main() -> int:
    args = parse_args()
    run_date = parse_run_date(args.date)
    config = choose_skill(args.skill, run_date)
    ctx = load_skill_context(config)
    report_dir = Path(args.report_dir) / run_date.isoformat() / config.name
    report_dir.mkdir(parents=True, exist_ok=True)

    baseline_dir = report_dir / "baseline"
    baseline = await evaluate_skill(
        ctx=ctx,
        provider_name=args.provider,
        model=args.model,
        output_dir=baseline_dir,
        run_profile=args.profile,
        case_limit=args.case_limit,
        session_timeout=args.session_timeout,
    )
    _write_skill_evaluation(report_dir / "baseline.json", baseline)
    (report_dir / "baseline-summary.md").write_text(baseline.summary + "\n")

    candidate = None
    confirmation_result: StandaloneEvalResult | None = None
    improvement_summary = None
    changed_files: tuple[str, ...] = ()
    regressions: tuple[str, ...] = ()
    sources_used = _collect_sources_from_evaluation(baseline)
    accepted_candidate = False
    pr_candidate = False
    decision = "review_only" if args.mode == "review" else "no_change"
    decision_reason = "Review mode records the baseline only."
    verification_state = baseline.verification_state
    research_trace_summary = baseline.research_trace_summary
    skip_reason = None
    full_eval_required = False
    errors: list[str] = []
    grading_errors: list[str] = list(baseline.grading_errors)

    if args.mode == "improve":
        if not baseline.evaluation_valid:
            errors.extend(baseline.grading_errors)
            decision = "invalid_baseline"
            decision_reason = "Baseline grading output was invalid, so the run cannot trust its scoring signal."
        elif baseline_is_clean(baseline):
            skip_reason = "clean_baseline"
            decision = "clean_skip"
            decision_reason = (
                "Baseline passed the sentinel checks and recorded enough research evidence, so the run skipped improvement."
            )
        elif not baseline.evidence_valid:
            skip_reason = "inconclusive_baseline"
            decision = "inconclusive"
            decision_reason = (
                "Baseline findings are inconclusive because the currentness-sensitive cases did not record enough live research evidence."
            )
        else:
            initial_dirty = _write_scope_is_dirty(ctx, args.allow_eval_tightening, args.profile)
            if initial_dirty and not args.allow_dirty_write_scope:
                raise RuntimeError(
                    "The target write scope is already dirty. Re-run with --allow-dirty-write-scope "
                    "only if you want autoresearch to work on top of existing edits."
                )

            before_snapshot = snapshot_paths(_writable_roots(ctx, args.allow_eval_tightening, args.profile))
            improvement_result = await _run_improvement(
                ctx=ctx,
                report_dir=report_dir,
                baseline=baseline,
                provider_name=args.provider,
                model=args.model,
                allow_eval_tightening=args.allow_eval_tightening,
                run_profile=args.profile,
                session_timeout=args.session_timeout,
            )
            improvement_summary = improvement_result["text"].strip()
            sources_used = tuple(sorted(set(sources_used) | set(improvement_result["source_urls"])))
            (report_dir / "improvement-summary.md").write_text(improvement_summary + "\n")

            after_snapshot = snapshot_paths(_writable_roots(ctx, args.allow_eval_tightening, args.profile))
            changed_files = diff_snapshots(before_snapshot, after_snapshot)

            if changed_files:
                candidate_dir = report_dir / "candidate"
                candidate = await evaluate_skill(
                    ctx=ctx,
                    provider_name=args.provider,
                    model=args.model,
                    output_dir=candidate_dir,
                    run_profile=args.profile,
                    case_limit=args.case_limit,
                    session_timeout=args.session_timeout,
                )
                _write_skill_evaluation(report_dir / "candidate.json", candidate)
                (report_dir / "candidate-summary.md").write_text(candidate.summary + "\n")
                grading_errors.extend(candidate.grading_errors)
                sources_used = tuple(sorted(set(sources_used) | set(_collect_sources_from_evaluation(candidate))))
                verification_state = candidate.verification_state
                research_trace_summary = candidate.research_trace_summary

                regressions = (
                    _compute_regressions(baseline, candidate)
                    if baseline.evaluation_valid and candidate.evaluation_valid
                    else ()
                )
                accepted_candidate = (
                    candidate.evaluation_valid
                    and candidate.evidence_valid
                    and candidate.average_score > baseline.average_score
                    and not regressions
                    and not candidate.matched_fail_triggers
                )

                if not candidate.evaluation_valid:
                    decision = "invalid_candidate"
                    decision_reason = "Candidate grading output was invalid, so the edit was rejected."
                    accepted_candidate = False
                elif not candidate.evidence_valid:
                    decision = "inconclusive"
                    decision_reason = (
                        "Candidate output did not record enough live research evidence, so the improvement signal is not trustworthy."
                    )
                    accepted_candidate = False
                elif regressions:
                    decision = "rejected_regression"
                    decision_reason = f"Candidate introduced regressions: {', '.join(regressions)}."
                    accepted_candidate = False
                elif candidate.average_score <= baseline.average_score:
                    decision = "rejected_no_improvement"
                    decision_reason = (
                        "Candidate did not improve the baseline score after normalization, so the edit was rejected."
                    )
                    accepted_candidate = False
                elif candidate.matched_fail_triggers:
                    decision = "rejected_candidate_issues"
                    decision_reason = (
                        "Candidate still matched rubric fail triggers, so it is not eligible for automatic acceptance."
                    )
                    accepted_candidate = False

                if accepted_candidate and args.profile == "daily_sentinel":
                    full_eval_required = True
                    confirmation_result = await run_standalone_eval(
                        config=config,
                        provider_name=args.provider,
                        model=args.model,
                        run_profile="manual",
                        case_limit=None,
                        session_timeout=args.session_timeout,
                        report_dir=report_dir / "confirmation-full-eval",
                    )
                    sources_used = tuple(
                        sorted(set(sources_used) | set(_collect_sources_from_standalone_result(confirmation_result)))
                    )
                    verification_state = confirmation_result.verification_state or verification_state
                    research_trace_summary = confirmation_result.research_trace_summary or research_trace_summary
                    if not _confirmation_passed(confirmation_result):
                        accepted_candidate = False
                        decision = (
                            "inconclusive"
                            if confirmation_result.verification_state == "inconclusive"
                            else "confirmation_failed"
                        )
                        decision_reason = (
                            "Sentinel candidate looked better, but the follow-up full-skill confirmation did not produce a clean, evidence-valid result."
                        )
                    else:
                        pr_candidate, decision = _determine_candidate_outcome(
                            accepted_candidate=True,
                            open_pr=args.open_pr,
                            confirmed=True,
                        )
                        decision_reason = (
                            "Sentinel candidate improved the score and passed full-skill confirmation."
                        )
                elif accepted_candidate:
                    pr_candidate, decision = _determine_candidate_outcome(
                        accepted_candidate=True,
                        open_pr=args.open_pr,
                        confirmed=False,
                    )
                    decision_reason = "Candidate improved the baseline score without regressions."

                if not accepted_candidate and not initial_dirty:
                    restore_snapshot(
                        before_snapshot,
                        _writable_roots(ctx, args.allow_eval_tightening, args.profile),
                    )
            else:
                decision = "no_change"
                decision_reason = "Improvement attempt did not produce any file changes."

    prompt_count = estimate_prompt_count(
        mode=args.mode,
        evaluated_case_count=len(baseline.cases),
        skipped_improvement=skip_reason == "clean_baseline",
        candidate_evaluated=candidate is not None,
        confirmation_evaluated_case_count=0
        if confirmation_result is None
        else confirmation_result.case_count,
    )

    result = AutoresearchResult(
        skill=config.name,
        run_date=run_date.isoformat(),
        mode=args.mode,
        run_profile=args.profile,
        runtime_engine="copilot-sdk",
        provider=args.provider,
        model=args.model,
        baseline_score=baseline.average_score,
        candidate_score=None if candidate is None else candidate.average_score,
        score_improved=bool(candidate and candidate.average_score > baseline.average_score),
        accepted_candidate=accepted_candidate,
        pr_candidate=pr_candidate,
        decision=decision,
        decision_reason=decision_reason,
        verification_state=verification_state,
        research_trace_summary=research_trace_summary,
        score_scale=score_scale_descriptor(),
        full_eval_required=full_eval_required,
        full_eval_status=None if confirmation_result is None else confirmation_result.status,
        full_eval_report_dir=None if confirmation_result is None else confirmation_result.report_dir,
        changed_files=changed_files,
        regressions=regressions,
        sources_used=sources_used,
        evaluated_case_names=baseline.evaluated_case_names,
        skip_reason=skip_reason,
        estimated_prompt_count=prompt_count,
        estimated_premium_requests=estimate_premium_requests(
            provider=args.provider,
            model=args.model,
            prompt_count=prompt_count,
        ),
        baseline_summary=baseline.summary,
        candidate_summary=None if candidate is None else candidate.summary,
        improvement_summary=improvement_summary,
        report_dir=report_dir.as_posix(),
        errors=tuple(errors),
        baseline_eval_valid=baseline.evaluation_valid,
        candidate_eval_valid=None if candidate is None else candidate.evaluation_valid,
        grading_errors=tuple(dict.fromkeys(grading_errors)),
    )
    result_path = report_dir / "result.json"
    result_path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n")
    print(result_path)
    return 0


async def _run_improvement(
    *,
    ctx,
    report_dir: Path,
    baseline,
    provider_name: str,
    model: str | None,
    allow_eval_tightening: bool,
    run_profile: str,
    session_timeout: float,
) -> dict[str, object]:
    weakest_case = min(baseline.cases, key=lambda case: case.overall_score)
    prompt = _build_improvement_prompt(ctx.config.name, baseline, weakest_case)
    attachments = _build_improvement_attachments(ctx, report_dir, weakest_case)
    result = await run_session(
        prompt=prompt,
        attachments=attachments,
        provider_name=provider_name,
        model=model,
        allow_writes=True,
        allow_eval_tightening=allow_eval_tightening,
        run_profile=run_profile,
        allow_live_research=ctx.config.live_research_policy != "off",
        config=ctx.config,
        system_message=(
            "You are the vgc-coach guarded autoresearch worker. Make small, evidence-backed edits only."
        ),
        timeout=session_timeout,
    )
    return {"text": result.final_text, "source_urls": result.source_urls}


def _build_improvement_prompt(skill_name: str, baseline, weakest_case) -> str:
    passing_checks = ", ".join(weakest_case.checks_passed) or "none recorded"
    failing_checks = ", ".join(weakest_case.checks_failed) or "none recorded"
    return "\n".join(
        [
            f"Target skill: {skill_name}",
            "",
            "Review the attached baseline artifacts and improve the target skill with the smallest useful change.",
            "Use the weakest evaluated case as the primary target unless the baseline artifacts prove a different single fix is more important.",
            "Recommended smallest fix is advisory only. Do not chase it if doing so would break currently passing checks.",
            "Hard rules:",
            "- Edit only the approved write scope for this session.",
            "- Do not touch generated plugin outputs directly.",
            "- Preserve the published output contract unless the baseline evidence proves it is broken.",
            "- Preserve all currently passing checks unless the baseline artifacts prove a direct conflict.",
            "- Preserve existing pass-worthy section order and confidence framing unless the baseline evidence proves they are wrong.",
            "- Never invent current-format facts.",
            "- Do not widen freshness or source-stack confidence without newly demonstrated evidence in the edited contract.",
            "- If the skill needs live currentness checks, use absolute dates and keep uncertainty explicit.",
            "",
            f"Weakest evaluated case: {weakest_case.case_name} ({weakest_case.overall_score})",
            f"Recommended smallest fix: {weakest_case.recommended_smallest_fix or 'none recorded'}",
            f"Currently passing checks: {passing_checks}",
            f"Currently failing checks: {failing_checks}",
            "",
            "Baseline summary:",
            baseline.summary,
            "",
            "Recurring failure categories:",
            ", ".join(baseline.failure_categories) or "none",
            "",
            "Matched fail triggers:",
            ", ".join(baseline.matched_fail_triggers) or "none",
            "",
            (
                "If the baseline already passes freshness/currentness framing, do not upgrade an "
                "`inference-heavy early read` to `current-field recommendation` unless the edited "
                "contract now proves the minimum live source stack requirement."
            ),
            "",
            "After editing, reply with a concise summary of what exact issue you targeted and what existing behavior you intentionally preserved.",
        ]
    )


def _build_improvement_attachments(ctx, report_dir: Path, weakest_case) -> list[dict[str, str]]:
    attachments = [
        {"type": "file", "path": str(ctx.config.skill_file)},
        {"type": "directory", "path": str(ctx.config.docs_dir)},
        {"type": "directory", "path": str(ctx.config.fixture_dir)},
        {"type": "file", "path": str(ctx.config.rubric_file)},
        {"type": "file", "path": str(report_dir / "baseline.json")},
        {"type": "file", "path": str(REPO_ROOT / weakest_case.response_path)},
        {"type": "file", "path": str(REPO_ROOT / weakest_case.evaluation_path)},
    ]
    attachments.extend({"type": "file", "path": str(path)} for path in ctx.shared_reference_files)
    return attachments


def _compute_regressions(baseline, candidate) -> tuple[str, ...]:
    regressions = []
    baseline_by_case = {case.case_name: case for case in baseline.cases}
    for case in candidate.cases:
        before = baseline_by_case[case.case_name]
        if case.overall_score < before.overall_score:
            regressions.append(
                f"{case.case_name} dropped from {before.overall_score} to {case.overall_score}"
            )
        elif len(case.matched_fail_triggers) > len(before.matched_fail_triggers):
            regressions.append(f"{case.case_name} introduced new fail triggers")
    return tuple(regressions)


def _writable_roots(ctx, allow_eval_tightening: bool, run_profile: str) -> tuple[Path, ...]:
    return get_allowed_write_roots(
        ctx.config,
        allow_eval_tightening=allow_eval_tightening,
        run_profile=run_profile,
    )


def _write_scope_is_dirty(ctx, allow_eval_tightening: bool, run_profile: str) -> bool:
    paths = [
        path.relative_to(Path.cwd()).as_posix()
        for path in _writable_roots(ctx, allow_eval_tightening, run_profile)
    ]
    result = subprocess.run(
        ["git", "status", "--porcelain", "--", *paths],
        check=True,
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


def _confirmation_passed(result: StandaloneEvalResult) -> bool:
    if result.status != "succeeded":
        return False
    if result.evaluation_valid is not True or result.evidence_valid is not True:
        return False
    if result.verification_state != "verified":
        return False
    return all(
        not case.checks_failed and not case.failure_categories and not case.matched_fail_triggers
        for case in result.cases
    )


def _determine_candidate_outcome(
    *,
    accepted_candidate: bool,
    open_pr: bool,
    confirmed: bool,
) -> tuple[bool, str]:
    if not accepted_candidate:
        return False, "rejected"
    if confirmed:
        return open_pr, "accepted_after_confirmation"
    if open_pr:
        return True, "pr_opened"
    return False, "accepted_no_pr"


def _collect_sources_from_evaluation(evaluation) -> tuple[str, ...]:
    return tuple(sorted({url for case in evaluation.cases for url in case.source_urls}))


def _collect_sources_from_standalone_result(result: StandaloneEvalResult) -> tuple[str, ...]:
    return tuple(sorted({url for case in result.cases for url in case.source_urls}))


def _write_skill_evaluation(path: Path, evaluation) -> None:
    path.write_text(json.dumps(evaluation.to_dict(), indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
