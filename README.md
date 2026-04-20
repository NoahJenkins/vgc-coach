# VGC Coach

VGC Coach is a Codex-first, agent-portable coaching project for Pokemon Champions VGC.

The product direction is not "build a fake optimizer." It is:

- research the live metagame accurately
- help build coherent teams around target mons or strategies
- generate matchup and lead plans
- review games and turn them into better future recommendations
- evolve toward real-time battle assistance only after the state/eval layers are trustworthy

## MVP

The first useful version should ship five core skills:

1. `vgc-meta-research`
2. `vgc-team-builder`
3. `vgc-team-audit`
4. `vgc-lead-planner`
5. `vgc-battle-review`

The repo also carries five support skills that reinforce the core layer:

1. `vgc-format-verifier`
2. `vgc-source-verifier`
3. `vgc-calcs-assistant`
4. `vgc-opponent-scout`
5. `vgc-practice-journal`

These are supported by a shared data and evaluation layer:

- format/rules verification
- source freshness checks
- versioned meta snapshots
- replay and battle-review fixtures
- skill eval harness

## Principles

- Codex is the first supported agent runtime.
- Skill logic must remain agent-neutral where possible.
- Runtime-specific behavior belongs in thin adapter docs, not in the core skill logic.
- Official rules outrank community sources.
- Current-meta claims must be source-backed or clearly marked as inferred.
- Skill changes should be measured against fixed eval cases before being trusted.

## Key Docs

- [Design Spec](./docs/superpowers/specs/2026-04-18-vgc-coach-design.md)
- [MVP Plan](./docs/superpowers/plans/2026-04-18-vgc-coach-mvp.md)

## Initial Repo Shape

```text
vgc-coach/
├── AGENTS.md
├── README.md
├── docs/
│   ├── superpowers/
│   │   ├── specs/
│   │   └── plans/
│   ├── runtime/
│   └── evals/
├── skills/
│   ├── vgc-meta-research/
│   ├── vgc-team-builder/
│   ├── vgc-team-audit/
│   ├── vgc-lead-planner/
│   └── vgc-battle-review/
├── data/
│   ├── snapshots/
│   ├── fixtures/
│   └── rubrics/
└── tools/
    ├── eval-runner/
    └── replay-ingestion/
```

## What Not To Build First

- autonomous Showdown battling
- "best team" scoring without a credible simulator/policy stack
- vision-first live coaching before a battle-state schema exists
- separate Codex/Claude/OpenCode implementations of the same core skill
