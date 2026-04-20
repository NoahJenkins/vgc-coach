# VGC Coach

VGC Coach is a Codex-first, runtime-portable coaching repo for Pokemon Champions VGC.

It is designed as a skill-and-evaluation workspace, not a finished end-user app. The current focus is building reliable coaching skills around live-format research, team building, lead planning, and replay review before adding heavier runtime or tooling layers.

## Core Focus

The MVP stays centered on five coaching skills:

1. `vgc-meta-research`
2. `vgc-team-builder`
3. `vgc-team-audit`
4. `vgc-lead-planner`
5. `vgc-battle-review`

The repo also includes support skills that reinforce that core layer:

- `vgc-format-verifier`
- `vgc-source-verifier`
- `vgc-calcs-assistant`
- `vgc-opponent-scout`
- `vgc-practice-journal`

## Current Capabilities

The repo already contains the core pieces needed to iterate on coaching quality:

- agent-portable skill definitions under `skills/`
- examples and reference material under `docs/skills/`
- runtime adapter notes under `docs/runtime/`
- fixed eval cases under `data/fixtures/evals/`
- scoring rubrics under `data/rubrics/`
- versioned meta snapshot artifacts under `data/snapshots/`
- design and MVP planning docs under `docs/superpowers/`

Planned next layers such as repo-local eval tooling, replay ingestion utilities, and battle-state schema work are not implemented yet.

## Principles

- Current-meta claims should use live verification before being presented as current.
- Official rules sources outrank community sources.
- Core coaching logic should stay runtime-neutral where possible.
- Runtime-specific differences should stay in thin adapter docs, not the shared skill layer.
- Skill changes should be judged against fixed eval cases and rubrics, not just nicer wording.

## Where To Start

- [README.md](./README.md): stable repo overview
- [STATE.md](./STATE.md): current workstream, progress, and next-step status
- [AGENTS.md](./AGENTS.md): repo operating rules and project constraints
- [Design Spec](./docs/superpowers/specs/2026-04-18-vgc-coach-design.md): product direction and architecture intent
- [MVP Plan](./docs/superpowers/plans/2026-04-18-vgc-coach-mvp.md): implementation roadmap for the first useful version

## Actual Repo Layout

```text
vgc-coach/
├── AGENTS.md
├── README.md
├── STATE.md
├── data/
│   ├── fixtures/
│   │   └── evals/
│   ├── rubrics/
│   └── snapshots/
├── docs/
│   ├── evals/
│   ├── runtime/
│   │   └── codex/
│   ├── skills/
│   └── superpowers/
│       ├── plans/
│       └── specs/
└── skills/
    ├── vgc-battle-review/
    ├── vgc-calcs-assistant/
    ├── vgc-format-verifier/
    ├── vgc-lead-planner/
    ├── vgc-meta-research/
    ├── vgc-opponent-scout/
    ├── vgc-practice-journal/
    ├── vgc-source-verifier/
    ├── vgc-team-audit/
    └── vgc-team-builder/
```

## What Not To Build First

- autonomous Showdown battling
- fake "best team" scoring without a credible simulator or policy layer
- vision-first live coaching before a battle-state schema exists
- separate Codex, Claude, and OpenCode rewrites of the same core coaching logic
