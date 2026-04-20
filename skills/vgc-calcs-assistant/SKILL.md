---
name: vgc-calcs-assistant
description: Use when a Pokemon Champions calc or speed question needs honest benchmark framing.
---

# VGC Calcs Assistant

Convert calc questions into prep decisions, not fake precision.

## Inputs
- damage or KO questions
- survival benchmarks
- speed checks
- spread-tradeoff questions
- match-prep requests that hinge on one or two benchmark interactions

## Output
Return these sections in order:

1. `Calc Goal`
2. `Known Inputs`
3. `Relevant Benchmarks`
4. `Decision Impact`
5. `Missing Inputs or Confidence Limits`

## Workflow
1. Define the real decision before discussing numbers.
2. List known inputs explicitly: species, level, item, ability, spread, mechanics, and field state.
3. If critical inputs are missing, switch from exact-numbers mode to honest benchmark framing.
4. Prioritize the few benchmarks that change lead, set, EV, or preserve decisions.
5. Explain what the benchmark changes in practice instead of stopping at raw damage math.
6. If a rules question blocks the calc, align with `vgc-format-verifier`.

## Required behavior
- Read [calc-checklist](../../docs/skills/vgc-calcs-assistant/references/calc-checklist.md) and [output-rubric](../../docs/skills/vgc-calcs-assistant/references/output-rubric.md) before finalizing.
- Keep every exact claim tied to explicit assumptions.
- Use benchmark bands when the data is incomplete.
- If the user really needs matchup prep instead of pure math, hand off toward `vgc-lead-planner` or `vgc-battle-review` after the key benchmarks are set.
- Do not invent exact rolls, dump irrelevant damage tables, or ignore the benchmark that actually changes the decision.
