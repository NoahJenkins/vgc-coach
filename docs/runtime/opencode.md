# OpenCode Runtime

OpenCode support in this repo is an additive adapter over the same shared skill packages used by Codex and Claude Code.

## Loading Model

- Repo-wide product and workflow rules still live in `AGENTS.md`.
- `opencode.json` should load this file through the `instructions` field so OpenCode gets runtime-specific behavior without duplicating the shared contract.
- OpenCode scans `.opencode/skills/`, `.claude/skills/`, and `.agents/skills/` for project skills.
- Because this repo keeps Codex and Claude discovery shims with the same shared `vgc-*` names, OpenCode support should expose unique wrapper names under `.opencode/skills/opencode-vgc-*/`.
- Each OpenCode wrapper should point the model back to the canonical shared files under `skills/` and `docs/` instead of duplicating coaching logic.
- `opencode.json` should deny the shared `vgc-*` names and allow only `opencode-vgc-*` so OpenCode has one unambiguous VGC skill namespace in this repo.
- The installable OpenCode package lives under `plugins/vgc-coach-opencode/`, and the repo-root `package.json` exposes it for git-based plugin installs.

## Adapter Rules

- Reuse `AGENTS.md`, `skills/`, `data/fixtures/`, and `data/rubrics/`.
- Keep OpenCode-specific behavior in this file, `.opencode/commands/`, and thin `.opencode/skills/opencode-vgc-*/` wrappers only.
- Keep `.opencode/skills/` as an OpenCode discovery layer, not a second skill implementation tree.
- Avoid OpenCode-only forks of the coaching logic unless a real runtime limitation forces them.

## Expected Invocation Model

- OpenCode should be able to discover the project skills from `.opencode/skills/opencode-vgc-*/`.
- Project slash commands under `.opencode/commands/` should provide a first-class path for the five MVP skills:
  - `/vgc-meta-research`
  - `/vgc-team-builder`
  - `/vgc-team-audit`
  - `/vgc-lead-planner`
  - `/vgc-battle-review`
- Those commands should route through the `opencode-vgc-*` wrappers, which then read the shared skill packages and references directly from `skills/` and `docs/`.
- Natural-language requests should still be able to trigger the same shared skills when the descriptions match.

## Current-Info And Sourcing Rules

- Current format, legality, and meta claims are time-sensitive; verify them live before presenting them as current.
- Prefer official rules sources over community sources.
- Use community sources for usage, trends, and archetype interpretation only after format truth is locked.
- Use absolute dates when clarifying “current” claims.
- Distinguish sourced facts from inference explicitly.

## Tooling Boundary

- `vgc-calcs-assistant` exact-browser support still depends on local `agent-browser` plus `python3 tools/browser_damage_calc.py`.
- In OpenCode MVP, exact damage, KO, and survival support is only acceptable when that local tool chain is available and working.
- If OpenCode cannot use the local browser/tool path because of missing install, missing permissions, or runtime mismatch, say the exact path is blocked or unverified and fall back to assumption-framed guidance.
- Speed checks remain assumption-framed unless a verified exact backend is added later.

## Validation Expectations

- When changing shared skill logic, validate against the existing fixed eval cases and rubrics.
- For OpenCode-specific support changes, at minimum verify project command discovery, wrapper-skill discovery through `.opencode/skills/opencode-vgc-*/`, shared file reads from `skills/` and `docs/`, and one representative command invocation.
- Use [OpenCode Team Builder Live Checklist](../evals/opencode-team-builder-live-checklist.md) when pressure-testing `vgc-team-builder` behavior in OpenCode.

## Install

Add the repo as a git-installed plugin in `opencode.json`:

```json
{
  "plugin": ["vgc-coach-opencode@git+https://github.com/NoahJenkins/vgc-coach.git"]
}
```

Restart OpenCode after editing the config.

## Update

If you keep the install unpinned, OpenCode refreshes the plugin when it reinstalls from the git source on restart.

If you pin to a release tag, update the ref and restart:

```json
{
  "plugin": ["vgc-coach-opencode@git+https://github.com/NoahJenkins/vgc-coach.git#v0.1.0"]
}
```

## Verify

Use the native skill tool to confirm the plugin-registered skills are visible:

```text
use skill tool to list skills
```

You should see the VGC Coach plugin namespace and its generated skills after restart.
