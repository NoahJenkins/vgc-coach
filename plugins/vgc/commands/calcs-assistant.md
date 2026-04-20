---
description: Turn Pokemon Champions damage and speed checks into actionable prep decisions.
---

# VGC Calcs Assistant

Use `$vgc-calcs-assistant` immediately for this request.

If "$ARGUMENTS" is non-empty, treat it as the user's calc or benchmark question and start there.
If "$ARGUMENTS" is empty, ask only for the missing species, benchmark, field state, or decision context needed to proceed.

Preserve the skill's contract:

- define the real decision before discussing numbers
- keep exact claims tied to explicit assumptions
- switch to honest benchmark framing when key inputs are missing
- explain the gameplay impact instead of dumping irrelevant damage tables

Recommended start:

`Use $vgc-calcs-assistant to reason through this Pokemon Champions calc question and explain the decision impact honestly. $ARGUMENTS`
