#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
from datetime import date
from pathlib import Path

from autoresearch.config import DEFAULT_REPORT_ROOT, REPO_ROOT, RunProfile, choose_skill, parse_run_date
from autoresearch.context import diff_snapshots, load_skill_context, restore_snapshot, snapshot_paths
from autoresearch.copilot_sdk import run_session
from autoresearch.evals import evaluate_skill
from autoresearch.results import (
    AutoresearchResult,
    baseline_is_clean,
    estimate_premium_requests,
    estimate_prompt_count,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Nightly autoresearch harness for vgc-coach skills.")
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
    baseline_result_path = report_dir / "baseline.json"
    baseline_result_path.write_text(
        json.dumps(baseline.to_dict(), indent=2, sort_keys=True) + "\n"
    )
    (report_dir / "baseline-summary.md").write_text(baseline.summary + "\n")

    candidate = None
    improvement_summary = None
    changed_files: tuple[str, ...] = ()
    regressions: tuple[str, ...] = ()
    sources_used = sorted({url for case in baseline.cases for url in case.source_urls})
    accepted_candidate = False
    pr_candidate = False
    decision = "no_change"
    skip_reason = None
    errors: list[str] = []

    if args.mode == "improve":
        if baseline_is_clean(baseline):
            skip_reason = "clean_baseline"
        else:
            initial_dirty = _write_scope_is_dirty(ctx, args.allow_eval_tightening)
            if initial_dirty and not args.allow_dirty_write_scope:
                raise RuntimeError(
                    "The target write scope is already dirty. Re-run with --allow-dirty-write-scope "
                    "only if you want autoresearch to work on top of existing edits."
                )

            before_snapshot = snapshot_paths(_writable_roots(ctx, args.allow_eval_tightening))
            improvement_result = await _run_improvement(
                ctx=ctx,
                report_dir=report_dir,
                baseline=baseline,
                provider_name=args.provider,
                model=args.model,
                allow_eval_tightening=args.allow_eval_tightening,
                session_timeout=args.session_timeout,
            )
            improvement_summary = improvement_result["text"].strip()
            sources_used = sorted(set(sources_used) | set(improvement_result["source_urls"]))
            (report_dir / "improvement-summary.md").write_text(improvement_summary + "\n")

            after_snapshot = snapshot_paths(_writable_roots(ctx, args.allow_eval_tightening))
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
                (report_dir / "candidate.json").write_text(
                    json.dumps(candidate.to_dict(), indent=2, sort_keys=True) + "\n"
                )
                (report_dir / "candidate-summary.md").write_text(candidate.summary + "\n")
                regressions = _compute_regressions(baseline, candidate)
                accepted_candidate = (
                    candidate.average_score > baseline.average_score
                    and not regressions
                    and not candidate.matched_fail_triggers
                )
                pr_candidate = accepted_candidate
                decision = "pr_opened" if accepted_candidate and args.open_pr else "rejected"

                if not accepted_candidate and not initial_dirty:
                    restore_snapshot(before_snapshot, _writable_roots(ctx, args.allow_eval_tightening))
            else:
                decision = "no_change"

    prompt_count = estimate_prompt_count(
        mode=args.mode,
        evaluated_case_count=len(baseline.cases),
        skipped_improvement=skip_reason == "clean_baseline",
        candidate_evaluated=candidate is not None,
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
        changed_files=changed_files,
        regressions=regressions,
        sources_used=tuple(sources_used),
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
    session_timeout: float,
) -> dict[str, object]:
    weakest_case = min(baseline.cases, key=lambda case: case.overall_score)
    prompt = "\n".join(
        [
            f"Target skill: {ctx.config.name}",
            "",
            "Review the attached baseline artifacts and improve the target skill with the smallest useful change.",
            "Use the weakest evaluated case as the primary target unless the baseline artifacts prove a different single fix is more important.",
            "Hard rules:",
            "- Edit only the approved write scope for this session.",
            "- Do not touch generated plugin outputs directly.",
            "- Preserve the published output contract unless the baseline evidence proves it is broken.",
            "- Never invent current-format facts.",
            "- If the skill needs live currentness checks, use absolute dates and keep uncertainty explicit.",
            "",
            f"Weakest evaluated case: {weakest_case.case_name} ({weakest_case.overall_score})",
            f"Recommended smallest fix: {weakest_case.recommended_smallest_fix or 'none recorded'}",
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
            "After editing, reply with a concise summary of what changed and why.",
        ]
    )
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
    result = await run_session(
        prompt=prompt,
        attachments=attachments,
        provider_name=provider_name,
        model=model,
        allow_writes=True,
        allow_eval_tightening=allow_eval_tightening,
        allow_live_research=ctx.config.live_research_policy != "off",
        config=ctx.config,
        system_message=(
            "You are the vgc-coach nightly autoresearch worker. Make small, evidence-backed edits only."
        ),
        timeout=session_timeout,
    )
    return {"text": result.final_text, "source_urls": result.source_urls}


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


def _writable_roots(ctx, allow_eval_tightening: bool) -> tuple[Path, ...]:
    roots = [ctx.config.skill_file, ctx.config.docs_dir]
    if allow_eval_tightening:
        roots.extend((ctx.config.fixture_dir, ctx.config.rubric_file))
    return tuple(roots)


def _write_scope_is_dirty(ctx, allow_eval_tightening: bool) -> bool:
    paths = [path.relative_to(Path.cwd()).as_posix() for path in _writable_roots(ctx, allow_eval_tightening)]
    result = subprocess.run(
        ["git", "status", "--porcelain", "--", *paths],
        check=True,
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
