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

## Skill Catalog

### Core Focus Skills

- `vgc-meta-research`: use for live Pokemon Champions meta snapshots, trend reads, and anti-meta openings grounded in current sources.
- `vgc-team-builder`: use for building one practical, coherent team around a target mon, strategy, or anti-meta goal.
- `vgc-team-audit`: use for findings-first team reviews that preserve identity unless the identity itself is the problem.
- `vgc-lead-planner`: use for default leads, matchup branches, preserve targets, and turn-one priorities.
- `vgc-battle-review`: use for replay or turn-log review that separates real mistakes from variance and hindsight.

### Support Skills

- `vgc-format-verifier`: use when legality, regulation, or “is this current?” format truth needs to be verified before coaching.
- `vgc-source-verifier`: use when a meta, matchup, or rules claim needs a source audit before it is repeated as fact.
- `vgc-calcs-assistant`: use for damage, survival, speed, and benchmark questions that need honest decision framing; v1 exact-browser support is limited to damage, KO, and survival, while speed checks remain assumption-framed.
- `vgc-opponent-scout`: use for public-info scouting that turns likely shells, techs, and tendencies into prep notes.
- `vgc-practice-journal`: use for compressing testing notes into repeatable next-session changes and follow-up questions.

## Current Capabilities

The repo already contains the core pieces needed to iterate on coaching quality:

- agent-portable skill definitions under `skills/`
- Codex repo-skill discovery wrappers under `.agents/skills/`
- examples and reference material under `docs/skills/`
- runtime adapter notes under `docs/runtime/`
- fixed eval cases under `data/fixtures/evals/`
- scoring rubrics under `data/rubrics/`
- versioned meta snapshot artifacts under `data/snapshots/`
- repo-local helper tooling under `tools/`
- design and MVP planning docs under `docs/superpowers/`

Planned next layers such as repo-local eval tooling, replay ingestion utilities, and battle-state schema work are not implemented yet.

## Principles

- Current-meta claims should use live verification before being presented as current.
- Official rules sources outrank community sources.
- Core coaching logic should stay runtime-neutral where possible.
- Keep `skills/` as the canonical portable skill source and use `.agents/skills/` only as a thin Codex discovery layer.
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
├── .agents/
│   └── skills/
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
├── tests/
├── tools/
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
