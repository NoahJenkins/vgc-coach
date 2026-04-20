---
name: vgc-format-verifier
description: Use when the user needs to confirm a current Pokemon Champions format, regulation, legality assumption, or rules claim before giving meta, team-building, scouting, or matchup advice.
---

# VGC Format Verifier

## Overview

Use this skill to lock the **actual rules context** before higher-level coaching starts.

This skill is for format truth: active regulation, rules version, legal mechanics, legal roster assumptions, and whether a requested claim is actually safe to build on.

## Inputs

Accept:

- regulation or format questions
- legality checks for mons, mechanics, or team assumptions
- "is this current?" gating requests
- requests that depend on which rules window is active

If the user does not specify a format, default to the **current Pokemon Champions doubles regulation** and verify it before answering.

## Output Contract

Always return these sections in this order:

1. `Requested Check`
2. `Verified Format State`
3. `Legality Notes`
4. `Confidence and Gaps`
5. `Sources`

Keep the answer concise, but do not skip a section.

## Workflow

1. Identify the exact claim that needs to be checked before reviewing sources.
2. Confirm the active regulation, rules version, and live date context first.
3. Prefer official format and policy sources over all community sources.
4. Separate directly confirmed rules from reasonable inference.
5. State when the request cannot be answered cleanly from the available official materials.
6. End with whether downstream coaching can safely proceed on the verified rules state.

## Verification Checklist

- Read [references/format-checklist.md](references/format-checklist.md) before finalizing the answer.
- Use `data/snapshots/` only as support or fallback context, not as a replacement for live verification on freshness-sensitive requests.
- If the rules question is actually about source trust rather than format truth, pair the reasoning with `vgc-source-verifier`.

## Freshness Policy

- Treat format and legality questions as freshness-sensitive by default.
- Use absolute dates when clarifying "current," "today," or "this regulation."
- If official sources lag or conflict, say that plainly instead of filling the gap with community assumptions.

## Output Quality Bar

- Read [references/output-rubric.md](references/output-rubric.md) when tightening the final answer.
- Lead with the check being performed, not a generic rules lecture.
- Make it obvious what is confirmed, what is inferred, and what remains unresolved.
- Do not quietly roll forward with an unverified legality assumption.

## Rules

- verify regulation context before answering legality questions
- prefer official rules sources over all community sources
- separate legality confirmation from meta interpretation
- say when a claim is unsupported instead of smoothing it over

## Common Mistakes

- assuming the latest regulation without checking
- treating usage sites as legality authorities
- answering the meta question while skipping the rules question underneath it
- presenting a partial official source as a full rules confirmation
