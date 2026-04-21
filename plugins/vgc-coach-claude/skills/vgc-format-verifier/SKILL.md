---
name: vgc-format-verifier
description: Use when Pokemon Champions rules or legality must be verified before coaching.
---

# VGC Format Verifier

Lock the actual rules context before higher-level coaching starts.

## Inputs
- regulation or format questions
- legality checks for mons, mechanics, or team assumptions
- "is this current?" gating requests
- requests that depend on which rules window is active

If format is omitted, default to the current Pokemon Champions doubles regulation and verify it before answering.

## Output
Return these sections in order:

1. `Requested Check`
2. `Verified Format State`
3. `Legality Notes`
4. `Confidence and Gaps`
5. `Sources`

## Workflow
1. Identify the exact claim being checked before reading sources.
2. Confirm the active regulation, rules version, and live date context first.
3. Prefer official format and policy sources over all community sources.
4. Separate directly confirmed rules from inference.
5. Say when the available official material is not enough.
6. End with whether downstream coaching can safely proceed.

## Required behavior
- Read [format-checklist](../../docs/skills/vgc-format-verifier/references/format-checklist.md) and [output-rubric](../../docs/skills/vgc-format-verifier/references/output-rubric.md) before finalizing.
- Use `data/snapshots/` only as support or fallback, not as a replacement for live verification on freshness-sensitive requests.
- Use absolute dates when clarifying "current," "today," or "this regulation."
- If the issue is source trust rather than format truth, pair the reasoning with `vgc-source-verifier`.
- Do not treat usage sites as legality authorities or quietly roll forward with an unverified rules assumption.
