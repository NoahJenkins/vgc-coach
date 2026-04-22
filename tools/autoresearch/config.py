from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Literal

LiveResearchPolicy = Literal["off", "conditional", "required"]
RunProfile = Literal["daily_sentinel", "manual"]

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT_ROOT = REPO_ROOT / ".artifacts" / "autoresearch"

PRIORITY_SKILLS: tuple[str, ...] = (
    "vgc-meta-research",
    "vgc-team-builder",
    "vgc-team-audit",
    "vgc-lead-planner",
    "vgc-battle-review",
)

PRIORITY_SENTINEL_CASES: dict[str, str] = {
    "vgc-meta-research": "case-01",
    "vgc-team-builder": "case-04",
    "vgc-team-audit": "case-01",
    "vgc-lead-planner": "case-02",
    "vgc-battle-review": "case-02",
}


@dataclass(frozen=True)
class SkillConfig:
    name: str
    fixture_slug: str
    live_research_policy: LiveResearchPolicy
    sentinel_case_name: str | None = None

    @property
    def skill_file(self) -> Path:
        return REPO_ROOT / "skills" / self.name / "SKILL.md"

    @property
    def docs_dir(self) -> Path:
        return REPO_ROOT / "docs" / "skills" / self.name

    @property
    def fixture_dir(self) -> Path:
        return REPO_ROOT / "data" / "fixtures" / "evals" / self.fixture_slug

    @property
    def rubric_file(self) -> Path:
        return REPO_ROOT / "data" / "rubrics" / f"{self.fixture_slug}-rubric.md"


def _skill(name: str, live_research_policy: LiveResearchPolicy) -> SkillConfig:
    return SkillConfig(
        name=name,
        fixture_slug=name.removeprefix("vgc-"),
        live_research_policy=live_research_policy,
        sentinel_case_name=PRIORITY_SENTINEL_CASES.get(name),
    )


SKILL_CONFIGS: dict[str, SkillConfig] = {
    "vgc-meta-research": _skill("vgc-meta-research", "required"),
    "vgc-team-builder": _skill("vgc-team-builder", "conditional"),
    "vgc-team-audit": _skill("vgc-team-audit", "conditional"),
    "vgc-lead-planner": _skill("vgc-lead-planner", "conditional"),
    "vgc-battle-review": _skill("vgc-battle-review", "conditional"),
    "vgc-format-verifier": _skill("vgc-format-verifier", "required"),
    "vgc-source-verifier": _skill("vgc-source-verifier", "required"),
    "vgc-calcs-assistant": _skill("vgc-calcs-assistant", "off"),
    "vgc-opponent-scout": _skill("vgc-opponent-scout", "conditional"),
    "vgc-practice-journal": _skill("vgc-practice-journal", "off"),
}


def parse_run_date(raw_date: str | None) -> date:
    if not raw_date:
        return datetime.now().date()
    return date.fromisoformat(raw_date)


def get_skill_config(skill_name: str) -> SkillConfig:
    try:
        return SKILL_CONFIGS[skill_name]
    except KeyError as exc:
        known = ", ".join(sorted(SKILL_CONFIGS))
        raise ValueError(f"Unknown skill '{skill_name}'. Known skills: {known}") from exc


def choose_skill(skill_name: str | None, run_date: date) -> SkillConfig:
    if skill_name and skill_name != "auto":
        return get_skill_config(skill_name)

    epoch = date(2026, 1, 1)
    index = (run_date - epoch).days % len(PRIORITY_SKILLS)
    return get_skill_config(PRIORITY_SKILLS[index])
