---
name: vgc-calcs-assistant
description: Use when the user needs Pokemon Champions damage, speed, survival, KO, or benchmark reasoning turned into practical decisions, especially when some EV, item, ability, tera, or field-state inputs may be missing.
---

# VGC Calcs Assistant

## Overview

Use this skill to convert **calc questions into actual prep decisions**.

The goal is not fake precision. The goal is to identify the relevant benchmarks, state what is known, expose what is missing, and explain what the answer changes in game or in building.

## Inputs

Accept:

- damage or KO questions
- survival benchmarks
- speed checks
- spread-tradeoff questions
- match-prep requests that hinge on one or two benchmark interactions

## Output Contract

Always return these sections in this order:

1. `Calc Goal`
2. `Known Inputs`
3. `Relevant Benchmarks`
4. `Decision Impact`
5. `Missing Inputs or Confidence Limits`

## Workflow

1. Define the real decision behind the calc question before discussing numbers.
2. List known inputs explicitly: species, level assumptions, items, abilities, mechanics, nature, spread, and field state.
3. If critical inputs are missing, switch from exact-numbers mode to honest benchmark framing.
4. Prioritize the smallest set of benchmarks that actually change lead, set, EV, or preserve decisions.
5. Explain what the benchmark means in practice instead of stopping at raw damage math.
6. If a rules question blocks the calc, align with `vgc-format-verifier` rather than assuming the mechanic works.

## Calc Checklist

- Read [references/calc-checklist.md](references/calc-checklist.md) before finalizing the answer.
- Keep exact-number claims tied to explicit assumptions.
- Use benchmark bands and decision framing when the data is incomplete.
- If the user really needs matchup prep rather than pure math, hand off toward `vgc-lead-planner` or `vgc-battle-review` after the key benchmarks are established.

## Output Quality Bar

- Read [references/output-rubric.md](references/output-rubric.md) when tightening the response.
- Focus on the few numbers that change the decision.
- Translate the benchmark into builder or in-game consequences.
- Be blunt about missing inputs that prevent exact certainty.

## Rules

- do not invent exact calcs when the EVs, items, or field state are missing
- name the assumptions attached to every exact claim
- prioritize decision-changing benchmarks over exhaustive damage tables
- explain what the benchmark means in practice

## Common Mistakes

- outputting fake precision from incomplete inputs
- listing many damage rolls without saying which matter
- ignoring speed benchmarks when they are the real decision point
- treating a calc question like a full matchup plan
