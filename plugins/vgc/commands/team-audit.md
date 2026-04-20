---
description: Audit a Pokemon Champions team and identify the highest-impact flaws first.
---

# VGC Team Audit

Use `$vgc-team-audit` immediately for this request.

If "$ARGUMENTS" is non-empty, treat it as the user's audit request and start there.
If "$ARGUMENTS" is empty, ask only for the missing team, target concerns, matchup focus, or event context needed to audit.

Preserve the skill's contract:

- findings first, not a compliment sandwich
- tie every issue to a concrete gameplay consequence
- prefer the smallest useful fixes before recommending a rebuild
- verify live-field assumptions when the audit depends on the current meta

Recommended start:

`Use $vgc-team-audit to review this Pokemon Champions team, identify the highest-impact issues first, and recommend the smallest useful changes. $ARGUMENTS`
