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
- `vgc-meta-research` source/freshness hardening batch committed on `main`
- `vgc-lead-planner` hardened to full MVP package shape:
  - strong contract in `SKILL.md`
  - runtime metadata in `agents/openai.yaml`
  - two good examples plus one failure example
  - checklist and output rubric under `references/`
  - three representative eval cases
- `vgc-battle-review` hardened to the same MVP package shape:
  - strong contract in `SKILL.md`
  - runtime metadata in `agents/openai.yaml`
  - two good examples plus one failure example
  - checklist and output rubric under `references/`
  - three representative eval cases

### In Progress

The MVP skill hardening pass is complete in the local working tree.

Current follow-up work is:

- deciding whether `.plugin-eval/` artifacts should stay committed or move to `.gitignore`
- choosing the next post-MVP quality layer:
  - repo-local eval runner tooling
  - deeper implementation work for `vgc-team-builder` and `vgc-team-audit`
  - replay ingestion utilities and battle-state schema later

### Not Started

- real implementation pass for `vgc-team-builder` and `vgc-team-audit` beyond current skill-package level
- repo-local eval runner tools
- replay ingestion utilities
- battle-state schema

## Working Tree Snapshot

Latest committed repo state:

- `ef4e5d6` `Harden lead planner docs and update state`

Current local working tree reflects the accepted `vgc-battle-review` hardening batch and this state refresh.

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

### MVP Gap Reality

The remaining MVP gaps are no longer repo setup or product framing.

The main remaining quality gaps are:

- repo-local tooling is still absent, but that is lower priority than finishing the core skill layer
- `vgc-team-builder` and `vgc-team-audit` still stop at skill-package depth rather than deeper repo-local implementation

### MVP Hardening Acceptance Notes

Acceptance checks passed for the two target skills:

- `vgc-lead-planner`
  - package shape matches the repo MVP standard
  - three eval cases cover weather offense, Trick Room, and balance/Fake Out pressure
  - contract preserves the required output section order
- `vgc-battle-review`
  - package shape now matches the same MVP standard
  - three eval cases cover sequencing loss, preserve-logic collapse, and hidden-information surprise tech
  - contract preserves the required output section order

## Immediate Next Recommended Steps

1. Decide whether `.plugin-eval/` artifacts should stay committed or move to `.gitignore`.
2. Choose whether the next investment is repo-local eval tooling or deeper implementation for `vgc-team-builder` and `vgc-team-audit`.
3. Only after that, add replay ingestion utilities and battle-state schema work.

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
5. If working on `vgc-lead-planner`, inspect:
   - [SKILL.md](./skills/vgc-lead-planner/SKILL.md)
   - [lead-planner-rubric.md](./data/rubrics/lead-planner-rubric.md)
   - [case-01.md](./data/fixtures/evals/lead-planner/case-01.md)
6. If working on `vgc-battle-review`, inspect:
   - [SKILL.md](./skills/vgc-battle-review/SKILL.md)
   - [battle-review-rubric.md](./data/rubrics/battle-review-rubric.md)
   - [case-01.md](./data/fixtures/evals/battle-review/case-01.md)
7. If working on `vgc-meta-research`, inspect:
   - [SKILL.md](./skills/vgc-meta-research/SKILL.md)
   - [meta-research-rubric.md](./data/rubrics/meta-research-rubric.md)
   - [meta-research-human-review.md](./data/rubrics/meta-research-human-review.md)
   - [benchmark-usage.jsonl](./skills/vgc-meta-research/.plugin-eval/benchmark-usage.jsonl)

## Success Condition For Current Workstream

The current MVP hardening workstream is now in a good stopping state:

- `vgc-lead-planner` and `vgc-battle-review` are both no longer scaffold-thin
- the repo has at least 3 representative eval cases for both skills
- the current batch has been reviewed locally and is ready for commit
