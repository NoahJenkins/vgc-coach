#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from autoresearch.config import DEFAULT_REPORT_ROOT, RunProfile, SKILL_CONFIGS, get_skill_config, parse_run_date
from autoresearch.reporting import current_timestamp, reset_report_dir, write_json, write_run_status, write_summary
from autoresearch.results import FullEvalResult, FullEvalSkillReport
from autoresearch.standalone import run_standalone_eval


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local full vgc-coach eval suite.")
    parser.add_argument("--date", default=None, help="Run date override in YYYY-MM-DD format")
    parser.add_argument(
        "--skills",
        nargs="*",
        default=None,
        help="Optional skill names or comma-separated skill lists. Defaults to all configured skills.",
    )
    parser.add_argument(
        "--provider",
        choices=("github-token", "byok-openai"),
        default="github-token",
        help="Copilot SDK auth/provider mode",
    )
    parser.add_argument("--model", default=None, help="Model override")
    parser.add_argument(
        "--profile",
        choices=("daily_sentinel", "manual"),
        default="manual",
        help="Run profile",
    )
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
    return parser.parse_args(argv)


def _parse_skill_names(raw_values: list[str] | None) -> tuple[str, ...]:
    if not raw_values:
        return tuple(SKILL_CONFIGS.keys())

    names: list[str] = []
    for raw in raw_values:
        for part in raw.split(","):
            name = part.strip()
            if name:
                names.append(name)
    if not names:
        return tuple(SKILL_CONFIGS.keys())
    return tuple(dict.fromkeys(names))


def _resolve_skill_names(raw_values: list[str] | None) -> tuple[str, ...]:
    names = _parse_skill_names(raw_values)
    for name in names:
        get_skill_config(name)
    return names


def _suite_status(*, requested_count: int, completed_count: int, failed_count: int) -> str:
    if failed_count == 0:
        return "succeeded"
    if completed_count == 0:
        return "failed"
    return "partial"


def _suite_summary(*, requested: tuple[str, ...], completed: tuple[str, ...], failed: tuple[str, ...]) -> str:
    if not requested:
        return "No skills were selected for the full eval suite."
    if not failed:
        return f"Completed all {len(completed)} requested skills."
    return (
        f"Completed {len(completed)} of {len(requested)} requested skills. "
        f"Failed skills: {', '.join(failed)}."
    )


async def run_full_eval_suite(
    *,
    skill_names: tuple[str, ...],
    provider_name: str,
    model: str | None,
    run_profile: RunProfile,
    case_limit: int | None,
    session_timeout: float,
    report_dir: Path,
) -> FullEvalResult:
    reset_report_dir(report_dir)
    started_at = current_timestamp()
    write_run_status(
        report_dir,
        kind="full-eval",
        status="running",
        started_at=started_at,
        finished_at=None,
        summary=f"Running full eval for {len(skill_names)} skills.",
        errors=(),
    )

    skill_reports: list[FullEvalSkillReport] = []
    suite_errors: list[str] = []
    for skill_name in skill_names:
        config = get_skill_config(skill_name)
        skill_report_dir = report_dir / "skills" / skill_name
        result = await run_standalone_eval(
            config=config,
            provider_name=provider_name,
            model=model,
            run_profile=run_profile,
            case_limit=case_limit,
            session_timeout=session_timeout,
            report_dir=skill_report_dir,
        )
        if result.status != "succeeded":
            suite_errors.append(f"{skill_name}: {result.summary}")
        skill_reports.append(
            FullEvalSkillReport.from_standalone_result(
                result,
                result_path=(skill_report_dir / "result.json").resolve().as_posix(),
                summary_path=(skill_report_dir / "summary.md").resolve().as_posix(),
                run_status_path=(skill_report_dir / "run-status.json").resolve().as_posix(),
            )
        )

    completed_skills = tuple(report.skill for report in skill_reports if report.status == "succeeded")
    failed_skills = tuple(report.skill for report in skill_reports if report.status != "succeeded")
    finished_at = current_timestamp()
    status = _suite_status(
        requested_count=len(skill_names),
        completed_count=len(completed_skills),
        failed_count=len(failed_skills),
    )
    result = FullEvalResult(
        kind="full-eval",
        status=status,
        started_at=started_at,
        finished_at=finished_at,
        report_dir=report_dir.resolve().as_posix(),
        provider=provider_name,
        model=model,
        run_profile=run_profile,
        summary=_suite_summary(
            requested=skill_names,
            completed=completed_skills,
            failed=failed_skills,
        ),
        requested_skills=skill_names,
        completed_skills=completed_skills,
        failed_skills=failed_skills,
        total_case_count=sum(report.case_count for report in skill_reports),
        skill_reports=tuple(skill_reports),
        errors=tuple(suite_errors),
    )

    result_path = report_dir / "result.json"
    summary_path = report_dir / "summary.md"
    write_json(result_path, result.to_dict())
    write_summary(summary_path, result.to_summary_markdown())
    write_run_status(
        report_dir,
        kind=result.kind,
        status=result.status,
        started_at=result.started_at,
        finished_at=result.finished_at,
        summary=result.summary,
        errors=result.errors,
        result_path=result_path.resolve().as_posix(),
        summary_path=summary_path.resolve().as_posix(),
    )
    return result


async def main() -> int:
    args = parse_args()
    run_date = parse_run_date(args.date)
    report_dir = Path(args.report_dir) / run_date.isoformat() / "full-eval"
    result_path = report_dir / "result.json"

    try:
        skill_names = _resolve_skill_names(args.skills)
        result = await run_full_eval_suite(
            skill_names=skill_names,
            provider_name=args.provider,
            model=args.model,
            run_profile=args.profile,
            case_limit=args.case_limit,
            session_timeout=args.session_timeout,
            report_dir=report_dir,
        )
    except Exception as exc:
        reset_report_dir(report_dir)
        started_at = current_timestamp()
        finished_at = current_timestamp()
        result = FullEvalResult(
            kind="full-eval",
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            report_dir=report_dir.resolve().as_posix(),
            provider=args.provider,
            model=args.model,
            run_profile=args.profile,
            summary=f"{type(exc).__name__}: {exc}",
            requested_skills=(),
            completed_skills=(),
            failed_skills=(),
            total_case_count=0,
            skill_reports=(),
            errors=(f"{type(exc).__name__}: {exc}",),
        )
        write_json(result_path, result.to_dict())
        write_summary(report_dir / "summary.md", result.to_summary_markdown())
        write_run_status(
            report_dir,
            kind=result.kind,
            status=result.status,
            started_at=result.started_at,
            finished_at=result.finished_at,
            summary=result.summary,
            errors=result.errors,
            result_path=result_path.resolve().as_posix(),
            summary_path=(report_dir / "summary.md").resolve().as_posix(),
        )

    print(result_path)
    return 0 if result.status == "succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
