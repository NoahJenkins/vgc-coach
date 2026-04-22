from __future__ import annotations

from pathlib import Path

from .config import SkillConfig
from .context import load_skill_context
from .copilot_sdk import AUTORESEARCH_INSTALL_COMMAND, get_copilot_sdk_preflight_error
from .evals import evaluate_skill
from .reporting import current_timestamp, reset_report_dir, write_json, write_run_status, write_summary
from .results import StandaloneEvalResult


async def run_standalone_eval(
    *,
    config: SkillConfig,
    provider_name: str,
    model: str | None,
    run_profile: str,
    case_limit: int | None,
    session_timeout: float,
    report_dir: Path,
) -> StandaloneEvalResult:
    reset_report_dir(report_dir)
    started_at = current_timestamp()
    write_run_status(
        report_dir,
        kind="standalone-eval",
        status="running",
        started_at=started_at,
        finished_at=None,
        summary=f"Running standalone eval for {config.name}.",
        errors=(),
    )

    result_path = report_dir / "result.json"
    summary_path = report_dir / "summary.md"
    preflight_error = get_copilot_sdk_preflight_error()
    if preflight_error:
        finished_at = current_timestamp()
        result = StandaloneEvalResult.failure(
            skill=config.name,
            started_at=started_at,
            finished_at=finished_at,
            report_dir=report_dir.resolve().as_posix(),
            provider=provider_name,
            model=model,
            run_profile=run_profile,
            errors=(preflight_error,),
            install_hint=AUTORESEARCH_INSTALL_COMMAND,
        )
        write_json(result_path, result.to_dict())
        write_summary(summary_path, result.to_summary_markdown())
        write_run_status(
            report_dir,
            kind=result.kind,
            status=result.status,
            started_at=started_at,
            finished_at=finished_at,
            summary=result.summary,
            errors=result.errors,
            result_path=result_path.resolve().as_posix(),
            summary_path=summary_path.resolve().as_posix(),
        )
        return result

    try:
        ctx = load_skill_context(config)
        evaluation = await evaluate_skill(
            ctx=ctx,
            provider_name=provider_name,
            model=model,
            output_dir=report_dir,
            run_profile=run_profile,
            case_limit=case_limit,
            session_timeout=session_timeout,
        )
        finished_at = current_timestamp()
        result = StandaloneEvalResult.from_evaluation(
            evaluation=evaluation,
            started_at=started_at,
            finished_at=finished_at,
            report_dir=report_dir.resolve().as_posix(),
            provider=provider_name,
            model=model,
            run_profile=run_profile,
        )
    except Exception as exc:
        finished_at = current_timestamp()
        result = StandaloneEvalResult.failure(
            skill=config.name,
            started_at=started_at,
            finished_at=finished_at,
            report_dir=report_dir.resolve().as_posix(),
            provider=provider_name,
            model=model,
            run_profile=run_profile,
            errors=(f"{type(exc).__name__}: {exc}",),
        )

    write_json(result_path, result.to_dict())
    write_summary(summary_path, result.to_summary_markdown())
    write_run_status(
        report_dir,
        kind=result.kind,
        status=result.status,
        started_at=started_at,
        finished_at=result.finished_at,
        summary=result.summary,
        errors=result.errors,
        result_path=result_path.resolve().as_posix(),
        summary_path=summary_path.resolve().as_posix(),
    )
    return result
