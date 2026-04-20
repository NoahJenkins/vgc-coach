---
name: vgc-lead-planner
description: Use when a Pokemon Champions team needs lead plans and preserve targets.
---

# VGC Lead Planner

Turn a team into real opening plans instead of fake full-game scripts.

## Inputs
- full team
- optional target matchups or archetypes
- optional target preserve targets or concerns
- optional open team sheet assumptions

If format is omitted, assume the current Pokemon Champions regulation and say so.

## Output
Return these sections in order:

1. `Team Identity and Default Lead`
2. `Matchup Plans`
3. `Preserve Targets`
4. `Turn-One Priorities`
5. `Common Traps`
6. `Open Questions`

## Workflow
1. Identify what the team is trying to preserve or establish before naming leads.
2. Recommend one default lead that fits the normal game plan.
3. Change leads only when the matchup meaningfully changes the opening incentives.
4. Tie each lead to a concrete first-turn goal: board stabilization, speed control, immediate pressure, or pivot positioning.
5. Name preserve targets explicitly so the plan is not just "bring strong mons."
6. Surface real uncertainty instead of inventing exact lines from thin matchup claims.

## Required behavior
- Read [planning-checklist](../../docs/skills/vgc-lead-planner/references/planning-checklist.md) and [output-rubric](../../docs/skills/vgc-lead-planner/references/output-rubric.md) before finalizing.
- If the prep is opponent-specific and public info exists, use `vgc-opponent-scout` to tighten the matchup branches.
- If a turn-one plan hinges on one speed or survival benchmark, align that point with `vgc-calcs-assistant`.
- Use live verification when the matchup plan depends on current field assumptions.
- Avoid fake certainty, vague first-turn goals, or the same lead into every materially different matchup.
