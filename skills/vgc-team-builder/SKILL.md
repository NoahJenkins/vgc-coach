---
name: vgc-team-builder
description: Use when the user wants a Pokemon Champions team built around target mons, a preferred strategy, or an anti-meta goal, especially when they need one strong recommended draft instead of a loose list of options.
---

# VGC Team Builder

## Overview

Use this skill to build **one practical recommended team** for Pokemon Champions around a real user goal.

This is a recommendation-first skill. It should commit to one primary draft, explain how that team is supposed to function, and stay honest when a requested mon or concept is weak.

## Inputs

Accept:

- target mons
- target strategy or archetype
- playstyle preference
- anti-meta goals
- avoid list
- optional event or ladder context

If the user does not specify format, default to the **current Pokemon Champions regulation** and state that verified assumption.

## Output Contract

Always return these sections in this order:

1. `Build Goal`
2. `Recommended Team`
3. `Role Map`
4. `Set Direction`
5. `Why Each Slot Exists`
6. `Matchup Notes`
7. `Weaknesses and Next Refinements`

## Section Requirements

### `Build Goal`

State the real objective of the team, the user ask being honored, the checked format or regulation context, and whether the team is a current-field recommendation or a more inference-heavy early read.

Use `current-field recommendation` when the build’s positioning is backed by verified current format or meta checks. Use `inference-heavy early read` when the shell relies more on inference because live support is limited or the field is moving quickly.

If the user does not specify format, verify the current regulation or rules state first, then state that verified assumption and a short dated or source basis note when current-context claims materially affect the build.

### `Recommended Team`

List the six mons that make up the one primary draft only. This section must not contain alternate branches.

### `Role Map`

Explain the team structure at a high level, including the primary win path, speed or tempo control, board-control tools, damage profile or pressure pattern, and likely preserve logic or closer identity when that is already clear from the build.

### `Set Direction`

Give lightweight set direction for each slot. The minimum useful level is role framing, likely item direction, move or utility emphasis, and tera-style or equivalent positioning direction when materially relevant. This is not a full export set sheet.

### `Why Each Slot Exists`

Explain each slot in the context of the full team plan. Each note should cover the slot’s job, why it belongs on this specific team, and what problem it solves in the current field or in the requested game plan.

### `Matchup Notes`

Cover the team’s intended posture into the most relevant pressure points for the build. This is matchup-intent guidance, not exhaustive pairing coverage. Keep it tied to the actual shell rather than generic type-chart commentary.

### `Weaknesses and Next Refinements`

State the real unresolved weaknesses. This is the only place where optional future tuning ideas belong.

## Workflow

1. Lock the active format and major meta pressures first.
2. If the build depends on a legality or rules assumption, align with `vgc-format-verifier` before choosing slots.
3. Identify the real build goal behind the request before choosing slots.
4. Build around one clear team identity.
5. Recommend one primary draft only.
6. Keep the requested mon or concept only when it still supports one coherent team.
7. If the request is weak but salvageable, say so directly, explain the tradeoffs, and build the best honest shell.
8. If the request breaks team quality too hard, say that plainly and pivot to the nearest viable version that preserves the user goal as much as possible.
9. Give lightweight set direction for each slot so the draft is testable immediately.
10. If a current-field positioning claim is thin, apply `vgc-source-verifier` discipline instead of overselling it.
11. End with the real weaknesses and likely next refinements instead of pretending the build is solved.

## Build Checklist

- Read [references/build-principles.md](references/build-principles.md) before finalizing the team.
- Cover speed or tempo control, board control, damage profile, and matchup intent.
- Keep optional swaps inside `Weaknesses and Next Refinements`, not in the main recommendation.
- Avoid generic six-goodstuff recommendations with no structure.

## Freshness Policy

- Use live web verification by default when current meta context materially affects the build.
- Do not claim a mon or shell is well-positioned right now without checking.
- Label inference when a positioning claim is not directly sourced.
- If the metagame is moving fast, say the build is a current best read rather than a solved shell.

## Output Quality Bar

- Read [references/output-rubric.md](references/output-rubric.md) when tightening the response.
- Be competitive-direct.
- Explain how all six slots support the same plan.
- Keep set direction lightweight and practical rather than export-level unless the user explicitly asks for a full build.

## Rules

- recommend one primary draft only
- keep the requested idea only when it still makes a coherent team
- be explicit when pivoting away from a weak request
- keep matchup notes tied to the actual shell
- do not hide unresolved weaknesses

## Common Mistakes

- forcing the requested mon into a shell where it does not belong
- giving multiple half-committed versions instead of one real recommendation
- listing six mons without role logic or usable set direction
- ignoring what the current field actually punishes
- turning the refinement section into a second team
