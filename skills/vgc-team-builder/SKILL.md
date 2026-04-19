---
name: vgc-team-builder
description: Use when the user wants a Pokemon Champions team built around target mons, a preferred strategy, or an anti-meta goal, especially when they need one strong recommended draft instead of a loose list of options.
---

# VGC Team Builder

## Overview

Use this skill to build **one coherent recommended team** for Pokemon Champions first.

This skill should act like a competitive prep partner. It should not silently force bad assumptions just because the user named a mon or idea. If a requested mon or shell is weak, say so directly and still give the best viable version.

## Inputs

Accept:

- target mons
- target strategy or archetype
- playstyle preference
- anti-meta goals
- avoid list

If the user does not specify format, default to the current Pokemon Champions regulation and say so.

## Output Contract

Always return these sections in this order:

1. `Build Goal`
2. `Recommended Team`
3. `Role Map`
4. `Why Each Slot Exists`
5. `Matchup Notes`
6. `Weaknesses and Next Refinements`

## Workflow

1. Lock the active format and major meta pressures first.
2. Interpret what the user is really trying to achieve with the requested mon or strategy.
3. Build around a clear team identity, not around six individually reasonable picks.
4. Prefer one strong recommendation over multiple weak branches.
5. Keep the requested idea when it is viable; if it is weak, explain the limitation and adapt honestly.
6. End with the real weaknesses instead of pretending the draft is solved.

## Build Principles

- Read [references/build-principles.md](references/build-principles.md) before finalizing the team.
- Build for Champions-first assumptions.
- Cover speed control, board control, damage profile, and matchup intent.
- Avoid generic six-goodstuff recommendations with no structure.

## Freshness Policy

- Use live web verification by default when current meta context materially affects the build.
- Do not claim a mon or shell is well-positioned right now without checking.
- If the meta is moving fast, say the build is an early-meta recommendation.

## Output Quality Bar

- Read [references/output-rubric.md](references/output-rubric.md) when tightening the response.
- Be competitive-direct.
- Explain why each slot exists in the same game plan.
- Keep recommendations human-usable rather than over-optimized for theoretical completeness.

## Common Mistakes

- forcing the requested mon into a shell where it does not belong
- proposing multiple branches instead of making a recommendation
- ignoring what the current field actually punishes
- listing six mons without role logic or matchup intent
