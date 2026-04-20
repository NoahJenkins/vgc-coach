---
description: Verify Pokemon Champions format rules, regulation, and legality assumptions.
---

# VGC Format Verifier

Use `$vgc-format-verifier` immediately for this request.

If "$ARGUMENTS" is non-empty, treat it as the user's format or legality check and start there.
If "$ARGUMENTS" is empty, ask only for the missing claim, team assumption, or regulation question needed to verify.

Preserve the skill's contract:

- confirm the active regulation, rules version, and live date context first
- prefer official rules sources over community sources
- separate directly confirmed rules from inference
- use absolute dates when clarifying "current," "today," or regulation windows

Recommended start:

`Use $vgc-format-verifier to confirm this Pokemon Champions format, regulation, or legality claim. $ARGUMENTS`
