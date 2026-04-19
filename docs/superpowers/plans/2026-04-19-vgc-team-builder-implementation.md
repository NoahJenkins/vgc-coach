# VGC Team Builder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade `skills/vgc-team-builder/` from a thin package into a stronger recommendation-first skill that produces one primary draft, lightweight per-slot set direction, honest weak-request handling, and repo-aligned evaluation support.

**Architecture:** Keep the skill core in `skills/vgc-team-builder/SKILL.md`, move repeatable detail into `references/`, preserve the lightweight example-driven package shape already used by the stronger MVP skills, and validate the finished package with the `skill-creator` scripts plus the repo’s fixed team-builder fixtures. Do not add runtime-specific forks or heavy tooling in this batch.

**Tech Stack:** Markdown skill files, repo-local eval fixtures and rubrics, `skill-creator` validation scripts, Git.

---

## File Structure

### Existing files to modify

- `skills/vgc-team-builder/SKILL.md`
  Responsibility: primary trigger, contract, workflow, output order, freshness rules, and main behavioral constraints.
- `skills/vgc-team-builder/references/build-principles.md`
  Responsibility: builder-specific decision rules that are too detailed for `SKILL.md`.
- `skills/vgc-team-builder/references/output-rubric.md`
  Responsibility: evaluation criteria for a strong final response.
- `skills/vgc-team-builder/examples/good-example.md`
  Responsibility: positive example for anti-meta requested-mon handling.
- `skills/vgc-team-builder/examples/good-example-02.md`
  Responsibility: positive example for a role-player build request.
- `skills/vgc-team-builder/examples/failure-example.md`
  Responsibility: negative example showing contract and recommendation failures.
- `skills/vgc-team-builder/agents/openai.yaml`
  Responsibility: UI-facing metadata and default prompt.

### Existing files to verify against

- `docs/superpowers/specs/2026-04-19-vgc-team-builder-design.md`
  Responsibility: approved design source of truth.
- `data/rubrics/team-builder-rubric.md`
  Responsibility: repo-local scoring expectations.
- `data/fixtures/evals/team-builder/case-01.md`
- `data/fixtures/evals/team-builder/case-02.md`
- `data/fixtures/evals/team-builder/case-03.md`
  Responsibility: fixed coverage for requested-mon honesty, one-draft output, and practical usefulness.

### No new files in this batch unless blocked

- Do not add new runtime docs.
- Do not add new tool scripts.
- Do not add extra skill docs outside the existing `references/`, `examples/`, and `agents/` package shape.

## Task 1: Rewrite the core skill contract in `SKILL.md`

**Files:**
- Modify: `skills/vgc-team-builder/SKILL.md`
- Verify against: `docs/superpowers/specs/2026-04-19-vgc-team-builder-design.md`

- [ ] **Step 1: Write the failing contract checklist in a local scratch note**

Create a local scratch checklist for the current `SKILL.md` and mark these expected failures before editing:

```markdown
- [ ] Output contract includes `Set Direction`
- [ ] One-primary-draft rule is explicit
- [ ] Weak-request pivot rule is explicit
- [ ] Optional swaps are confined to `Weaknesses and Next Refinements`
- [ ] Matchup guidance is shell-specific, not generic
```

Expected result: at least the first four items are not yet satisfied by the current file.

- [ ] **Step 2: Re-read the current skill body and confirm the gaps**

Run: `sed -n '1,260p' skills/vgc-team-builder/SKILL.md`

Expected: the current file still ends its output contract at `Why Each Slot Exists`, `Matchup Notes`, and `Weaknesses and Next Refinements`, with no `Set Direction` section and no explicit nearest-viable-version pivot rule.

- [ ] **Step 3: Rewrite `SKILL.md` to match the approved design**

Replace the body so it includes all of the following exact content changes:

```markdown
## Overview

Use this skill to build **one practical recommended team** for Pokemon Champions around a real user goal.

This is a recommendation-first skill. It should commit to one primary draft, explain how that team is supposed to function, and stay honest when a requested mon or concept is weak.

## Inputs

Accept:

- target mons
- target strategy or archetype
- playstyle preference
- anti-meta goals
- avoid list
- optional event or ladder context

If the user does not specify format, default to the current Pokemon Champions regulation and say so.

## Output Contract

Always return these sections in this order:

1. `Build Goal`
2. `Recommended Team`
3. `Role Map`
4. `Set Direction`
5. `Why Each Slot Exists`
6. `Matchup Notes`
7. `Weaknesses and Next Refinements`

## Workflow

1. Lock the active format and major meta pressures first.
2. Identify the real build goal behind the request before choosing slots.
3. Build around one clear team identity, not six individually reasonable picks.
4. Recommend one primary draft only.
5. Keep the requested mon or concept only when it still supports one coherent team.
6. If the request breaks team quality too hard, say so directly and pivot to the nearest viable version.
7. Give lightweight set direction for each slot so the draft is testable immediately.
8. End with the real weaknesses and likely next refinements instead of pretending the build is solved.

## Build Checklist

- Read [references/build-principles.md](references/build-principles.md) before finalizing the team.
- Cover speed or tempo control, board control, damage profile, and matchup intent.
- Keep optional swaps inside `Weaknesses and Next Refinements`, not in the main recommendation.
- Avoid generic six-goodstuff recommendations with no structure.

## Freshness Policy

- Use live web verification by default when current meta context materially affects the build.
- Do not claim a mon or shell is well-positioned right now without checking.
- Label inference when a positioning claim is not directly sourced.
- If the metagame is moving fast, say the build is a current best read rather than a solved shell.

## Output Quality Bar

- Read [references/output-rubric.md](references/output-rubric.md) when tightening the response.
- Be competitive-direct.
- Explain how all six slots support the same plan.
- Keep set direction lightweight and practical rather than export-level unless the user explicitly asks for a full build.

## Rules

- recommend one primary draft only
- keep the requested idea only when it still makes a coherent team
- be explicit when pivoting away from a weak request
- keep matchup notes tied to the actual shell
- do not hide unresolved weaknesses

## Common Mistakes

- forcing the requested mon into a shell where it does not belong
- giving multiple half-committed versions instead of one real recommendation
- listing six mons without role logic or usable set direction
- ignoring what the current field actually punishes
- turning the refinement section into a second team
```

- [ ] **Step 4: Run a direct file check**

Run: `sed -n '1,260p' skills/vgc-team-builder/SKILL.md`

Expected: `Set Direction` appears in the output contract and the nearest-viable-version rule is explicit in `Workflow` and `Rules`.

- [ ] **Step 5: Commit the core skill rewrite**

```bash
git add skills/vgc-team-builder/SKILL.md
git commit -m "feat: strengthen vgc team builder contract"
```

## Task 2: Tighten the supporting references for repeatable team-building behavior

**Files:**
- Modify: `skills/vgc-team-builder/references/build-principles.md`
- Modify: `skills/vgc-team-builder/references/output-rubric.md`

- [ ] **Step 1: Write the failing reference checklist**

Use this checklist before editing:

```markdown
- [ ] Build principles mention one-primary-draft behavior
- [ ] Build principles mention nearest-viable-version pivots
- [ ] Output rubric rewards lightweight set direction
- [ ] Output rubric penalizes branchy alternate builds
```

Expected: at least two items fail against the current files.

- [ ] **Step 2: Update `build-principles.md`**

Replace or extend the file so it includes these decision rules:

```markdown
## Recommendation Discipline

- Build one primary team, not a menu of branches.
- If you mention optional swaps, keep them for the final refinement section only.

## Requested Mon Handling

- If the requested mon is good in the requested role, commit to it.
- If the requested mon is weak but salvageable, say so and build the best honest shell.
- If the requested ask is not realistically viable, explain that directly and pivot to the nearest viable version that preserves the user goal as much as possible.

## Set Direction Standard

Each final build should provide lightweight set direction for every slot:

- likely role framing
- likely item direction
- move or utility emphasis
- tera-style or equivalent positioning direction when relevant

Do not turn this into a full export unless the user asks for one.
```

- [ ] **Step 3: Update `output-rubric.md`**

Replace or extend the rubric so it includes these exact bullets:

```markdown
A strong team-builder answer:

- states the build goal clearly
- recommends one real team
- gives every slot a concrete job
- includes lightweight set direction for each slot
- explains matchup intent
- admits real weaknesses

A weak answer:

- gives a pile of reasonable mons without structure
- hides the requested mon's limitations
- branches into multiple half-committed versions
- gives roster-only output with no practical set direction
- avoids making an actual recommendation
```

- [ ] **Step 4: Run a direct file check**

Run: `sed -n '1,240p' skills/vgc-team-builder/references/build-principles.md && printf '\n---\n' && sed -n '1,220p' skills/vgc-team-builder/references/output-rubric.md`

Expected: both files now reinforce one-primary-draft behavior and lightweight set direction.

- [ ] **Step 5: Commit the reference updates**

```bash
git add skills/vgc-team-builder/references/build-principles.md skills/vgc-team-builder/references/output-rubric.md
git commit -m "feat: tighten vgc team builder reference rules"
```

## Task 3: Refresh examples so they teach the new contract

**Files:**
- Modify: `skills/vgc-team-builder/examples/good-example.md`
- Modify: `skills/vgc-team-builder/examples/good-example-02.md`
- Modify: `skills/vgc-team-builder/examples/failure-example.md`

- [ ] **Step 1: Confirm baseline example gaps**

Run: `find skills/vgc-team-builder/examples -maxdepth 1 -type f | sort | xargs -I{} sh -c 'printf "=== %s ===\n" "$1"; sed -n "1,200p" "$1"' sh {}`

Expected: the good examples talk about coherent recommendations, but none explicitly teach `Set Direction` or nearest-viable-version pivots.

- [ ] **Step 2: Rewrite the first good example**

Replace the explanation with this content:

```markdown
# Good Example 1

Request:

`Build me a Champions anti-meta balance team around Sableye.`

Why this is good:

- keeps the requested mon central only if it still earns a real role
- gives one recommended shell instead of multiple branches
- includes lightweight set direction so the team can be tested immediately
- explains why Sableye belongs on that specific team
- acknowledges the Dark-type Prankster problem instead of hiding it
```

- [ ] **Step 3: Rewrite the second good example**

Replace the explanation with this content:

```markdown
# Good Example 2

Request:

`I want to use Hisuian Zoroark as a Fake Out bait and speed-control piece. Build the best shell for it right now.`

Why this is good:

- turns a player idea into one practical team identity
- evaluates whether the mon is a real role player in the current field
- gives lightweight set direction for how each slot supports that plan
- keeps the final recommendation sharp and matchup-aware
```

- [ ] **Step 4: Rewrite the failure example**

Replace the file with:

```markdown
# Failure Example

Bad behavior:

- jams the requested mon into an unrelated team with no clear job
- drops the requested idea without explaining the pivot
- gives three half-baked versions instead of one real recommendation
- lists six mons with no usable set direction
- pretends obvious weaknesses do not exist
```

- [ ] **Step 5: Run a direct file check**

Run: `find skills/vgc-team-builder/examples -maxdepth 1 -type f | sort | xargs -I{} sh -c 'printf "=== %s ===\n" "$1"; sed -n "1,200p" "$1"' sh {}`

Expected: the examples now teach one-primary-draft behavior, set direction, and honest pivot handling.

- [ ] **Step 6: Commit the example refresh**

```bash
git add skills/vgc-team-builder/examples/good-example.md skills/vgc-team-builder/examples/good-example-02.md skills/vgc-team-builder/examples/failure-example.md
git commit -m "feat: refresh vgc team builder examples"
```

## Task 4: Refresh UI metadata and validate the skill package

**Files:**
- Modify: `skills/vgc-team-builder/agents/openai.yaml`
- Verify: `skills/vgc-team-builder/SKILL.md`
- Verify: `data/rubrics/team-builder-rubric.md`
- Verify: `data/fixtures/evals/team-builder/case-01.md`
- Verify: `data/fixtures/evals/team-builder/case-02.md`
- Verify: `data/fixtures/evals/team-builder/case-03.md`

- [ ] **Step 1: Regenerate `agents/openai.yaml` using `skill-creator`**

Run:

```bash
python /Users/noahjenkins/.codex/skills/.system/skill-creator/scripts/generate_openai_yaml.py \
  skills/vgc-team-builder \
  --interface display_name="VGC Team Builder" \
  --interface short_description="Build one coherent Champions team" \
  --interface default_prompt="Use $vgc-team-builder to build one practical Pokemon Champions team around my target mon, strategy, or anti-meta goal."
```

Expected: `[OK] Created agents/openai.yaml`

- [ ] **Step 2: Validate the skill folder**

Run:

```bash
python /Users/noahjenkins/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/vgc-team-builder
```

Expected: `Skill is valid!`

- [ ] **Step 3: Run a repo-local fixture review against the finished package**

Run:

```bash
sed -n '1,260p' skills/vgc-team-builder/SKILL.md
printf '\n---\n'
sed -n '1,200p' data/rubrics/team-builder-rubric.md
printf '\n---\n'
find data/fixtures/evals/team-builder -maxdepth 1 -type f | sort | xargs -I{} sh -c 'printf "=== %s ===\n" "$1"; sed -n "1,200p" "$1"' sh {}
```

Use this review checklist and do not proceed until every item is true:

```markdown
- [ ] Output contract includes `Set Direction`
- [ ] Skill commits to one primary draft
- [ ] Skill teaches explicit honest pivots for weak requests
- [ ] Rubric still matches the strengthened contract
- [ ] Eval cases still cover the main failure modes
```

- [ ] **Step 4: Commit the metadata and validation pass**

```bash
git add skills/vgc-team-builder/agents/openai.yaml skills/vgc-team-builder/SKILL.md skills/vgc-team-builder/references/build-principles.md skills/vgc-team-builder/references/output-rubric.md skills/vgc-team-builder/examples/good-example.md skills/vgc-team-builder/examples/good-example-02.md skills/vgc-team-builder/examples/failure-example.md
git commit -m "chore: validate vgc team builder package"
```

## Self-Review

### Spec coverage

- `one primary recommended draft only` is implemented in Task 1 and reinforced in Tasks 2-4.
- `lightweight set direction for each slot` is implemented in Task 1 and reinforced in Tasks 2-4.
- `keep request only when coherent, otherwise pivot honestly` is implemented in Task 1 and reinforced in Tasks 2-4.
- `optional swaps only in Weaknesses and Next Refinements` is implemented in Tasks 1-2.
- `metadata integrity and skill validation using skill-creator` is implemented in Task 4.

### Placeholder scan

- No `TODO`, `TBD`, or vague “handle appropriately” steps remain.
- Every command is concrete.
- Every file path is exact.

### Type and naming consistency

- Output section names match the approved design exactly.
- The plan uses `Set Direction` consistently everywhere.
- The plan uses `nearest viable version` / honest pivot language consistently across skill body, references, and examples.
