---
name: vgc-practice-journal
description: Use when the user wants to turn Pokemon Champions ladder games, test sessions, scrims, or review notes into a concise practice journal with repeated patterns, things to keep, and concrete next-session adjustments.
---

# VGC Practice Journal

## Overview

Use this skill to convert **messy testing notes into a repeatable improvement loop**.

This is not a single-game battle review replacement. It is for aggregating a practice block, identifying recurring patterns, preserving what is working, and deciding what to change next session.

## Inputs

Accept:

- ladder session notes
- testing-block recaps
- scrim summaries
- repeated review findings
- optional target skill or matchup focus

## Output Contract

Always return these sections in this order:

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
4. Separate what should be preserved from what should be changed.
5. Turn the next session into a small number of testable adjustments.
6. If one game deserves deeper diagnosis, point toward `vgc-battle-review` instead of overloading the journal.

## Journal Checklist

- Read [references/journaling-checklist.md](references/journaling-checklist.md) before finalizing the answer.
- Favor recurring patterns over isolated frustration.
- Keep `Keep` and `Change Next Session` concrete enough to test.
- If a repeated issue depends on prep assumptions, hand off toward `vgc-opponent-scout` or `vgc-calcs-assistant` explicitly.

## Output Quality Bar

- Read [references/output-rubric.md](references/output-rubric.md) when tightening the answer.
- Keep the recap short and the adjustment list usable.
- Preserve successful patterns instead of making every journal a list of failures.
- End with follow-up questions that sharpen the next session.

## Rules

- do not turn a journal into a turn-by-turn battle review
- focus on repeated patterns, not one-off tilt
- keep next-session changes testable
- preserve what is working, not just what is failing

## Common Mistakes

- writing a vague diary instead of extracting patterns
- treating one bad game as a recurring trend
- listing problems without deciding what to keep
- ending with generic "practice more" guidance
