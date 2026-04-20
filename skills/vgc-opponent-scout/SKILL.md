---
name: vgc-opponent-scout
description: Use when public Pokemon Champions info needs an honest opponent scout.
---

# VGC Opponent Scout

Turn public opponent information into actionable prep.

## Inputs
- player names
- public team lists or tournament results
- archetype-based prep requests
- opponent tendencies inferred from public records
- optional team-preview or matchup context from the user side

## Output
Return these sections in order:

1. `Scout Target`
2. `Likely Shells`
3. `Common Techs or Tendencies`
4. `Gameplan Risks`
5. `Prep Adjustments`
6. `Confidence and Sources`

## Workflow
1. Lock what the user actually has: public results, public teams, archetype clues, or pure format tendencies.
2. Separate confirmed public info from extrapolation.
3. Build the scout around the most likely shells and the few techs that materially change prep.
4. Translate the scout into preview, lead-select, or preserve risks the user can act on.
5. If the read is thin, keep the advice broad and say so directly.
6. Never imply private scouting access or exact closed-team certainty.

## Required behavior
- Read [scouting-checklist](../../docs/skills/vgc-opponent-scout/references/scouting-checklist.md) and [output-rubric](../../docs/skills/vgc-opponent-scout/references/output-rubric.md) before finalizing.
- Use `vgc-source-verifier` discipline whenever a tendency claim is weakly evidenced.
- If a prep point turns on one speed or survival check, point toward `vgc-calcs-assistant`.
- If the scout should flow into lead prep, keep the handoff clean for `vgc-lead-planner`.
- Do not invent private info, hide low confidence, or list generic techs without saying which ones matter.
