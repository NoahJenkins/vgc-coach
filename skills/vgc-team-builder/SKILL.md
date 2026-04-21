---
name: vgc-team-builder
description: Use when building one practical Pokemon Champions team around a target idea.
---

# VGC Team Builder

Build one practical recommended team around a real user goal. Commit to one primary draft and stay honest when the ask is weak.

## Inputs
- target mons
- target strategy or archetype
- playstyle preference
- anti-meta goals
- avoid list
- optional event or ladder context

If format is omitted, assume the current Pokemon Champions regulation, verify it when current-context claims matter, and say so.

## Output
Return these sections in order:

1. `Build Goal` - objective, format basis, and `current-field recommendation` or `inference-heavy early read`
2. `Recommended Team` - one six-mon draft only
3. `Role Map` - win path, speed or tempo control, board control, closer logic
4. `Set Direction` - lightweight role, item, move, and mechanics-aware direction for each slot
5. `Why Each Slot Exists` - job, team fit, and what each slot solves
6. `Matchup Notes` - pressure points this shell is built to handle
7. `Weaknesses and Next Refinements` - unresolved issues and optional future tuning only

## Workflow
1. Lock the active format and major meta pressures first.
2. Align with `vgc-format-verifier` if legality or rules gate the build.
3. Identify the real build goal behind the request before choosing slots.
4. Build around one clear team identity.
5. Keep the requested idea only when it still supports that identity.
6. If the ask is weak, say so plainly and pivot to the nearest viable version that preserves the goal.
7. Give lightweight set direction so the draft is testable immediately.
8. If a current-field positioning claim is thin, apply `vgc-source-verifier` discipline instead of overselling it.
9. End with real weaknesses instead of pretending the build is solved.

## Required behavior
- Read [build-principles](../../docs/skills/vgc-team-builder/references/build-principles.md) and [output-rubric](../../docs/skills/vgc-team-builder/references/output-rubric.md) before finalizing.
- Read [Champions Reg M-A legality](../../docs/skills/shared/references/champions-reg-m-a-legality.md) before finalizing current-format Champions builds.
- Use live verification by default when current meta context materially affects the build.
- Keep optional swaps only in `Weaknesses and Next Refinements`.
- Explain how all six slots support the same plan.
- If the active regulation does not have `Terastallization` active, do not give Tera recommendations.
- If a specific held item is not currently verified as legal, do not present it as confirmed legal; either use a verified legal item or label the item direction as unverified.
- Do not give multiple half-committed drafts, hide a bad requested mon, or turn the refinement section into a second team.
