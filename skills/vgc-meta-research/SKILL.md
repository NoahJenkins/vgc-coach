---
name: vgc-meta-research
description: Use when the user needs a current Pokemon Champions metagame summary, confirmation of what is popular in the active regulation, anti-meta opportunities, or source-backed guidance about teams, cores, and strategic trends.
---

# VGC Meta Research

## Overview

Use this skill to produce a **current, source-backed** view of the active Pokemon Champions format.

This is a live-research skill, not an offline knowledge dump. For current rules, current popularity, or "what's good right now," verify live first and keep the answer anchored to the active regulation.

## Inputs

Accept:

- regulation or format request
- optional target mon
- optional archetype
- optional event lens

If the user does not specify a format, default to the **current Pokemon Champions regulation** and state that assumption.

## Output Contract

Always return these sections in this order:

1. `Format Check`
2. `Meta Snapshot`
3. `Popular Teams and Cores`
4. `Strategic Trends`
5. `Anti-Meta Openings`
6. `Sources`

Keep the sections concise, but do not skip them.

## Workflow

1. Confirm the active format, legal mechanics, and relevant date.
2. Browse live sources before making any current-meta claim.
3. Separate official format truth from community meta interpretation.
4. Summarize what is popular now, not what was popular in old Scarlet/Violet VGC.
5. Call out uncertainty when data is thin, conflicting, or very new.
6. Give anti-meta takeaways that are actually usable in team building or prep.

## Source Policy

- Read [references/source-policy.md](references/source-policy.md) before summarizing the live format.
- Read [references/current-source-map.md](references/current-source-map.md) when deciding which live sources to consult first.
- Prefer official rules and event-policy sources over all community sources.
- Use community sources for usage, teams, and trends after format legality is locked.
- If sources conflict, say so explicitly instead of averaging them into fake certainty.

## Freshness Policy

- Treat current-format questions as freshness-sensitive by default.
- Use absolute dates when clarifying "current," "now," or "today."
- If live sources are thin or early, label the answer as early-meta guidance rather than settled truth.

## Output Quality Bar

- Read [references/output-rubric.md](references/output-rubric.md) when tightening the final answer.
- Use the dated snapshot in `data/snapshots/` only as a support artifact or fallback, not as a replacement for live verification.
- Distinguish sourced fact from inference.
- Do not invent usage percentages, placements, or cores.
- Do not carry forward stale SV-era assumptions into Champions.

## Common Mistakes

- Answering from memory when the user asked about the current meta.
- Treating inactive mechanics as live.
- Presenting community usage sites as legality authorities.
- Giving anti-meta ideas without explaining what they punish.
