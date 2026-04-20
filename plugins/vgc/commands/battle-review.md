---
description: Review a Pokemon Champions battle for real mistakes and better lines.
---

# VGC Battle Review

Use `$vgc-battle-review` immediately for this request.

If "$ARGUMENTS" is non-empty, treat it as the user's replay-review request and start there.
If "$ARGUMENTS" is empty, ask only for the missing replay summary, log, turn notes, or review goal needed to proceed.

Preserve the skill's contract:

- focus on the true swing turns instead of narrating every turn equally
- separate actual mistakes from acceptable losing lines and variance
- avoid hindsight-only criticism and impossible alternative lines
- verify live matchup assumptions when the review depends on the current field

Recommended start:

`Use $vgc-battle-review to review this Pokemon Champions battle and identify key decision points, better lines, and future prep implications. $ARGUMENTS`
