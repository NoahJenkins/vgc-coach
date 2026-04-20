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
3. If the request is a fully specified damage, KO, or survival question, use the repo-local exact-browser calc path first.
4. If critical exact inputs are missing, illegal for the active ruleset, or the browser calc fails, switch to honest benchmark framing instead of inventing precision.
5. Treat speed questions separately; do not force them through the exact-browser damage path.
6. Prioritize the few benchmarks that change lead, set, EV, or preserve decisions.
7. Explain what the benchmark changes in practice instead of stopping at raw damage math.
8. If a rules question blocks the calc, align with `vgc-format-verifier`.

## Required behavior
- Read [calc-checklist](../../docs/skills/vgc-calcs-assistant/references/calc-checklist.md), [browser-exactness](../../docs/skills/vgc-calcs-assistant/references/browser-exactness.md), and [output-rubric](../../docs/skills/vgc-calcs-assistant/references/output-rubric.md) before finalizing.
- Keep every exact claim tied to explicit assumptions.
- For fully specified damage/survival requests, prefer `python3 tools/browser_damage_calc.py` with a structured JSON payload over ad-hoc browser clicking.
- Use browser-derived exact numbers only when the exact run returned `status=exact`.
- If the exact run returned `fallback` or `blocked`, say exact external verification did not complete and continue with benchmark framing.
- Use benchmark bands when the data is incomplete.
- Do not route speed-only checks through the exact browser tool in v1.
- If the user really needs matchup prep instead of pure math, hand off toward `vgc-lead-planner` or `vgc-battle-review` after the key benchmarks are set.
- Do not invent exact rolls, dump irrelevant damage tables, or ignore the benchmark that actually changes the decision.
