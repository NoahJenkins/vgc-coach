---
description: Check whether a Pokemon Champions claim is actually supported by its sources.
---

# VGC Source Verifier

Use `$vgc-source-verifier` immediately for this request.

If "$ARGUMENTS" is non-empty, treat it as the user's claim-audit request and start there.
If "$ARGUMENTS" is empty, ask only for the missing claim or source set needed to perform the audit.

Preserve the skill's contract:

- rewrite the claim into a testable sentence before checking sources
- separate what the sources confirm from what remains inference
- penalize stale timing, weak source rank, and source-to-claim drift
- do not upgrade weak evidence into certainty

Recommended start:

`Use $vgc-source-verifier to review this Pokemon Champions claim and judge whether the sources actually support it. $ARGUMENTS`
