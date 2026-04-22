from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .config import REPO_ROOT, RunProfile
from .context import CaseFile, SkillContext, extract_rubric_fail_triggers
from .copilot_sdk import run_session
from .reporting import write_json
from .results import (
    CaseEvaluation,
    DimensionScore,
    ResearchTrace,
    SCORE_DIMENSION_MAX,
    SCORE_DIMENSION_MIN,
    SkillEvaluation,
)

GENERATION_SYSTEM_MESSAGE = """
You are running inside the vgc-coach autoresearch harness.

Operate with the repo's AGENTS.md rules and the attached skill contract.
Do not mention the harness, grading, or internal reasoning in the final answer.
Return only the final user-facing answer for the fixture request.
""".strip()

GRADING_SYSTEM_MESSAGE = """
You are grading a candidate response for the vgc-coach repository.

Use the attached rubric and fixture literally. Return strict JSON only.
Do not wrap the JSON in markdown fences. Do not add prose before or after it.
""".strip()


async def evaluate_skill(
    *,
    ctx: SkillContext,
    provider_name: str,
    model: str | None,
    output_dir: Path,
    run_profile: RunProfile = "manual",
    case_limit: int | None = None,
    session_timeout: float = 900.0,
) -> SkillEvaluation:
    output_dir.mkdir(parents=True, exist_ok=True)
    rubric_fail_triggers = extract_rubric_fail_triggers(ctx.rubric_text)
    case_results: list[CaseEvaluation] = []
    cases = select_cases(ctx=ctx, run_profile=run_profile, case_limit=case_limit)

    for case in cases:
        case_dir = output_dir / case.name
        case_dir.mkdir(parents=True, exist_ok=True)

        response = await _generate_case_response(
            ctx=ctx,
            case=case,
            provider_name=provider_name,
            model=model,
            run_profile=run_profile,
            session_timeout=session_timeout,
        )
        response_path = case_dir / "response.md"
        response_path.write_text(response["text"].strip() + "\n")
        response_path_abs = response_path.resolve()

        research_trace = _build_research_trace(case=case, response=response)
        write_json(case_dir / "research-trace.json", research_trace.to_dict())

        raw_evaluation_payload = await _grade_case_response(
            ctx=ctx,
            case=case,
            response_text=response["text"],
            rubric_fail_triggers=rubric_fail_triggers,
            provider_name=provider_name,
            model=model,
            session_timeout=session_timeout,
        )
        evaluation_payload = _normalize_evaluation_payload(raw_evaluation_payload, case.name)
        evaluation_payload["research_trace"] = research_trace.to_dict()
        evaluation_payload["verification_state"] = research_trace.verification_state
        evaluation_payload["evidence_valid"] = research_trace.evidence_valid
        evaluation_path = case_dir / "evaluation.json"
        write_json(evaluation_path, evaluation_payload)
        evaluation_path_abs = evaluation_path.resolve()

        case_results.append(
            CaseEvaluation(
                case_name=case.name,
                case_path=case.path.relative_to(REPO_ROOT).as_posix(),
                request=case.request,
                overall_score=int(evaluation_payload["overall_score"]),
                dimension_scores=tuple(
                    DimensionScore(
                        name=str(score["name"]),
                        score=int(score["score"]),
                        rationale=str(score["rationale"]),
                    )
                    for score in evaluation_payload.get("dimension_scores", [])
                ),
                checks_passed=tuple(evaluation_payload.get("checks_passed", [])),
                checks_failed=tuple(evaluation_payload.get("checks_failed", [])),
                failure_categories=tuple(evaluation_payload.get("failure_categories", [])),
                matched_fail_triggers=tuple(evaluation_payload.get("matched_fail_triggers", [])),
                summary=str(evaluation_payload.get("summary", "")).strip(),
                recommended_smallest_fix=str(
                    evaluation_payload.get("recommended_smallest_fix", "")
                ).strip(),
                source_urls=tuple(response["source_urls"]),
                response_path=response_path_abs.relative_to(REPO_ROOT).as_posix(),
                evaluation_path=evaluation_path_abs.relative_to(REPO_ROOT).as_posix(),
                research_trace=research_trace,
                verification_state=research_trace.verification_state,
                evidence_valid=research_trace.evidence_valid,
                evaluation_valid=bool(evaluation_payload.get("evaluation_valid", True)),
                grading_errors=tuple(evaluation_payload.get("grading_errors", [])),
            )
        )

    average_score = round(
        sum(case.overall_score for case in case_results) / max(len(case_results), 1),
        2,
    )
    failure_categories = tuple(_top_items(case_results, "failure_categories"))
    matched_fail_triggers = tuple(_top_items(case_results, "matched_fail_triggers"))
    verification_state = _aggregate_verification_state(case_results)
    summary = _build_skill_summary(case_results, verification_state=verification_state)
    grading_errors = tuple(
        error
        for case in case_results
        for error in (f"{case.case_name}: {message}" for message in case.grading_errors)
    )
    return SkillEvaluation(
        skill=ctx.config.name,
        average_score=average_score,
        cases=tuple(case_results),
        failure_categories=failure_categories,
        matched_fail_triggers=matched_fail_triggers,
        summary=summary,
        verification_state=verification_state,
        evidence_valid=all(case.evidence_valid for case in case_results),
        research_trace_summary=_build_research_trace_summary(case_results),
        evaluation_valid=all(case.evaluation_valid for case in case_results),
        grading_errors=grading_errors,
    )


def select_cases(
    *,
    ctx: SkillContext,
    run_profile: RunProfile,
    case_limit: int | None,
) -> tuple[CaseFile, ...]:
    if run_profile == "daily_sentinel":
        sentinel_case_name = ctx.config.sentinel_case_name
        if not sentinel_case_name:
            raise ValueError(f"No sentinel case is configured for {ctx.config.name}")
        for case in ctx.cases:
            if case.name == sentinel_case_name:
                return (case,)
        raise ValueError(
            f"Sentinel case '{sentinel_case_name}' was not found for {ctx.config.name}"
        )
    if run_profile != "manual":
        raise ValueError(f"Unsupported run profile '{run_profile}'")
    return ctx.cases if case_limit is None else ctx.cases[:case_limit]


async def _generate_case_response(
    *,
    ctx: SkillContext,
    case: CaseFile,
    provider_name: str,
    model: str | None,
    run_profile: RunProfile,
    session_timeout: float,
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            f"Skill under test: {ctx.config.name}",
            "",
            "Read the attached skill contract and supporting docs before answering.",
            "Answer the following user request exactly as the shared skill should answer it today.",
            "Keep the response production-quality and user-facing.",
            "",
            f"User request: {case.request}",
        ]
    )
    attachments = [
        {"type": "file", "path": str(ctx.config.skill_file)},
        {"type": "directory", "path": str(ctx.config.docs_dir)},
    ]
    attachments.extend({"type": "file", "path": str(path)} for path in ctx.shared_reference_files)
    result = await run_session(
        prompt=prompt,
        attachments=attachments,
        provider_name=provider_name,
        model=model,
        allow_writes=False,
        allow_eval_tightening=False,
        run_profile=run_profile,
        allow_live_research=ctx.config.live_research_policy != "off",
        config=ctx.config,
        system_message=GENERATION_SYSTEM_MESSAGE,
        timeout=session_timeout,
    )
    return {
        "text": result.final_text,
        "source_urls": result.source_urls,
        "attempted_urls": result.attempted_urls,
        "approved_urls": result.approved_urls,
        "tool_names": result.tool_names,
        "read_paths": result.read_paths,
        "write_paths": result.write_paths,
        "shell_commands": result.shell_commands,
    }


async def _grade_case_response(
    *,
    ctx: SkillContext,
    case: CaseFile,
    response_text: str,
    rubric_fail_triggers: tuple[str, ...],
    provider_name: str,
    model: str | None,
    session_timeout: float,
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            f"Skill under review: {ctx.config.name}",
            "",
            "Grade the candidate response using the attached rubric and fixture.",
            "Use the rubric's language exactly when possible.",
            "Score only the rubric dimensions explicitly named in the attached rubric.",
            (
                "Use this fixed integer scoring scale for every dimension: "
                f"{SCORE_DIMENSION_MAX} = strong pass, 1 = mixed or partial, "
                f"{SCORE_DIMENSION_MIN} = fail or materially missing."
            ),
            "Do not invent any other numeric scale.",
            "Return `overall_score` as the exact sum of the dimension scores.",
            "If the rubric does not support a requested field, return an empty list instead of inventing structure.",
            "If fail-trigger language exists in the rubric or fixture, map it into `matched_fail_triggers`.",
            "Return JSON with this shape:",
            json.dumps(
                {
                    "overall_score": 0,
                    "dimension_scores": [{"name": "string", "score": 0, "rationale": "string"}],
                    "checks_passed": ["string"],
                    "checks_failed": ["string"],
                    "failure_categories": ["string"],
                    "matched_fail_triggers": ["string"],
                    "summary": "string",
                    "recommended_smallest_fix": "string",
                },
                indent=2,
            ),
            "",
            f"Fixture:\n{case.raw_text}",
            "",
            "Rubric fail triggers:",
            json.dumps(rubric_fail_triggers),
            "",
            "Candidate response:",
            response_text,
        ]
    )
    attachments = [{"type": "file", "path": str(ctx.config.rubric_file)}]
    result = await run_session(
        prompt=prompt,
        attachments=attachments,
        provider_name=provider_name,
        model=model,
        allow_writes=False,
        allow_eval_tightening=False,
        run_profile="manual",
        allow_live_research=False,
        config=ctx.config,
        system_message=GRADING_SYSTEM_MESSAGE,
        timeout=session_timeout,
    )
    payload = _parse_json_response(result.final_text)
    payload.setdefault("overall_score", None)
    payload.setdefault("dimension_scores", [])
    payload.setdefault("checks_passed", [])
    payload.setdefault("checks_failed", [])
    payload.setdefault("failure_categories", [])
    payload.setdefault("matched_fail_triggers", [])
    payload.setdefault("summary", "")
    payload.setdefault("recommended_smallest_fix", "")
    return payload


def _normalize_evaluation_payload(payload: dict[str, Any], case_name: str) -> dict[str, Any]:
    normalized = dict(payload)
    errors: list[str] = []

    raw_dimension_scores = normalized.get("dimension_scores", [])
    if not isinstance(raw_dimension_scores, list):
        raw_dimension_scores = []
        errors.append(f"grader returned non-list dimension_scores for {case_name}")

    dimension_scores: list[dict[str, Any]] = []
    for index, raw_score in enumerate(raw_dimension_scores):
        if not isinstance(raw_score, dict):
            errors.append(f"dimension_scores[{index}] is not an object for {case_name}")
            continue
        name = str(raw_score.get("name", "")).strip()
        if not name:
            errors.append(f"dimension_scores[{index}].name is empty for {case_name}")
            continue
        try:
            score_value = int(raw_score.get("score"))
        except (TypeError, ValueError):
            errors.append(
                f"dimension_scores[{index}].score is not numeric for {case_name}: "
                f"{raw_score.get('score')!r}"
            )
            continue
        if score_value < SCORE_DIMENSION_MIN or score_value > SCORE_DIMENSION_MAX:
            errors.append(
                f"dimension_scores[{index}].score is outside the allowed scale for {case_name}: "
                f"{score_value}"
            )
            continue
        dimension_scores.append(
            {
                "name": name,
                "score": score_value,
                "rationale": str(raw_score.get("rationale", "")).strip(),
            }
        )

    if not dimension_scores:
        errors.append(f"grader returned no usable dimension_scores for {case_name}")

    computed_overall = sum(score["score"] for score in dimension_scores)
    normalized["checks_passed"] = _normalize_string_list(normalized.get("checks_passed"))
    normalized["checks_failed"] = _normalize_string_list(normalized.get("checks_failed"))
    normalized["failure_categories"] = _normalize_string_list(normalized.get("failure_categories"))
    normalized["matched_fail_triggers"] = sorted(
        set(_normalize_string_list(normalized.get("matched_fail_triggers")))
    )
    normalized["summary"] = str(normalized.get("summary", "")).strip()
    normalized["recommended_smallest_fix"] = str(
        normalized.get("recommended_smallest_fix", "")
    ).strip()
    normalized["dimension_scores"] = dimension_scores

    reported_overall = normalized.get("overall_score")
    if reported_overall is None:
        normalized["reported_overall_score"] = None
    else:
        try:
            normalized["reported_overall_score"] = int(reported_overall)
        except (TypeError, ValueError):
            errors.append(f"overall_score is not numeric for {case_name}: {reported_overall!r}")
            normalized["reported_overall_score"] = reported_overall
        else:
            if normalized["reported_overall_score"] != computed_overall:
                errors.append(
                    f"reported overall_score does not match computed total for {case_name}: "
                    f"{normalized['reported_overall_score']} != {computed_overall}"
                )

    normalized["evaluation_valid"] = not errors
    normalized["grading_errors"] = errors

    if errors:
        normalized["overall_score"] = 0
        return normalized

    normalized["overall_score"] = computed_overall
    return normalized


def _normalize_string_list(raw_value: Any) -> list[str]:
    if raw_value is None:
        return []
    if not isinstance(raw_value, list):
        return [str(raw_value).strip()] if str(raw_value).strip() else []
    normalized = []
    for item in raw_value:
        text = str(item).strip()
        if text:
            normalized.append(text)
    return normalized


def _parse_json_response(text: str) -> dict[str, Any]:
    candidate = text.strip()
    if candidate.startswith("```"):
        candidate = candidate.strip("`")
        first_brace = candidate.find("{")
        last_brace = candidate.rfind("}")
        if first_brace != -1 and last_brace != -1:
            candidate = candidate[first_brace : last_brace + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        first_brace = candidate.find("{")
        last_brace = candidate.rfind("}")
        if first_brace == -1 or last_brace == -1:
            raise
        return json.loads(candidate[first_brace : last_brace + 1])


def _top_items(cases: list[CaseEvaluation], attribute: str) -> list[str]:
    counter: Counter[str] = Counter()
    for case in cases:
        for item in getattr(case, attribute):
            counter[item] += 1
    return [name for name, _count in counter.most_common()]


def _aggregate_verification_state(cases: list[CaseEvaluation]) -> str:
    if any(not case.evaluation_valid for case in cases):
        return "invalid_grading"
    if any(not case.evidence_valid for case in cases):
        return "inconclusive"
    return "verified"


def _build_skill_summary(cases: list[CaseEvaluation], *, verification_state: str) -> str:
    if not cases:
        return "No eval cases were available."

    invalid_cases = [case for case in cases if not case.evaluation_valid]
    if invalid_cases:
        invalid_names = ", ".join(case.case_name for case in invalid_cases)
        return f"Invalid grading output for: {invalid_names}."

    if verification_state == "inconclusive":
        inconclusive_cases = ", ".join(case.case_name for case in cases if not case.evidence_valid)
        return (
            f"Inconclusive verification for: {inconclusive_cases}. "
            "Currentness-sensitive cases did not record enough live research evidence."
        )

    weakest = min(cases, key=lambda case: case.overall_score)
    strongest = max(cases, key=lambda case: case.overall_score)
    categories = _top_items(cases, "failure_categories")[:3]
    category_text = ", ".join(categories) if categories else "no recurring category failures"
    return (
        f"Weakest case: {weakest.case_name} ({weakest.overall_score}). "
        f"Strongest case: {strongest.case_name} ({strongest.overall_score}). "
        f"Recurring failure categories: {category_text}."
    )


def _build_research_trace(case: CaseFile, response: dict[str, Any]) -> ResearchTrace:
    expectation = case.research_expectation
    live_research_expected = expectation != "repo_only"
    successful_source_urls = tuple(sorted(set(response.get("source_urls", ()))))
    attempted_urls = tuple(sorted(set(response.get("attempted_urls", ()))))
    approved_urls = tuple(sorted(set(response.get("approved_urls", ()))))
    tool_names = tuple(sorted(set(response.get("tool_names", ()))))
    read_paths = tuple(sorted(set(response.get("read_paths", ()))))
    shell_commands = tuple(dict.fromkeys(response.get("shell_commands", ())))

    evidence_valid = bool(successful_source_urls) if live_research_expected else True
    verification_state = "verified" if evidence_valid else "inconclusive"

    if live_research_expected:
        summary = (
            f"Expected live research. Recorded {len(attempted_urls)} URL attempts, "
            f"{len(approved_urls)} approved URL accesses, and "
            f"{len(successful_source_urls)} successful source URLs."
        )
    else:
        summary = (
            f"Live research not required. Recorded {len(read_paths)} local reads and "
            f"{len(shell_commands)} shell inspection commands."
        )

    return ResearchTrace(
        expectation=expectation,
        live_research_expected=live_research_expected,
        attempted_urls=attempted_urls,
        approved_urls=approved_urls,
        successful_source_urls=successful_source_urls,
        tool_names=tool_names,
        read_paths=read_paths,
        shell_commands=shell_commands,
        evidence_valid=evidence_valid,
        verification_state=verification_state,
        summary=summary,
    )


def _build_research_trace_summary(cases: list[CaseEvaluation]) -> str:
    if not cases:
        return "No research trace data recorded."

    verified_count = sum(1 for case in cases if case.evidence_valid)
    attempted_urls = sum(len(case.research_trace.attempted_urls) for case in cases)
    approved_urls = sum(len(case.research_trace.approved_urls) for case in cases)
    successful_urls = sum(len(case.research_trace.successful_source_urls) for case in cases)
    return (
        f"Verified evidence for {verified_count}/{len(cases)} cases. "
        f"Recorded {attempted_urls} URL attempts, {approved_urls} approved URL accesses, "
        f"and {successful_urls} successful source URLs."
    )
