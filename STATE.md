# VGC Coach State

Last updated: 2026-04-19

## Purpose

`vgc-coach` is a Codex-first, runtime-portable coaching repo for Pokemon Champions VGC.

The repo is optimizing for:

- current-format research accuracy
- practical team-building help
- matchup and lead planning
- replay-based feedback loops
- disciplined evaluation of skill quality

The repo is explicitly **not** trying to start with:

- fake simulator-driven "best team" claims
- autonomous Showdown battling
- vision-first live coaching

## Canonical Planning Docs

- [Design Spec](./docs/superpowers/specs/2026-04-18-vgc-coach-design.md)
- [MVP Plan](./docs/superpowers/plans/2026-04-18-vgc-coach-mvp.md)
- [README](./README.md)
- [AGENTS](./AGENTS.md)

## Current Repo Status

### Completed

- Repo initialized and scaffolded
- Core product framing documented in `README.md` and `AGENTS.md`
- Superpowers design and MVP plan written under `docs/superpowers/`
- Shared contracts scaffolded for:
  - meta snapshots
  - team build requests
  - battle review requests
- Initial rubric and eval fixture structure created
- Runtime guidance added for:
  - Codex
  - Claude Code
  - OpenCode
- First five MVP skill folders created:
  - `vgc-meta-research`
  - `vgc-team-builder`
  - `vgc-team-audit`
  - `vgc-lead-planner`
  - `vgc-battle-review`
- `vgc-meta-research`, `vgc-team-builder`, and `vgc-team-audit` implemented beyond scaffold level

### In Progress

The main active workstream is `vgc-meta-research`.

Uncommitted work currently present:

- stronger `vgc-meta-research` source/freshness guidance
- live source map reference for current Champions research
- dated Reg M-A snapshot artifact
- manual live-check checklist
- plugin-eval benchmark artifacts for real observed usage
- quality-first eval rewrite for `vgc-meta-research`

### Not Started

- end-to-end implementation work for:
  - `vgc-lead-planner`
  - `vgc-battle-review`
- real implementation pass for `vgc-team-builder` and `vgc-team-audit` beyond current skill-package level
- repo-local eval runner tools
- replay ingestion utilities
- battle-state schema

## Working Tree Snapshot

Latest committed repo state:

- `a92b089` `feat: implement core vgc coaching skills`

Tracked but uncommitted changes exist in:

- `data/fixtures/evals/meta-research/case-01.md`
- `data/fixtures/evals/meta-research/case-02.md`
- `data/fixtures/evals/meta-research/case-03.md`
- `data/rubrics/meta-research-rubric.md`
- `data/snapshots/README.md`
- `skills/vgc-meta-research/SKILL.md`
- `skills/vgc-meta-research/examples/good-example.md`

Untracked current additions:

- `data/rubrics/meta-research-human-review.md`
- `data/snapshots/champions-reg-m-a-2026-04-18.json`
- `docs/evals/meta-research-live-checklist.md`
- `skills/vgc-meta-research/references/current-source-map.md`
- `skills/vgc-meta-research/.plugin-eval/`

## Current Findings

### Product Direction

Quality should be the primary optimization target.

Priority order:

1. format correctness
2. source freshness and trust
3. practical competitive usefulness
4. inference honesty
5. efficiency

### Plugin Eval Reality

`plugin-eval` is now available as a shell command on this machine.

Observed benchmark results for `vgc-meta-research` show:

- the skill can complete representative tasks successfully
- live current-source research is extremely token-heavy in practice
- default plugin-eval scoring over-weights cost relative to the product goal

This led to adding a quality-first rubric layer in-repo rather than treating plugin-eval's default grade as the source of truth.

## Immediate Next Recommended Steps

1. Review the three benchmark output artifacts using the new quality-first rubric.
2. Decide whether the current `vgc-meta-research` quality is good enough to commit as-is.
3. Commit the current `vgc-meta-research` batch once reviewed.
4. Move next to `vgc-team-builder` using the same pattern:
   - quality-first rubric
   - real examples
   - plugin-eval benchmark only as supporting evidence

## Open Decisions

- Should `.plugin-eval/` benchmark artifacts be committed or ignored?
- Should `STATE.md` remain the canonical progress tracker, or should a dated status file also live under `docs/superpowers/`?
- How much of plugin-eval's budget-oriented grading should influence merge decisions for research-heavy skills?

## Thread Handoff Notes

If a future thread resumes work here, start with:

1. Read [STATE.md](./STATE.md)
2. Read [Design Spec](./docs/superpowers/specs/2026-04-18-vgc-coach-design.md)
3. Read [MVP Plan](./docs/superpowers/plans/2026-04-18-vgc-coach-mvp.md)
4. Check `git status --short`
5. If working on `vgc-meta-research`, inspect:
   - [SKILL.md](./skills/vgc-meta-research/SKILL.md)
   - [meta-research-rubric.md](./data/rubrics/meta-research-rubric.md)
   - [meta-research-human-review.md](./data/rubrics/meta-research-human-review.md)
   - [benchmark-usage.jsonl](./skills/vgc-meta-research/.plugin-eval/benchmark-usage.jsonl)

## Success Condition For Current Workstream

The current `vgc-meta-research` workstream is in a good stopping state when:

- the quality-first rubric and benchmark-informed changes are reviewed
- the current batch is committed cleanly
- the repo has one accepted standard for judging research-skill quality
