# Contributing To VGC Coach

VGC Coach is open source under [Apache-2.0](./LICENSE). Focused contributions are welcome.

This repo is a shared coaching skill workspace first. The main goal is to improve reusable skill quality without forking the same coaching logic across runtimes.

## Before You Open An Issue

- use the issue templates under `.github/ISSUE_TEMPLATE/`
- keep reports focused on one bug, gap, or proposal
- do not post secrets or sensitive data in public issues
- read [SECURITY.md](./SECURITY.md) before reporting a vulnerability

## Good Contribution Scope

Prefer small, reviewable changes such as:

- tightening a shared skill contract under `skills/`
- improving supporting references or examples under `docs/skills/`
- strengthening eval fixtures under `data/fixtures/evals/`
- sharpening rubrics under `data/rubrics/`
- correcting repo docs so they match the live tree
- fixing thin runtime adapters when they no longer match the shared skill packages

For larger direction changes, open an issue or discussion first so the repo contract stays coherent.

## Repo Rules That Matter

- Keep `skills/` as the only canonical editable source for shared coaching logic.
- Keep `plugins/` and marketplace metadata generated. Refresh them with `python3 tools/build_plugins.py build` instead of editing package copies by hand.
- Keep `.agents/skills/`, `.claude/skills/`, and `.opencode/skills/` thin. Do not turn them into separate skill trees.
- Do not add runtime-specific forks unless a real runtime limitation forces it.
- Preserve the output contract in a skill's `SKILL.md` unless the change intentionally updates that contract.
- Do not invent legality, meta, usage, matchup, or calc facts.
- When current-format claims are involved, prefer official rules sources first and label inference clearly.

## Validation Expectations

If your change affects skill behavior, validate it against the relevant fixed eval cases and rubric:

- fixtures: `data/fixtures/evals/`
- rubrics: `data/rubrics/`

If your change affects runtime support, also verify the matching discovery layer and runtime docs:

- Codex: `.agents/skills/` and `docs/runtime/codex.md`
- Claude Code: `.claude/skills/` and `docs/runtime/claude-code.md`
- OpenCode: `.opencode/skills/`, `.opencode/commands/`, `opencode.json`, and `docs/runtime/opencode.md`

If your change affects packaged installs or runtime metadata, also refresh and verify the generated plugin outputs:

- `python3 tools/build_plugins.py build`
- `python3 tools/build_plugins.py check`
- `python3 -m unittest tests.test_build_plugins`

If your change touches exact-browser calc behavior, preserve the current limitation honestly: v1 exact support is only for damage, KO, and survival. Speed guidance is still assumption-framed unless a verified exact backend is added.

## Pull Request Checklist

Before opening a PR:

- keep the change focused and avoid unrelated cleanup
- update docs when behavior or public onboarding changes
- regenerate plugin packages and release notes when changing shared skill content or runtime packaging
- verify any paths and links you touched still exist
- make sure runtime wrapper docs still match the live repo
- explain what changed, why it changed, and how you validated it

By submitting a contribution, you agree that your work will be licensed under the repository's Apache-2.0 license.
