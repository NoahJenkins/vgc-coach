---
description: Build one practical Pokemon Champions team around a target idea.
---

# VGC Team Builder

Use `$vgc-team-builder` immediately for this request.

If "$ARGUMENTS" is non-empty, treat it as the user's build brief and start there.
If "$ARGUMENTS" is empty, ask only for the missing target mon, strategy, playstyle preference, anti-meta goal, or avoid list needed to build.

Preserve the skill's contract:

- verify freshness-sensitive format or meta assumptions before presenting them as current
- commit to one coherent primary draft, not multiple half-built options
- keep set direction lightweight but testable
- stay honest when the requested idea is weak instead of forcing fake support

Recommended start:

`Use $vgc-team-builder to build one practical Pokemon Champions team around my target mon, strategy, or anti-meta goal, with one primary draft and lightweight set direction. $ARGUMENTS`
