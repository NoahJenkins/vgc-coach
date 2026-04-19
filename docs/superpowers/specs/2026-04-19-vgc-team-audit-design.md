# VGC Team Audit Design

## Goal

Strengthen `vgc-team-audit` from a basic review scaffold into a findings-first, identity-preserving audit skill that identifies real structural weaknesses, ties them to gameplay consequences, and recommends the smallest useful fixes.

## Scope

This design covers:

- the skill behavior contract
- findings ordering and identity-preservation rules
- supporting checklist and rubric expectations
- example and fixed-fixture implications

This design does not cover:

- repo-local eval tooling
- replay ingestion
- runtime-specific forks of the skill

## Core Product Decision

`vgc-team-audit` should behave like a competitive audit, not a rewrite engine.

It should start with the team identity, surface the highest-impact issues first, separate "structurally broken" from "just unusual," and recommend targeted changes before larger rebuilds.

## Output Contract

The skill should always return:

1. `Top Findings`
2. `Team Identity`
3. `Matchup Holes`
4. `Recommended Changes`
5. `Residual Risk`

## Design Principles

### 1. Findings First

Do not spend the opening on compliments or generic scene-setting. The first section should surface the actual problems.

### 2. Identity Preservation

Preserve the team identity when possible. A team being weird is not, by itself, a flaw.

### 3. Consequence-Driven Critique

Each issue should explain how it loses games, such as preview pressure, lead collapse, preserve failures, or set tension.

### 4. Proportional Fixes

Recommend the smallest useful changes first. Only escalate to larger rebuilds when the identity itself causes the failure.

### 5. Honest Residual Risk

Do not pretend the team is solved after a few edits. State what still looks shaky.

## Acceptance Signals

The implementation is aligned when:

- the skill opens with high-signal findings
- unconventional teams are not flattened by default
- recommendations are tied to actual gameplay consequences
- residual risk is stated honestly
- examples and fixed cases punish filler praise and vague "needs synergy" language
