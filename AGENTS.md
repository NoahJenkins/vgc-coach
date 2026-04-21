# VGC Coach Instructions

## Repo Purpose

`vgc-coach` is a shared VGC coaching skill-and-eval workspace for Pokemon Champions.

This repo is for building, testing, and hardening reusable coaching skills, not for shipping a finished end-user app first.

The main product surface is the shared skill layer under `skills/`, supported by fixed eval cases, rubrics, runtime adapters, and thin discovery wrappers for supported runtimes.

## Product Direction

Optimize for:

- current-format research accuracy
- practical team-building help
- matchup and lead planning
- replay-based feedback loops
- disciplined evaluation of skill quality

Do not optimize for:

- verbose but weak advice
- stale meta claims presented as current
- fake legality, usage, or matchup certainty
- runtime-specific rewrites of the same coaching logic

## Canonical Source Of Truth

- `skills/` is the only canonical editable source for shared coaching skill behavior.
- `plugins/` contains generated distribution artifacts and is not a hand-edited source tree.
- `.agents/skills/` is the Codex discovery layer and should stay thin.
- `.claude/skills/` is the Claude Code discovery layer and should stay thin.
- `.opencode/skills/` is additive runtime support and should stay thin.
- `.agents/plugins/marketplace.json`, `.claude-plugin/marketplace.json`, and the repo-root `package.json` are generated distribution metadata.
- `docs/runtime/*.md` is where runtime-specific behavior and limitations belong.
- `docs/skills/` holds shared references and examples that support the canonical skill packages.
- `data/fixtures/` and `data/rubrics/` are the validation layer for judging skill quality.

Do not fork shared skill logic into runtime-specific copies unless a real runtime limitation forces it.

## Runtime Support

- Codex is the primary runtime for this repo.
- Claude Code is supported through a thin adapter over the same shared skill packages.
- OpenCode support exists as an additive adapter layer and should not drive the repo structure.
- Runtime-specific wrappers should point back to shared skill packages instead of duplicating them.
- Shared repo rules belong here in `AGENTS.md`; runtime-specific exceptions belong in `docs/runtime/`.

## Skill Change Rules

- Keep shared coaching logic runtime-neutral whenever possible.
- Preserve the output contracts defined in each `SKILL.md` unless the change intentionally updates that contract.
- Regenerate packaged plugin artifacts after shared-skill or runtime-doc changes instead of editing generated plugin copies by hand.
- When a skill depends on current format, legality, or meta state, verify those claims live before presenting them as current.
- Prefer official rules sources over community sources.
- Use community sources for trends, usage, and archetype interpretation only after format truth is locked.
- Label inference clearly when it is not directly sourced.
- Do not invent legality, usage, matchup, or calc facts.

## Validation Expectations

- A skill is not improved just because it reads better.
- Validate skill changes against the relevant fixed eval cases under `data/fixtures/evals/`.
- Use the matching rubric under `data/rubrics/` when judging whether the behavior actually improved.
- If a change affects runtime support, also verify the relevant discovery layer and runtime docs still match reality.
- If exact-browser calc behavior is involved, preserve the current limitation honestly: v1 exact support is only for damage, KO, and survival; speed guidance remains assumption-framed unless a verified exact backend exists.

## Current Priority

The current MVP priority remains:

1. `vgc-meta-research`
2. `vgc-team-builder`
3. `vgc-team-audit`
4. `vgc-lead-planner`
5. `vgc-battle-review`

Support skills and calc tooling should reinforce those core skills rather than pull the repo into separate product directions.

## Working Style In This Repo

- Prefer edits that strengthen the shared skill packages over runtime-local workarounds.
- Keep runtime glue thin and isolated.
- Keep repo docs factual and aligned with the live tree.
- Treat `README.md` as the stable repo overview, not the full operating manual for each skill.
- When documenting current capability, describe what the repo actually supports today and keep future work clearly framed as future work.
