---
description: Plan default and matchup-specific leads for a Pokemon Champions team.
---

# VGC Lead Planner

Use `$vgc-lead-planner` immediately for this request.

If "$ARGUMENTS" is non-empty, treat it as the user's lead-planning request and start there.
If "$ARGUMENTS" is empty, ask only for the missing team, matchup targets, preserve targets, or open-team-sheet assumptions needed to proceed.

Preserve the skill's contract:

- recommend one default lead that matches the actual team identity
- change leads only when the matchup materially changes opening incentives
- tie each lead to concrete first-turn goals and preserve targets
- verify live-field assumptions when matchup planning depends on the current format

Recommended start:

`Use $vgc-lead-planner to generate lead plans, preserve targets, and first-turn goals for this Pokemon Champions team. $ARGUMENTS`
