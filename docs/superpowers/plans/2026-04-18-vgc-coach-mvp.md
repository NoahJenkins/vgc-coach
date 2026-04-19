# VGC Coach MVP Plan

> For future execution, keep the repo Codex-first but agent-neutral. Build shared artifacts before runtime-specific polish.

**Goal:** Stand up a usable VGC coaching repo with a clear MVP scope, durable data/eval artifacts, and the first five skills.

**Architecture:** Build the repo around a shared data layer, a small set of high-value coaching skills, and a repeatable evaluation harness. Keep Codex as the first runtime while preserving portability through thin runtime adapter docs rather than branching the core skill logic.

**Tech Stack:** Markdown docs, repo-local skill folders, JSON fixtures/snapshots, rubric files, optional small Node/Python utilities later.

---

## Phase 1: Repo Foundation

### Task 1: Establish repo guidance and product framing

**Files**

- Create: `AGENTS.md`
- Create: `README.md`

**Done when**

- The repo states its purpose, non-goals, and Codex-first portability rules.
- A new contributor can understand what this project is and what it is not.

### Task 2: Persist the design and plan artifacts

**Files**

- Create: `docs/superpowers/specs/2026-04-18-vgc-coach-design.md`
- Create: `docs/superpowers/plans/2026-04-18-vgc-coach-mvp.md`

**Done when**

- The repo contains a durable design doc and an MVP execution plan.

## Phase 2: Shared Data Contracts

### Task 3: Define `meta snapshot v1`

**Files**

- Create: `data/snapshots/README.md`
- Create: `data/snapshots/meta-snapshot-v1.example.json`

**Content**

- required fields
- source provenance
- freshness metadata
- usage/core/sample team sections

**Done when**

- Skills have one shared meta artifact contract.

### Task 4: Define `team build request v1`

**Files**

- Create: `data/fixtures/team-build-request-v1.example.json`

**Done when**

- The builder skill has a stable request shape.

### Task 5: Define `battle review request v1`

**Files**

- Create: `data/fixtures/battle-review-request-v1.example.json`

**Done when**

- Replay review and future live-state skills have a common review input contract.

## Phase 3: Evaluation Layer

### Task 6: Create evaluation rubric set

**Files**

- Create: `data/rubrics/meta-research-rubric.md`
- Create: `data/rubrics/team-builder-rubric.md`
- Create: `data/rubrics/team-audit-rubric.md`
- Create: `data/rubrics/lead-planner-rubric.md`
- Create: `data/rubrics/battle-review-rubric.md`

**Criteria to score**

- format correctness
- freshness/source discipline
- practical usefulness
- internal coherence
- hallucination risk

### Task 7: Create fixed eval fixtures

**Files**

- Create: `data/fixtures/evals/meta-research/`
- Create: `data/fixtures/evals/team-builder/`
- Create: `data/fixtures/evals/team-audit/`
- Create: `data/fixtures/evals/lead-planner/`
- Create: `data/fixtures/evals/battle-review/`

**Done when**

- Each MVP skill has at least 3 representative eval cases.

### Task 8: Document plugin-eval workflow

**Files**

- Create: `docs/evals/plugin-eval-workflow.md`

**Done when**

- The repo explains how to use `plugin-eval` to benchmark skill changes.

## Phase 4: Skill Scaffolding

### Task 9: Create the first five skill folders

**Files**

- Create: `skills/vgc-meta-research/SKILL.md`
- Create: `skills/vgc-team-builder/SKILL.md`
- Create: `skills/vgc-team-audit/SKILL.md`
- Create: `skills/vgc-lead-planner/SKILL.md`
- Create: `skills/vgc-battle-review/SKILL.md`

**Done when**

- Each skill has a purpose, inputs, outputs, source policy, and failure policy.

### Task 10: Add example-driven guidance to each skill

**Files**

- Create: `skills/*/examples/`

**Done when**

- Every MVP skill includes at least two positive examples and one failure-mode example.

## Phase 5: Runtime Portability

### Task 11: Add Codex runtime guidance

**Files**

- Create: `docs/runtime/codex.md`

**Done when**

- The repo documents how Codex should load and use the project.

### Task 12: Add Claude Code and OpenCode adapter docs

**Files**

- Create: `docs/runtime/claude-code.md`
- Create: `docs/runtime/opencode.md`

**Done when**

- Future runtime support has a documented landing zone without duplicating core skill logic.

## Phase 6: Showdown-As-Testing-Surface

### Task 13: Define Showdown export and replay-review boundaries

**Files**

- Create: `docs/showdown-integration.md`

**Must clarify**

- what v1 supports
- what v1 explicitly does not support
- why battle automation is deferred

## Exit Criteria For MVP

The MVP is ready when:

- the repo has the five core skills
- the repo has fixed eval cases and rubrics
- the repo has a shared meta snapshot schema
- the repo has runtime guidance for Codex first and future adapters
- skill changes can be reviewed against explicit fixtures instead of vibes

## Recommended Build Order

1. Foundation docs
2. Shared schemas
3. Rubrics and eval fixtures
4. Core skill scaffolds
5. Codex runtime docs
6. Cross-runtime docs
7. Showdown integration notes

## Recommendation

Do not start by writing automation-heavy tools.

The highest-ROI first implementation work is:

1. shared schemas
2. eval fixtures
3. first five skills
4. Codex runtime guidance

That path gets the repo useful quickly and avoids repeating the optimizer mistake of building impressive-looking machinery before the truth layer is solid.
