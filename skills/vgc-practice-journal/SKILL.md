---
name: vgc-practice-journal
description: Use when Pokemon Champions session notes need a concise practice journal.
---

# VGC Practice Journal

Convert messy testing notes into a repeatable improvement loop.

## Inputs
- ladder session notes
- testing-block recaps
- scrim summaries
- repeated review findings
- optional target skill or matchup focus

## Output
Return these sections in order:

1. `Session Goal`
2. `What Happened`
3. `Repeated Patterns`
4. `Keep`
5. `Change Next Session`
6. `Follow-Up Questions`

## Workflow
1. Identify what the user was trying to improve during the session.
2. Compress the session into a short factual recap rather than a blow-by-blow log.
3. Extract repeated patterns across games, not one-off emotional reactions.
4. Separate what should be preserved from what should change.
5. Turn the next session into a small number of testable adjustments.
6. If one game needs deeper diagnosis, point toward `vgc-battle-review`.

## Required behavior
- Read [journaling-checklist](../../docs/skills/vgc-practice-journal/references/journaling-checklist.md) and [output-rubric](../../docs/skills/vgc-practice-journal/references/output-rubric.md) before finalizing.
- Favor recurring patterns over isolated frustration.
- Keep `Keep` and `Change Next Session` concrete enough to test.
- If a repeated issue depends on prep assumptions, hand off toward `vgc-opponent-scout` or `vgc-calcs-assistant`.
- Do not turn the journal into a turn-by-turn review, one-game tilt report, or vague "practice more" recap.
