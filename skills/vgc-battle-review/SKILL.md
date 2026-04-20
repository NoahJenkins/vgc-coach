---
name: vgc-battle-review
description: Use when the user wants a competitive review of a Pokemon Champions battle, replay, log, or turn summary, especially to separate actual mistakes from variance and turn the game into concrete future prep.
---

# VGC Battle Review

## Overview

Use this skill to turn a battle into **actionable review**, not hindsight theater.

The goal is to identify the real swing turns, separate sequencing or planning mistakes from ordinary variance, and translate the review into something the player can use in future prep or games.

## Inputs

Accept:

- replay summaries
- logs
- turn-by-turn notes
- post-game self-reflections
- optional review goal
- optional player-side context

If the format is not specified, assume the current Pokemon Champions regulation and state that assumption.

## Output Contract

Always return:

1. `Review Goal and Match Context`
2. `Key Turning Points`
3. `Actual Mistakes vs Variance`
4. `Stronger Alternative Lines`
5. `Prep and Practice Implications`
6. `Open Questions`

## Workflow

1. Identify what the player was trying to accomplish before judging the result.
2. Find the real decision points instead of narrating every turn equally.
3. Separate information the player reasonably had at the time from hindsight-only knowledge.
4. Distinguish bad sequencing, bad planning, and acceptable low-roll outcomes.
5. Offer stronger alternative lines that are realistic from the actual board state.
6. End with what the player should change in prep, habits, or team assumptions next time.

## Review Checklist

- Read [references/review-checklist.md](references/review-checklist.md) before finalizing the answer.
- If a turning point depends on one benchmark question, call out the calc uncertainty cleanly for `vgc-calcs-assistant`.
- If the loss exposed a repeatable prep pattern across multiple games, leave a clean handoff for `vgc-practice-journal`.
- If opponent prep or public tendencies were part of the miss, point toward `vgc-opponent-scout`.
- Check whether the loss came from lead plan, preserve logic, sequencing, positioning, damage assumptions, or matchup misunderstanding.
- Prefer a small number of high-signal findings over a turn-by-turn recap with no prioritization.

## Freshness Policy

- Use live meta verification when the review depends on current format assumptions or matchup positioning.
- If the review is mostly about board sequencing or decision quality, live research can be lighter, but do not present stale matchup claims as current.

## Output Quality Bar

- Read [references/output-rubric.md](references/output-rubric.md) before finalizing the answer.
- Keep the review concrete enough that a competitive player could act on it immediately.
- Do not relabel unavoidable bad outcomes as mistakes.
- Tie the review back to future prep, not just past blame.

## Rules

- do not call every loss a misplay
- identify the decision point, not just the bad result
- tie review output back to future prep

## Common Mistakes

- recapping every turn without deciding which turn actually mattered
- judging lines with hindsight that was not available in game
- calling variance a misplay because the result was bad
- offering alternative lines that ignore the real board state or player goal
