# VGC Team Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade `skills/vgc-team-audit/` into a findings-first, identity-preserving audit skill with stronger references, examples, and fixed eval expectations.

**Architecture:** Keep the core contract in `skills/vgc-team-audit/SKILL.md`, move repeatable decision rules into `references/`, teach the contract through examples, and use the existing fixed fixtures and rubric as the acceptance surface.

**Tech Stack:** Markdown skill files, repo-local eval fixtures and rubrics, Git.

---

## Key Implementation Areas

### Task 1: Tighten the core skill contract

**Files:**
- Modify: `skills/vgc-team-audit/SKILL.md`

- [ ] Make the output sections explicit and ordered.
- [ ] Add section-level requirements for `Top Findings`, `Team Identity`, `Matchup Holes`, `Recommended Changes`, and `Residual Risk`.
- [ ] Make findings-first, identity-preserving, and smallest-useful-fix behavior explicit in workflow and rules.

### Task 2: Strengthen the supporting references

**Files:**
- Modify: `skills/vgc-team-audit/references/audit-checklist.md`
- Modify: `skills/vgc-team-audit/references/output-rubric.md`

- [ ] Turn the checklist into reusable audit questions rather than a short bullet dump.
- [ ] Tighten the rubric so it rewards findings-first structure and residual-risk honesty.
- [ ] Add weak-pattern checks for filler praise, vague synergy talk, and identity-erasing rewrites.

### Task 3: Refresh examples and runtime metadata

**Files:**
- Modify: `skills/vgc-team-audit/examples/good-example.md`
- Modify: `skills/vgc-team-audit/examples/good-example-02.md`
- Modify: `skills/vgc-team-audit/examples/failure-example.md`
- Modify: `skills/vgc-team-audit/agents/openai.yaml`

- [ ] Make the good examples teach targeted, identity-preserving fixes.
- [ ] Make the failure example teach what not to do.
- [ ] Update UI metadata so it matches the revised contract.

### Task 4: Tighten fixed eval expectations

**Files:**
- Modify: `data/fixtures/evals/team-audit/case-01.md`
- Modify: `data/fixtures/evals/team-audit/case-02.md`
- Modify: `data/fixtures/evals/team-audit/case-03.md`
- Modify: `data/rubrics/team-audit-rubric.md`

- [ ] Add checks that reject filler praise, vague synergy language, and identity-erasing rewrites.
- [ ] Keep the cases centered on targeted fixes and honest residual risk.
- [ ] Update the rubric only where the older language no longer matches the contract.
