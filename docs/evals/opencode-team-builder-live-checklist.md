# OpenCode Team Builder Live Checklist

Use this checklist when pressure-testing `vgc-team-builder` outputs in OpenCode without `plugin-eval`.

## Goal

Confirm that OpenCode team-builder answers stay inside the shared Champions truth and do not drift into:

- wrong base-form versus Mega-form assumptions
- wrong ability or move-access claims
- illegal current-format item recommendations
- stale or unsupported meta framing
- multi-branch or incoherent roster output

## Prompts To Run

### Prompt 1

`Use $vgc-team-builder to build me an anti-meta rain team with Sableye if it gets Rain Dance. I was thinking Mega Sableye support. Keep items legal for current Champions.`

Pass if:

- the answer confirms current `Regulation M-A` and `Mega Evolution active` first
- the answer verifies the exact form and role-critical assumption before building
- the answer does not treat `Mega Sableye` as if it still had `Prankster`
- the answer does not assume `Rain Dance` access without checking current Champions move data
- the answer pivots cleanly to base `Sableye` or another nearest viable version if Mega support breaks the role
- every recommended item is inside the current Regulation M-A allowlist
- the matchup framing targets the actual current field instead of legacy threats

### Prompt 2

`Use $vgc-team-builder to build around Hisuian Zoroark as a Fake Out bait and speed-control piece. Do not use illegal current-format items.`

Pass if:

- the answer verifies current format state before calling the read current-field or early
- the answer gives one coherent team rather than a pile of alternates
- the answer keeps every recommended item legal for current Champions
- the answer gives practical set direction for all six slots
- the answer explains why the requested mon belongs on that exact shell

### Prompt 3

`Use $vgc-team-builder to build around a weak favorite in current Champions. Be honest if the idea is bad and still give me the nearest viable version.`

Pass if:

- the answer is honest when the request is weak
- the answer does not silently force a bad version of the requested role
- the answer still gives one testable team with clear slot jobs
- the answer labels the result as current-field or inference-heavy appropriately

## Review Standard

Fail the run if any output:

- recommends unsupported current-format items
- assumes a Mega keeps the same ability as the base form
- contradicts itself on move access or legality and then builds anyway
- centers matchup notes on unsupported or irrelevant threats instead of the live field
- produces six individually plausible mons with no shared plan
- hides a broken requested-mon assumption instead of pivoting plainly

## Quick Review Questions

Ask these before accepting the output:

1. Did it lock the current format and mechanics correctly?
2. Did it verify exact form, ability, move access, and item legality for the requested role?
3. Did it target the actual current Reg M-A field?
4. Is this one coherent, testable team?
5. Could a player import and test this immediately without fixing factual errors first?

## Supporting Artifacts

- `docs/skills/shared/references/champions-reg-m-a-legality.md`
- `docs/skills/vgc-team-builder/references/build-principles.md`
- `skills/vgc-team-builder/SKILL.md`
- `data/rubrics/team-builder-rubric.md`
- `data/fixtures/evals/team-builder/case-01.md`
- `data/fixtures/evals/team-builder/case-04.md`
- `data/snapshots/champions-reg-m-a-2026-04-18.json`
