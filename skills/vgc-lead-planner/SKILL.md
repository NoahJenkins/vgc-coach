---
name: vgc-lead-planner
description: Use when the user wants matchup-specific opening plans for a Pokemon Champions team, especially to choose default leads, preserve targets, and first-turn priorities without collapsing every pairing into one autopilot line.
---

# VGC Lead Planner

## Overview

Use this skill to turn a team into **real opening plans**.

This is not a flowchart-for-every-turn skill. The goal is to give the player a practical starting map: what to lead most often, what to preserve, what turn-one objective matters, and how those priorities change by matchup.

## Inputs

Accept:

- full team
- optional target matchups or archetypes
- optional target preserve targets or concerns
- optional open team sheet assumptions

If the format is not specified, assume the current Pokemon Champions regulation and state that assumption.

## Output Contract

Always return:

1. `Team Identity and Default Lead`
2. `Matchup Plans`
3. `Preserve Targets`
4. `Turn-One Priorities`
5. `Common Traps`
6. `Open Questions`

## Workflow

1. Identify what the team is actually trying to preserve or set up before naming leads.
2. Recommend one default lead that fits the team's normal game plan.
3. Change leads only when the matchup meaningfully changes the opening incentives.
4. Tie each lead to a concrete first-turn goal such as board stabilization, speed control, immediate pressure, or pivot positioning.
5. Name the preserve targets explicitly so the lead plan is not just "bring strong mons."
6. Surface the real uncertainty instead of inventing exact lines from thin matchup claims.

## Planning Checklist

- Read [references/planning-checklist.md](references/planning-checklist.md) before finalizing the answer.
- If the prep is opponent-specific and public info exists, use `vgc-opponent-scout` to tighten the matchup branches.
- If a turn-one plan hinges on one speed or survival benchmark, align that point with `vgc-calcs-assistant`.
- Check whether the team needs to preserve speed control, weather control, redirection, setup support, or a specific closer.
- Prefer a smaller set of trustworthy lead plans over fake coverage of every possible opposing variation.

## Freshness Policy

- Use live meta verification when the matchup plans depend on current field assumptions.
- If the request is mostly internal team-structure planning, live research can be lighter, but do not present stale matchup claims as current.
- If the metagame is moving fast, say the plans are a current best read rather than a solved script.

## Output Quality Bar

- Read [references/output-rubric.md](references/output-rubric.md) before finalizing the response.
- Keep plans human-usable under tournament or ladder time pressure.
- Explain why the lead changes by matchup instead of only naming pairs.
- Make preserve targets and turn-one objectives explicit.

## Rules

- avoid fake certainty
- show how plans differ by matchup
- prioritize useful practical lines over exhaustive trees
- do not collapse every matchup into one "safe" lead if the team clearly has different incentives

## Common Mistakes

- recommending the same lead into weather, Fake Out, and redirection-heavy matchups with no adjustment
- naming preserve targets too late for the lead advice to be useful
- writing vague priorities like "play carefully" instead of stating the board goal
- pretending an opening is safe without acknowledging obvious opposing punish lines
