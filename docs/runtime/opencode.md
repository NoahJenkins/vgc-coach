# OpenCode Runtime

OpenCode support in this repo is an additive adapter over the same shared skill packages used by Codex and Claude Code.

## Loading Model

- Repo-wide product and workflow rules still live in `AGENTS.md`.
- `opencode.json` should load this file through the `instructions` field so OpenCode gets runtime-specific behavior without duplicating the shared contract.
- Project skill discovery should use `.agents/skills/<skill-name>/`, which already resolves back to the canonical packages under `skills/<skill-name>/`.
- `.agents/docs` should shim back to the real `docs/` tree so shared relative references inside `SKILL.md` continue to work if OpenCode resolves skill paths from `.agents/skills/`.
- Do not create a second editable skill tree under `.opencode/skills/` unless OpenCode-specific limits force it later.

## Adapter Rules

- Reuse `AGENTS.md`, `skills/`, `data/fixtures/`, and `data/rubrics/`.
- Keep OpenCode-specific behavior in this file and `.opencode/commands/` only.
- Keep `.agents/skills/` as a discovery layer, not a second skill implementation tree.
- Avoid OpenCode-only forks of the coaching logic unless a real runtime limitation forces them.

## Expected Invocation Model

- OpenCode should be able to discover the project skills from `.agents/skills/`.
- Project slash commands under `.opencode/commands/` should provide a first-class path for the five MVP skills:
  - `/vgc-meta-research`
  - `/vgc-team-builder`
  - `/vgc-team-audit`
  - `/vgc-lead-planner`
  - `/vgc-battle-review`
- Those commands should route back to the shared skill packages instead of re-encoding the coaching logic.
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
- For OpenCode-specific support changes, at minimum verify project command discovery, shared skill discovery through `.agents/skills/`, shared-doc reference resolution, and one representative command invocation.
- Use [OpenCode Team Builder Live Checklist](../evals/opencode-team-builder-live-checklist.md) when pressure-testing `vgc-team-builder` behavior in OpenCode.
