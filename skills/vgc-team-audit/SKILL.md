---
name: vgc-team-audit
description: Use when a Pokemon Champions team needs a findings-first audit.
---

# VGC Team Audit

Perform a findings-first competitive audit of a team. Preserve the identity unless the identity itself is the problem.

## Inputs
- full team
- optional target concerns
- optional target matchups
- optional event or ladder context

If format is omitted, assume the current Pokemon Champions regulation and say so.

## Output
Return these sections in order:

1. `Top Findings`
2. `Team Identity`
3. `Matchup Holes`
4. `Recommended Changes`
5. `Residual Risk`

## Section focus
- `Top Findings`: highest-impact structural problems first, with gameplay consequences
- `Team Identity`: what the team is trying to do, and whether that identity is sound or under-supported
- `Matchup Holes`: real pressure points, not generic type-chart recap
- `Recommended Changes`: smallest useful fixes first, each tied to the exact problem solved
- `Residual Risk`: what stays shaky after the proposed changes

## Workflow
1. Identify what the team is trying to do before criticizing it.
2. Separate structural flaws from stylistic differences.
3. Surface the highest-impact issues first.
4. Tie every issue to a concrete gameplay consequence or recurring loss pattern.
5. Recommend the smallest useful fixes before larger rebuilds.
6. Preserve the identity unless the identity itself creates the failure.
7. End with residual risk instead of pretending the team is solved.

## Required behavior
- Read [audit-checklist](../../docs/skills/vgc-team-audit/references/audit-checklist.md) and [output-rubric](../../docs/skills/vgc-team-audit/references/output-rubric.md) before finalizing.
- Use live meta verification when the audit depends on current field assumptions.
- Findings first, not a compliment sandwich.
- Keep fixes concrete, proportional, and identity-preserving when reasonable.
- Do not flatten unconventional teams into generic balance or recommend a major rebuild before proving a smaller fix is insufficient.
