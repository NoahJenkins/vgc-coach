# VGC Coach Design

## Goal

Create a Codex-first coaching repo for Pokemon Champions VGC that gives accurate, practical help for:

- current meta research
- team building around target mons or strategies
- matchup and lead planning
- battle review and iterative improvement

The system should be portable to Claude Code, OpenCode, and similar agent runtimes later without rewriting the core logic.

## Product Thesis

The immediate value is not autonomous battle optimization. The immediate value is structured competitive help that stays current, explains its reasoning, and improves through replay review and evaluation.

This repo should act like a disciplined VGC assistant, not like an overconfident theory engine.

## Non-Goals For V1

- autonomous Showdown battling
- simulator-based team ranking
- image/video-driven live coaching
- deep historical analytics across large replay archives
- polished hosted product UI

## Recommended Architecture

### 1. Core Skill Layer

The core repo value should live in skills that solve concrete user jobs.

MVP skills:

1. `vgc-meta-research`
2. `vgc-team-builder`
3. `vgc-team-audit`
4. `vgc-lead-planner`
5. `vgc-battle-review`

Supporting skills:

- `vgc-format-verifier`
- `vgc-source-verifier`
- `vgc-calcs-assistant`
- `vgc-opponent-scout`
- `vgc-practice-journal`

### 2. Shared Data Layer

Every coaching skill should consume the same durable artifacts instead of scraping or improvising independently.

Required shared artifacts:

- `meta snapshots`
  - format rules version
  - source provenance
  - usage leaders
  - common cores
  - sample teams
  - freshness timestamp
- `team inputs`
  - showdown paste or structured 6-mon team artifact
- `replay fixtures`
  - replay URLs, parsed logs, or normalized battle-review examples
- `rubrics`
  - criteria for good skill output

### 3. Evaluation Layer

The repo needs a first-class quality loop.

The evaluation layer should answer:

- Did the skill stay format-accurate?
- Did the advice become more actionable?
- Did the builder produce coherent teams?
- Did battle review identify the right mistakes?

Recommended mechanism:

- fixed eval cases under `data/fixtures/`
- shared rubrics under `data/rubrics/`
- repo-local eval runner under `tools/eval-runner/`
- `plugin-eval` used to benchmark changes to skill quality

### 4. Runtime Adapter Layer

The project should be Codex-first but not Codex-only.

Use one shared core:

- repo `AGENTS.md`
- portable skill content under `skills/`
- shared eval/data artifacts

Then add thin runtime-specific guidance:

- `docs/runtime/codex.md`
- `docs/runtime/claude-code.md`
- `docs/runtime/opencode.md`

These files should explain loading, tool assumptions, and any runtime-specific formatting quirks. They should not fork the core coaching logic unless a runtime limitation forces it.

## Skill Definitions

### `vgc-meta-research`

Purpose:

- produce a concise, source-backed view of the active format

Inputs:

- format/regulation
- optional region/event lens
- optional target archetype

Outputs:

- top usage
- common teams/cores
- important strategies
- anti-meta openings
- freshness note

### `vgc-team-builder`

Purpose:

- build a team around target mons, archetypes, or strategic goals

Inputs:

- target mons
- target strategy
- style preferences
- avoid list
- anti-meta goal

Outputs:

- 6-mon draft
- role map
- set directions
- why each slot exists
- unresolved tradeoffs

### `vgc-team-audit`

Purpose:

- critique an existing team and identify practical weaknesses

Outputs:

- structural holes
- matchup weaknesses
- speed-control issues
- item/moveset tension
- recommended changes

### `vgc-lead-planner`

Purpose:

- convert a team into opening lines and matchup heuristics

Outputs:

- default leads
- matchup-specific leads
- preserve targets
- first-turn goals
- common traps to avoid

### `vgc-battle-review`

Purpose:

- turn a replay, log, or turn summary into concrete learning

Outputs:

- key decision points
- mistakes
- stronger lines
- prep implications
- recurring habits to improve

## Data Contracts To Add Early

### Meta Snapshot v1

Must include:

- `snapshot_id`
- `generated_at`
- `format`
- `rules_version`
- `sources[]`
- `usage[]`
- `common_cores[]`
- `sample_teams[]`
- `fresh_until`

### Team Build Request v1

Must include:

- `format`
- `target_mons[]`
- `target_strategy`
- `constraints`
- `anti_meta_targets[]`
- `playstyle`

### Battle Review Request v1

Must include:

- `format`
- `source_type`
- `replay_url` or `battle_log`
- `player_side`
- `review_goal`

## Showdown Strategy

Showdown should be treated as a testing and review surface first.

Build early support for:

- export to Showdown paste
- replay/log ingestion
- replay review prompts
- matchup test plans

Do not treat Showdown battle automation as a core dependency of v1 quality.

## Feedback Loop Strategy

Use two layers:

### Layer 1: Skill evaluation

Use `plugin-eval` and repo-local fixtures to measure:

- factual accuracy
- format correctness
- coherence
- usefulness
- failure cases

### Layer 2: Real usage feedback

Capture:

- bad recommendations
- user corrections
- replay outcomes
- recurring build mistakes
- stale-source incidents

This feedback should feed new fixtures and rubric updates.

## Initial Repo Layout

```text
vgc-coach/
├── AGENTS.md
├── README.md
├── docs/
│   ├── runtime/
│   └── superpowers/
│       ├── specs/
│       └── plans/
├── skills/
├── data/
│   ├── fixtures/
│   ├── rubrics/
│   └── snapshots/
└── tools/
```

## Recommended First Milestone

Ship a usable offline repo with:

- design docs
- eval fixtures
- rubrics
- the first five skill folders
- a meta snapshot schema
- a replay review schema
- Codex runtime guidance

That would be enough to make the repo real and testable without prematurely building automation theater.
