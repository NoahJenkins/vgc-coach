---
name: vgc-opponent-scout
description: Use when the user wants honest prep notes on a Pokemon Champions opponent, public team trail, or archetype tendency and needs likely reads, common techs, and prep risks without inventing unsupported specifics.
---

# VGC Opponent Scout

## Overview

Use this skill to turn **public opponent information into actionable prep**.

The job is to describe likely shells, reasonable tech expectations, and the real gameplan risks while staying explicit about what is actually known and what is only a low-confidence read.

## Inputs

Accept:

- player names
- public team lists or tournament results
- archetype-based prep requests
- opponent tendencies inferred from public records
- optional team-preview or matchup context from the user side

## Output Contract

Always return these sections in this order:

1. `Scout Target`
2. `Likely Shells`
3. `Common Techs or Tendencies`
4. `Gameplan Risks`
5. `Prep Adjustments`
6. `Confidence and Sources`

## Workflow

1. Lock what the user actually has access to: public results, public teams, archetype clues, or pure format tendencies.
2. Separate confirmed public info from reasonable extrapolation.
3. Build the scout around the most likely shells and the few techs that meaningfully change prep.
4. Translate the scout into risks the user can act on at preview, lead select, or preserve planning.
5. If the read is thin, keep the advice broad and say so directly.
6. Never imply private scouting access or exact closed-team certainty.

## Scout Checklist

- Read [references/scouting-checklist.md](references/scouting-checklist.md) before finalizing the answer.
- Use `vgc-source-verifier` discipline whenever a tendency claim is weakly evidenced.
- If a prep point turns on one speed or survival check, point toward `vgc-calcs-assistant` instead of bluffing.
- If the scout should flow into lead prep, keep the handoff clean for `vgc-lead-planner`.

## Output Quality Bar

- Read [references/output-rubric.md](references/output-rubric.md) when tightening the response.
- Keep the scout focused on the few patterns that change prep.
- Be explicit about confidence level and why.
- Translate tendencies into usable prep adjustments, not trivia.

## Rules

- do not invent private or exact closed-team information
- separate confirmed public info from extrapolated reads
- keep prep adjustments tied to the likely shells and techs you named
- label low-confidence scouting plainly

## Common Mistakes

- presenting archetype guesses as confirmed opponent info
- listing many generic techs without saying which are most relevant
- giving prep advice untethered to the stated confidence level
- implying private team-sheet knowledge from thin public evidence
