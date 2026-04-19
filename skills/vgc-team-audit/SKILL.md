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

If the format is not specified, assume the current Pokemon Champions regulation and state that assumption.

## Output Contract

Always return these sections in this order:

1. `Top Findings`
2. `Team Identity`
3. `Matchup Holes`
4. `Recommended Changes`
5. `Residual Risk`

## Workflow

1. Identify what the team is trying to do before criticizing it.
2. Surface the highest-impact issues first.
3. Tie each issue to a concrete gameplay consequence.
4. Recommend the smallest useful fixes before proposing larger rebuilds.
5. Preserve the team identity unless the identity itself creates the failure.

## Audit Checklist

- Read [references/audit-checklist.md](references/audit-checklist.md) before finalizing the findings.
- Check structure, tempo, speed control, positioning, damage profile, and common matchup pressure.
- Focus on actionable weaknesses, not aesthetic preferences.

## Freshness Policy

- Use live meta verification when the audit depends on current field assumptions.
- If the audit is mostly internal team structure, live research may be lighter, but do not assume stale meta matchups.

## Output Quality Bar

- Read [references/output-rubric.md](references/output-rubric.md) when tightening the answer.
- Findings first.
- No filler praise before the real issues.
- Keep fixes concrete and proportional.

## Common Mistakes

- flattening every team into the same safe balance shell
- confusing unusual with bad
- giving generic synergy comments instead of identifying real losses
- recommending major rebuilds when one smaller change would solve the problem
