from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class DimensionScore:
    name: str
    score: int
    rationale: str


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
    evaluation_valid: bool = True
    grading_errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["dimension_scores"] = [asdict(score) for score in self.dimension_scores]
        return data


@dataclass(frozen=True)
class SkillEvaluation:
    skill: str
    average_score: float
    cases: tuple[CaseEvaluation, ...]
    failure_categories: tuple[str, ...]
    matched_fail_triggers: tuple[str, ...]
    summary: str
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
        }


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
    changed_files: tuple[str, ...]
    regressions: tuple[str, ...]
    sources_used: tuple[str, ...]
    evaluated_case_names: tuple[str, ...]
    skip_reason: str | None
    estimated_prompt_count: int
    estimated_premium_requests: int | None
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


def baseline_is_clean(evaluation: SkillEvaluation) -> bool:
    return all(
        case.evaluation_valid
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
) -> int:
    baseline_prompts = 2 * evaluated_case_count
    if mode == "review" or skipped_improvement:
        return baseline_prompts
    if candidate_evaluated:
        return baseline_prompts * 2 + 1
    return baseline_prompts + 1


def estimate_premium_requests(
    *,
    provider: str,
    model: str | None,
    prompt_count: int,
) -> int | None:
    if provider != "github-token":
        return None
    if model != "gpt-5.4":
        return None
    return prompt_count
