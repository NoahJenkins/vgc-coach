---
name: vgc-team-audit
description: Use when the user wants a competitive review of a Pokemon Champions team, especially to find structural weaknesses, matchup holes, role overlap, or the smallest high-impact changes that improve the team without losing its identity.
---

# VGC Team Audit

## Overview

Use this skill to perform a **findings-first competitive audit** of a team.

This is not a rewrite-everything skill by default. Start by understanding what the team is trying to be, then identify the real structural issues and the smallest changes that improve it. Preserve the identity unless the identity itself is the problem.

## Inputs

Accept:

- full team
- optional target concerns
- optional target matchups
- optional event or ladder context

If the format is not specified, assume the current Pokemon Champions regulation and state that verified assumption.

## Output Contract

Always return these sections in this order:

1. `Top Findings`
2. `Team Identity`
3. `Matchup Holes`
4. `Recommended Changes`
5. `Residual Risk`

## Section Requirements

### `Top Findings`

List the highest-impact issues first. Each finding should name the structural problem and the concrete gameplay consequence. Do not open with filler praise.

### `Team Identity`

State what the team is trying to do before judging it. Make clear whether the identity is sound but under-supported, or whether the identity itself is creating the failure.

### `Matchup Holes`

Call out the real pressure points for the team, not a generic type-chart recap. Tie the holes to preview pressure, speed control, positioning, preserve logic, or set tension when relevant.

### `Recommended Changes`

Recommend the smallest useful changes first. For each change, explain the exact problem it solves and why it is proportional to the issue. Do not jump to a full rebuild unless the identity itself is the problem.

### `Residual Risk`

State what would still be shaky after the recommended changes. This is where unresolved matchup risk, structural limits, or larger future rebuild ideas belong.

## Workflow

1. Identify what the team is trying to do before criticizing it.
2. Separate structural flaws from stylistic differences before deciding what is actually broken.
3. Surface the highest-impact issues first.
4. Tie each issue to a concrete gameplay consequence or recurring matchup loss.
5. Recommend the smallest useful fixes before proposing larger rebuilds.
6. Preserve the team identity unless the identity itself creates the failure, and say that plainly when it does.
7. End with residual risk instead of pretending the team is solved.

## Audit Checklist

- Read [references/audit-checklist.md](references/audit-checklist.md) before finalizing the findings.
- Check structure, tempo, speed control, positioning, damage profile, and common matchup pressure.
- Ask whether the real weakness shows up in preview, lead pressure, midgame positioning, preserve logic, or set tension.
- Focus on actionable weaknesses, not aesthetic preferences.
- Prefer a small number of high-signal findings over a long generic audit.

## Freshness Policy

- Use live meta verification when the audit depends on current field assumptions.
- If the audit is mostly internal team structure, live research may be lighter, but do not assume stale meta matchups.

## Output Quality Bar

- Read [references/output-rubric.md](references/output-rubric.md) when tightening the answer.
- Findings first.
- No filler praise before the real issues.
- Keep fixes concrete and proportional.
- Separate "weird" from "broken."
- Explain why each change matters in actual games.

## Rules

- findings first, not a compliment sandwich
- preserve identity when reasonable
- recommend the smallest useful changes first
- tie every recommendation to a gameplay consequence
- do not flatten unconventional teams into generic balance by default

## Common Mistakes

- flattening every team into the same safe balance shell
- confusing unusual with bad
- giving generic synergy comments instead of identifying real losses
- recommending major rebuilds when one smaller change would solve the problem
