---
name: vgc-battle-review
description: Use when reviewing a Pokemon Champions replay for mistakes and better lines.
---

# VGC Battle Review

Turn a battle into actionable review instead of hindsight theater.

## Inputs
- replay summaries
- logs
- turn-by-turn notes
- post-game self-reflections
- optional review goal
- optional player-side context

If format is omitted, assume the current Pokemon Champions regulation and say so.

## Output
Return these sections in order:

1. `Review Goal and Match Context`
2. `Key Turning Points`
3. `Actual Mistakes vs Variance`
4. `Stronger Alternative Lines`
5. `Prep and Practice Implications`
6. `Open Questions`

## Workflow
1. Identify the player's likely plan before judging the result.
2. Focus on the real swing turns instead of narrating every turn equally.
3. Separate information the player had in game from hindsight-only knowledge.
4. Distinguish sequencing or planning mistakes from acceptable losing lines and variance.
5. Offer alternative lines that were realistic from the actual board state.
6. End with what should change in prep, habits, or team assumptions next time.

## Required behavior
- Read [review-checklist](../../docs/skills/vgc-battle-review/references/review-checklist.md) and [output-rubric](../../docs/skills/vgc-battle-review/references/output-rubric.md) before finalizing.
- If a turning point depends on one benchmark, hand that point to `vgc-calcs-assistant`.
- If the loss exposes a repeatable prep pattern, leave a clean handoff for `vgc-practice-journal`.
- If public opponent tendencies mattered, point toward `vgc-opponent-scout`.
- Use live meta verification when the review depends on current matchup assumptions.
- Do not call every loss a misplay, judge with unavailable hindsight, or offer impossible alternative lines.
