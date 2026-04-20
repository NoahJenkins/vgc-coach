---
name: vgc-source-verifier
description: Use when a Pokemon Champions claim needs a source audit.
---

# VGC Source Verifier

Judge whether a claim is actually supported by the cited material.

## Inputs
- source-backed claims from chat, notes, or draft answers
- citations the user wants checked
- "is this actually supported?" requests
- suspicious meta, matchup, or rules claims that may overreach the evidence

## Output
Return these sections in order:

1. `Claim Under Review`
2. `Source Verdict`
3. `What Is Confirmed`
4. `What Remains Inference`
5. `Trust Notes`
6. `Sources`

`Source Verdict` should classify the claim as `supported`, `partially supported`, `stale`, `conflicted`, or `unsupported`.

## Workflow
1. Rewrite the claim into a testable sentence before reading the sources.
2. Check whether the cited material directly supports that sentence, only supports part of it, or supports something weaker.
3. Separate factual support from the answer writer's interpretation.
4. Penalize stale timing, weak source rank, missing dates, and source-to-claim drift.
5. If the claim depends on current format truth, line that up with `vgc-format-verifier` rather than guessing.
6. End with what the sources justify saying right now and what they do not.

## Required behavior
- Read [source-review-checklist](../../docs/skills/vgc-source-verifier/references/source-review-checklist.md) and [output-rubric](../../docs/skills/vgc-source-verifier/references/output-rubric.md) before finalizing.
- Prefer official sources for rules claims and dated community sources for usage or trend claims.
- If a source only implies the claim, keep that in `What Remains Inference`, not `What Is Confirmed`.
- Use absolute dates when freshness affects safety, and say when sources conflict.
- Do not upgrade weak evidence into certainty or quote a source without checking whether it proves the actual claim.
