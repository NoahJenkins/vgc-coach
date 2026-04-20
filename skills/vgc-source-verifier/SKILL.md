---
name: vgc-source-verifier
description: Use when a Pokemon Champions claim about rules, usage, matchup trends, or team positioning needs a direct source audit to decide whether it is confirmed, partially supported, stale, or still inference.
---

# VGC Source Verifier

## Overview

Use this skill to judge whether a **claim is actually supported by the cited material**.

This is not a meta-summary skill. It is a claim-audit skill for checking whether the sources really say what the answer is about to claim.

## Inputs

Accept:

- source-backed claims from chat, notes, or draft answers
- citations the user wants checked
- "is this actually supported?" requests
- suspicious meta, matchup, or rules claims that may overreach the evidence

## Output Contract

Always return these sections in this order:

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

## Verification Checklist

- Read [references/source-review-checklist.md](references/source-review-checklist.md) before finalizing the answer.
- Prefer official sources for rules claims and dated community sources for usage or team-trend claims.
- If a source only implies the claim, put that in `What Remains Inference`, not `What Is Confirmed`.

## Freshness Policy

- Stale evidence counts against claim strength even if the source was once credible.
- Use absolute dates when freshness affects whether a claim is still safe.
- If sources conflict, say so directly instead of averaging them into a fake consensus.

## Output Quality Bar

- Read [references/output-rubric.md](references/output-rubric.md) when tightening the answer.
- Audit the claim, not the author's intentions.
- Be specific about why a source is weak, stale, partial, or misapplied.
- Keep the result usable for the next answer writer.

## Rules

- state the claim being tested in one sentence
- judge the support strength directly
- separate confirmed text from interpretation
- mark stale or low-rank sources explicitly
- do not upgrade weak evidence into certainty

## Common Mistakes

- quoting a source without checking whether it proves the actual claim
- hiding stale evidence behind present-tense language
- treating trend interpretation as if it were directly sourced fact
- skipping source-rank discussion when the evidence is thin
