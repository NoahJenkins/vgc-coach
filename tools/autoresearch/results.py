from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

COPILOT_MODEL_MULTIPLIERS = {
    "gpt-5.4": 1.0,
    "gpt-5.4-mini": 0.33,
}

SCORE_DIMENSION_MIN = 0
SCORE_DIMENSION_MAX = 2


def score_scale_descriptor() -> dict[str, Any]:
    return {
        "per_dimension_min": SCORE_DIMENSION_MIN,
        "per_dimension_max": SCORE_DIMENSION_MAX,
        "allowed_values": list(range(SCORE_DIMENSION_MIN, SCORE_DIMENSION_MAX + 1)),
        "overall_score": "sum(dimension_scores)",
    }


@dataclass(frozen=True)
class DimensionScore:
    name: str
    score: int
    rationale: str


@dataclass(frozen=True)
class ResearchTrace:
    expectation: str
    live_research_expected: bool
    requested_urls: tuple[str, ...]
    attempted_urls: tuple[str, ...]
    approved_urls: tuple[str, ...]
    tool_arg_urls: tuple[str, ...]
    event_urls: tuple[str, ...]
    successful_source_urls: tuple[str, ...]
    tool_names: tuple[str, ...]
    read_paths: tuple[str, ...]
    shell_commands: tuple[str, ...]
    evidence_valid: bool
    verification_state: str
    evidence_source: str
    url_resolution_detail: str
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CaseEvaluation:
    case_name: str
    case_path: str
    request: str
    overall_score: int
    dimension_scores: tuple[DimensionScore, ...]
    checks_passed: tuple[str, ...]
    checks_failed: tuple[str, ...]
    failure_categories: tuple[str, ...]
    matched_fail_triggers: tuple[str, ...]
    summary: str
    recommended_smallest_fix: str
    source_urls: tuple[str, ...]
    response_path: str
    evaluation_path: str
    research_trace: ResearchTrace
    verification_state: str
    evidence_valid: bool
    evaluation_valid: bool = True
    grading_errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["dimension_scores"] = [asdict(score) for score in self.dimension_scores]
        data["research_trace"] = self.research_trace.to_dict()
        return data


@dataclass(frozen=True)
class SkillEvaluation:
    skill: str
    average_score: float
    cases: tuple[CaseEvaluation, ...]
    failure_categories: tuple[str, ...]
    matched_fail_triggers: tuple[str, ...]
    summary: str
    verification_state: str = "verified"
    evidence_valid: bool = True
    research_trace_summary: str = ""
    evaluation_valid: bool = True
    grading_errors: tuple[str, ...] = ()

    @property
    def evaluated_case_names(self) -> tuple[str, ...]:
        return tuple(case.case_name for case in self.cases)

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill": self.skill,
            "average_score": self.average_score,
            "cases": [case.to_dict() for case in self.cases],
            "failure_categories": list(self.failure_categories),
            "matched_fail_triggers": list(self.matched_fail_triggers),
            "summary": self.summary,
            "verification_state": self.verification_state,
            "evidence_valid": self.evidence_valid,
            "research_trace_summary": self.research_trace_summary,
        }


@dataclass(frozen=True)
class StandaloneEvalResult:
    kind: str
    status: str
    started_at: str
    finished_at: str
    report_dir: str
    skill: str
    provider: str
    model: str | None
    run_profile: str
    summary: str
    average_score: float | None
    case_count: int
    evaluated_case_names: tuple[str, ...]
    failure_categories: tuple[str, ...]
    matched_fail_triggers: tuple[str, ...]
    verification_state: str | None
    evidence_valid: bool | None
    research_trace_summary: str | None
    evaluation_valid: bool | None
    errors: tuple[str, ...]
    install_hint: str | None
    cases: tuple[CaseEvaluation, ...] = ()

    @classmethod
    def from_evaluation(
        cls,
        *,
        evaluation: SkillEvaluation,
        started_at: str,
        finished_at: str,
        report_dir: str,
        provider: str,
        model: str | None,
        run_profile: str,
    ) -> "StandaloneEvalResult":
        return cls(
            kind="standalone-eval",
            status="succeeded",
            started_at=started_at,
            finished_at=finished_at,
            report_dir=report_dir,
            skill=evaluation.skill,
            provider=provider,
            model=model,
            run_profile=run_profile,
            summary=evaluation.summary,
            average_score=evaluation.average_score,
            case_count=len(evaluation.cases),
            evaluated_case_names=evaluation.evaluated_case_names,
            failure_categories=evaluation.failure_categories,
            matched_fail_triggers=evaluation.matched_fail_triggers,
            verification_state=evaluation.verification_state,
            evidence_valid=evaluation.evidence_valid,
            research_trace_summary=evaluation.research_trace_summary,
            evaluation_valid=evaluation.evaluation_valid,
            errors=evaluation.grading_errors,
            install_hint=None,
            cases=evaluation.cases,
        )

    @classmethod
    def failure(
        cls,
        *,
        skill: str,
        started_at: str,
        finished_at: str,
        report_dir: str,
        provider: str,
        model: str | None,
        run_profile: str,
        errors: tuple[str, ...],
        install_hint: str | None = None,
    ) -> "StandaloneEvalResult":
        summary = errors[0] if errors else "Standalone eval failed."
        return cls(
            kind="standalone-eval",
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            report_dir=report_dir,
            skill=skill,
            provider=provider,
            model=model,
            run_profile=run_profile,
            summary=summary,
            average_score=None,
            case_count=0,
            evaluated_case_names=(),
            failure_categories=(),
            matched_fail_triggers=(),
            verification_state=None,
            evidence_valid=None,
            research_trace_summary=None,
            evaluation_valid=None,
            errors=errors,
            install_hint=install_hint,
            cases=(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "status": self.status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "report_dir": self.report_dir,
            "skill": self.skill,
            "provider": self.provider,
            "model": self.model,
            "run_profile": self.run_profile,
            "summary": self.summary,
            "average_score": self.average_score,
            "case_count": self.case_count,
            "evaluated_case_names": list(self.evaluated_case_names),
            "failure_categories": list(self.failure_categories),
            "matched_fail_triggers": list(self.matched_fail_triggers),
            "verification_state": self.verification_state,
            "evidence_valid": self.evidence_valid,
            "research_trace_summary": self.research_trace_summary,
            "evaluation_valid": self.evaluation_valid,
            "errors": list(self.errors),
            "install_hint": self.install_hint,
            "cases": [case.to_dict() for case in self.cases],
        }

    def to_summary_markdown(self) -> str:
        lines = [
            "# Standalone Eval",
            "",
            f"- Status: `{self.status}`",
            f"- Skill: `{self.skill}`",
            f"- Report dir: `{self.report_dir}`",
            f"- Provider: `{self.provider}`",
            f"- Model: `{self.model or 'default'}`",
            f"- Profile: `{self.run_profile}`",
            f"- Started: `{self.started_at}`",
            f"- Finished: `{self.finished_at}`",
        ]
        if self.average_score is not None:
            lines.append(f"- Average score: `{self.average_score}`")
        lines.append(f"- Case count: `{self.case_count}`")
        if self.verification_state is not None:
            lines.append(f"- Verification: `{self.verification_state}`")
        if self.evaluated_case_names:
            lines.append(
                f"- Evaluated cases: {', '.join(f'`{name}`' for name in self.evaluated_case_names)}"
            )
        lines.extend(
            [
                "",
                "## Summary",
                "",
                self.summary or "No summary recorded.",
            ]
        )
        if self.research_trace_summary:
            lines.extend(["", "## Research Trace", "", self.research_trace_summary])
        if self.errors:
            lines.extend(["", "## Errors", ""])
            lines.extend(f"- {error}" for error in self.errors)
        if self.install_hint:
            lines.extend(["", "## Install Hint", "", f"`{self.install_hint}`"])
        return "\n".join(lines) + "\n"


@dataclass(frozen=True)
class FullEvalSkillReport:
    skill: str
    status: str
    report_dir: str
    result_path: str
    summary_path: str
    run_status_path: str
    average_score: float | None
    case_count: int
    evaluated_case_names: tuple[str, ...]
    verification_state: str | None
    evidence_valid: bool | None
    research_trace_summary: str | None
    evaluation_valid: bool | None
    summary: str
    errors: tuple[str, ...]

    @classmethod
    def from_standalone_result(
        cls,
        result: StandaloneEvalResult,
        *,
        result_path: str,
        summary_path: str,
        run_status_path: str,
    ) -> "FullEvalSkillReport":
        return cls(
            skill=result.skill,
            status=result.status,
            report_dir=result.report_dir,
            result_path=result_path,
            summary_path=summary_path,
            run_status_path=run_status_path,
            average_score=result.average_score,
            case_count=result.case_count,
            evaluated_case_names=result.evaluated_case_names,
            verification_state=result.verification_state,
            evidence_valid=result.evidence_valid,
            research_trace_summary=result.research_trace_summary,
            evaluation_valid=result.evaluation_valid,
            summary=result.summary,
            errors=result.errors,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill": self.skill,
            "status": self.status,
            "report_dir": self.report_dir,
            "result_path": self.result_path,
            "summary_path": self.summary_path,
            "run_status_path": self.run_status_path,
            "average_score": self.average_score,
            "case_count": self.case_count,
            "evaluated_case_names": list(self.evaluated_case_names),
            "verification_state": self.verification_state,
            "evidence_valid": self.evidence_valid,
            "research_trace_summary": self.research_trace_summary,
            "evaluation_valid": self.evaluation_valid,
            "summary": self.summary,
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class FullEvalResult:
    kind: str
    status: str
    started_at: str
    finished_at: str
    report_dir: str
    provider: str
    model: str | None
    run_profile: str
    summary: str
    requested_skills: tuple[str, ...]
    completed_skills: tuple[str, ...]
    failed_skills: tuple[str, ...]
    total_case_count: int
    skill_reports: tuple[FullEvalSkillReport, ...]
    verification_state: str | None
    evidence_valid: bool | None
    errors: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "status": self.status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "report_dir": self.report_dir,
            "provider": self.provider,
            "model": self.model,
            "run_profile": self.run_profile,
            "summary": self.summary,
            "requested_skills": list(self.requested_skills),
            "completed_skills": list(self.completed_skills),
            "failed_skills": list(self.failed_skills),
            "requested_skill_count": len(self.requested_skills),
            "completed_skill_count": len(self.completed_skills),
            "failed_skill_count": len(self.failed_skills),
            "total_case_count": self.total_case_count,
            "skill_reports": [report.to_dict() for report in self.skill_reports],
            "verification_state": self.verification_state,
            "evidence_valid": self.evidence_valid,
            "errors": list(self.errors),
        }

    def to_summary_markdown(self) -> str:
        lines = [
            "# Full Eval",
            "",
            f"- Status: `{self.status}`",
            f"- Report dir: `{self.report_dir}`",
            f"- Provider: `{self.provider}`",
            f"- Model: `{self.model or 'default'}`",
            f"- Profile: `{self.run_profile}`",
            f"- Started: `{self.started_at}`",
            f"- Finished: `{self.finished_at}`",
            f"- Requested skills: `{len(self.requested_skills)}`",
            f"- Completed skills: `{len(self.completed_skills)}`",
            f"- Failed skills: `{len(self.failed_skills)}`",
            f"- Total cases: `{self.total_case_count}`",
        ]
        if self.verification_state is not None:
            lines.append(f"- Verification: `{self.verification_state}`")
        if self.evidence_valid is not None:
            lines.append(f"- Evidence valid: `{self.evidence_valid}`")
        lines.extend(
            [
                "",
                "## Summary",
                "",
                self.summary or "No summary recorded.",
                "",
                "## Skill Results",
                "",
            ]
        )
        for report in self.skill_reports:
            score_text = "n/a" if report.average_score is None else str(report.average_score)
            lines.append(
                f"- `{report.skill}`: `{report.status}` score `{score_text}` "
                f"cases `{report.case_count}`"
            )
        if self.errors:
            lines.extend(["", "## Errors", ""])
            lines.extend(f"- {error}" for error in self.errors)
        return "\n".join(lines) + "\n"


@dataclass(frozen=True)
class AutoresearchResult:
    skill: str
    run_date: str
    mode: str
    run_profile: str
    runtime_engine: str
    provider: str
    model: str | None
    baseline_score: float
    candidate_score: float | None
    score_improved: bool
    accepted_candidate: bool
    pr_candidate: bool
    decision: str
    decision_reason: str
    verification_state: str
    research_trace_summary: str
    score_scale: dict[str, Any]
    full_eval_required: bool
    full_eval_status: str | None
    full_eval_report_dir: str | None
    changed_files: tuple[str, ...]
    regressions: tuple[str, ...]
    sources_used: tuple[str, ...]
    evaluated_case_names: tuple[str, ...]
    skip_reason: str | None
    estimated_prompt_count: int
    estimated_premium_requests: float | None
    baseline_summary: str
    candidate_summary: str | None
    improvement_summary: str | None
    report_dir: str
    errors: tuple[str, ...]
    baseline_eval_valid: bool
    candidate_eval_valid: bool | None
    grading_errors: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def aggregate_verification_state(states: tuple[str | None, ...]) -> str | None:
    concrete_states = [state for state in states if state is not None]
    if not concrete_states:
        return None
    if "invalid_grading" in concrete_states:
        return "invalid_grading"
    if "inconclusive" in concrete_states:
        return "inconclusive"
    return "verified"


def baseline_is_clean(evaluation: SkillEvaluation) -> bool:
    return all(
        case.evaluation_valid
        and case.evidence_valid
        and not case.matched_fail_triggers
        and not case.checks_failed
        and not case.failure_categories
        for case in evaluation.cases
    )


def estimate_prompt_count(
    *,
    mode: str,
    evaluated_case_count: int,
    skipped_improvement: bool,
    candidate_evaluated: bool,
    confirmation_evaluated_case_count: int = 0,
) -> int:
    baseline_prompts = 2 * evaluated_case_count
    if mode == "review" or skipped_improvement:
        return baseline_prompts
    prompt_count = baseline_prompts + 1
    if candidate_evaluated:
        prompt_count += baseline_prompts
    prompt_count += 2 * confirmation_evaluated_case_count
    return prompt_count


def estimate_premium_requests(
    *,
    provider: str,
    model: str | None,
    prompt_count: int,
) -> float | None:
    if provider != "github-token":
        return None
    if model is None:
        return None
    multiplier = COPILOT_MODEL_MULTIPLIERS.get(model.lower())
    if multiplier is None:
        return None
    return round(prompt_count * multiplier, 2)
