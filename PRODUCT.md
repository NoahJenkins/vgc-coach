---
name: VGC Coach
register: brand
audience:
  primary: Competitive Pokemon Champions players preparing for current-format VGC play.
  secondary: Developers and contributors improving shared coaching skills, evals, and runtime adapters.
purpose: Open-source coaching workspace for practical, source-aware Pokemon Champions prep.
tone: Practical, strategic, competitive, clear, and source-aware.
---

# Product Context: VGC Coach

VGC Coach is a shared VGC coaching skill-and-eval workspace for Pokemon Champions. The repo is for building, testing, and hardening reusable coaching skills, supported by fixed eval cases, rubrics, runtime adapters, and thin discovery wrappers.

The public website should primarily help players understand what the workspace does: build teams, check the current meta, plan leads, review games, and judge whether AI-generated advice is trustworthy. Developers and contributors are secondary; contributor architecture can appear, but player clarity comes first.

## Product Direction

Optimize for current-format research accuracy, practical team-building help, matchup and lead planning, replay-based feedback loops, and disciplined evaluation of skill quality.

Do not optimize for verbose but weak advice, stale meta claims presented as current, fake legality or matchup certainty, or runtime-specific rewrites of the same coaching logic.

## Brand Personality

VGC Coach should feel practical, strategic, and competitive. Confidence should come from useful specificity, not hype. The interface and copy should make the project feel like a disciplined prep tool that helps players make better decisions under current-format constraints.

## Site Principles

- Prioritize player tasks over contributor architecture when shaping the homepage.
- Make source accuracy, legality, uncertainty, fixed test cases, and rubrics visible without turning the page into documentation.
- Preserve repo-aligned language: open-source coaching workspace, shared coaching logic, current format rules, fixed test cases and rubrics, and support tools.
- Avoid generic AI-product hype and vague productivity claims.
- Support light and dark mode as first-class visual surfaces.

## Canonical Concepts

- `skills/` is the canonical editable source for shared coaching behavior.
- Runtime-specific layers should stay thin and point back to shared skill packages.
- `vgc-meta-research`, `vgc-team-builder`, `vgc-team-audit`, `vgc-lead-planner`, and `vgc-battle-review` are the core MVP skills.
- Current-format, legality, meta, matchup, usage, and calc claims must be verified before being presented as current truth.
