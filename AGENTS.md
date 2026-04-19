# VGC Coach Instructions

## Project Goal

Build a Codex-first but runtime-portable VGC coaching system for Pokemon Champions.

The repo should prioritize:

- current-format research accuracy
- practical team-building help
- matchup and lead planning
- replay-based feedback loops
- disciplined evaluation of skill quality

## Core Rules

- Keep the core coaching logic agent-neutral.
- Keep runtime glue thin and isolated.
- Do not present stale meta claims as current.
- Prefer official rules sources over community sources.
- When a claim is inferred rather than directly sourced, label it.
- Do not invent legality, usage, or matchup facts.

## Runtime Strategy

- Codex is the first supported runtime.
- Future Claude Code and OpenCode support should reuse the same core skill content.
- Shared guidance should live in `AGENTS.md` and repo-local skill folders.
- Runtime-specific differences should be documented under `docs/runtime/`.

## Expected Repo Structure

- `skills/`
  - agent-portable skill definitions and examples
- `data/snapshots/`
  - current and historical meta snapshots
- `data/fixtures/`
  - replay samples, team samples, board-state fixtures, eval cases
- `data/rubrics/`
  - scoring rubrics for quality evaluation
- `tools/`
  - support utilities such as eval runners or replay ingestion
- `docs/runtime/`
  - Codex/Claude/OpenCode adapter notes

## Quality Bar

- A skill is not considered improved just because it sounds better.
- Skill changes should be tested against fixed eval cases.
- Advice should be optimized for usefulness in real team prep and battle decisions, not for verbosity.

## Current Priority

Build the MVP around:

1. `vgc-meta-research`
2. `vgc-team-builder`
3. `vgc-team-audit`
4. `vgc-lead-planner`
5. `vgc-battle-review`

All future work should reinforce those skills before expanding into live-battle coaching.
