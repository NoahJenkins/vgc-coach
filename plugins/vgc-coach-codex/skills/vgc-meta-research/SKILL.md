---
name: vgc-meta-research
description: Use when a user wants a live Pokemon Champions meta snapshot.
---

# VGC Meta Research

Produce a current, source-backed view of the active Pokemon Champions format.

## Inputs
- regulation or format request
- optional target mon
- optional archetype
- optional event lens

If format is omitted, default to the current Pokemon Champions regulation and say so.

## Output
Return these sections in order:

1. `Format Check`
2. `Meta Snapshot`
3. `Popular Teams and Cores`
4. `Strategic Trends`
5. `Anti-Meta Openings`
6. `Sources`

## Workflow
1. Confirm the active format, legal mechanics, and relevant date.
2. Browse live sources before making any current-meta claim.
3. Separate official format truth from community meta interpretation.
4. Summarize what is popular now, not old Scarlet/Violet VGC assumptions.
5. Call out uncertainty when data is thin, conflicting, or very new.
6. Give anti-meta takeaways that are actually usable in team building or prep.

## Required behavior
- Read [source-policy](../../docs/skills/vgc-meta-research/references/source-policy.md), [current-source-map](../../docs/skills/vgc-meta-research/references/current-source-map.md), and [output-rubric](../../docs/skills/vgc-meta-research/references/output-rubric.md) before finalizing.
- If the real question is whether the format or legality assumption is current, align with `vgc-format-verifier` first.
- If a trend claim feels weak or overstated, use `vgc-source-verifier` discipline before repeating it.
- Use community sources for usage and trends only after format legality is locked.
- Use absolute dates, label early-meta guidance clearly, and do not invent usage numbers, placements, or cores.
