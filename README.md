# VGC Coach

VGC Coach is an open-source VGC coaching skill-and-eval workspace for Pokemon Champions.

This repo is built around canonical skill packages in `skills/`, thin runtime adapters, fixed eval cases, and quality rubrics. It is meant to improve reusable coaching behavior first, not to start with a finished end-user app.

## Open Source Status

- License: [Apache-2.0](./LICENSE)
- Contributions: [focused PRs welcome](./CONTRIBUTING.md)
- Shared skill logic lives in `skills/`
- Runtime-specific behavior stays in `docs/runtime/`

## Use This Repo

The simplest way to use these skills is to clone this repository and open it in a supported coding agent. This repo is currently designed as a project-scoped skill workspace, not as a packaged npm or Python distribution.

```bash
git clone https://github.com/NoahJenkins/vgc-coach.git
cd vgc-coach
```

After cloning:

- Codex discovers the repo-local skill wrappers from `.agents/skills/`
- Claude Code discovers the project skill wrappers from `.claude/skills/`
- OpenCode has secondary support through `opencode.json`, `.opencode/skills/`, and `.opencode/commands/`

Runtime-specific setup and behavior live here:

- [Codex runtime](./docs/runtime/codex.md)
- [Claude Code runtime](./docs/runtime/claude-code.md)
- [OpenCode runtime](./docs/runtime/opencode.md)

## How The Repo Works

- `skills/` is the only canonical editable source for shared coaching skill behavior.
- `.agents/skills/`, `.claude/skills/`, and `.opencode/skills/` are discovery layers that point back to the shared skill packages.
- `docs/skills/` contains references and examples that support the shared skills.
- `data/fixtures/evals/` and `data/rubrics/` are the acceptance surface for judging whether a skill actually improved.
- `docs/runtime/` documents runtime-specific behavior without forking the underlying coaching logic.

If you want to adapt these skills for your own agent setup, use the shared packages in `skills/` as the source of truth and keep any runtime-specific wrappers thin.

## Core Focus

The current MVP stays centered on five coaching skills:

1. `vgc-meta-research`
2. `vgc-team-builder`
3. `vgc-team-audit`
4. `vgc-lead-planner`
5. `vgc-battle-review`

Support skills reinforce that core layer:

- `vgc-format-verifier`
- `vgc-source-verifier`
- `vgc-calcs-assistant`
- `vgc-opponent-scout`
- `vgc-practice-journal`

## Skill Catalog

### Core Focus Skills

- `vgc-meta-research`: live Pokemon Champions meta snapshots, trend reads, and anti-meta openings grounded in current sources
- `vgc-team-builder`: one practical, coherent team around a target mon, strategy, or anti-meta goal
- `vgc-team-audit`: findings-first team reviews that preserve identity unless the identity itself is the problem
- `vgc-lead-planner`: default leads, matchup branches, preserve targets, and turn-one priorities
- `vgc-battle-review`: replay or turn-log review that separates real mistakes from variance and hindsight

### Support Skills

- `vgc-format-verifier`: verify legality, regulation, and current-format truth before coaching
- `vgc-source-verifier`: audit whether a meta, matchup, or rules claim is actually sourced cleanly
- `vgc-calcs-assistant`: damage, survival, speed, and benchmark framing; v1 exact support is limited to damage, KO, and survival, while speed checks remain assumption-framed
- `vgc-opponent-scout`: turn public info into likely shells, techs, and prep notes
- `vgc-practice-journal`: compress testing notes into next-session changes and follow-up questions

## Stable Today

The repo already includes:

- canonical shared skill packages under `skills/`
- Codex discovery wrappers under `.agents/skills/`
- Claude Code discovery wrappers under `.claude/skills/`
- OpenCode adapter support under `opencode.json`, `.opencode/skills/`, and `.opencode/commands/`
- runtime docs under `docs/runtime/`
- examples and references under `docs/skills/`
- fixed eval cases under `data/fixtures/evals/`
- scoring rubrics under `data/rubrics/`
- versioned meta snapshot artifacts under `data/snapshots/`
- repo-local helper tooling under `tools/`
- exact-browser calc support for `vgc-calcs-assistant` through `python3 tools/browser_damage_calc.py`, currently limited to damage, KO, and survival

## Not Built Yet

These are still future-work layers, not shipped capabilities:

- repo-local eval runner tooling
- replay ingestion utilities
- battle-state schema work
- broader exact-browser calc support beyond the current v1 path

## Principles

- Verify current meta, rules, and legality before presenting them as current.
- Prefer official rules sources over community sources.
- Keep shared coaching logic runtime-neutral where possible.
- Keep runtime wrappers thin and avoid runtime-specific rewrites of the same skill logic.
- Judge skill changes against fixtures and rubrics, not just nicer wording.

## Where To Start

- [AGENTS.md](./AGENTS.md): repo rules and project constraints
- [STATE.md](./STATE.md): current workstream and progress snapshot
- [Design Spec](./docs/superpowers/specs/2026-04-18-vgc-coach-design.md): product direction and architecture intent
- [MVP Plan](./docs/superpowers/plans/2026-04-18-vgc-coach-mvp.md): early implementation roadmap

## Repo Layout

Abridged view of the main public-facing structure:

```text
vgc-coach/
├── AGENTS.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── STATE.md
├── .agents/
│   └── skills/
├── .claude/
│   ├── CLAUDE.md
│   └── skills/
├── .opencode/
│   ├── commands/
│   └── skills/
├── opencode.json
├── data/
│   ├── fixtures/
│   │   └── evals/
│   ├── rubrics/
│   └── snapshots/
├── docs/
│   ├── evals/
│   ├── runtime/
│   ├── skills/
│   └── superpowers/
├── tools/
└── skills/
```
