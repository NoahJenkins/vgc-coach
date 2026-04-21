# Claude Code Runtime

Claude Code support in this repo is a thin adapter over the same shared skill packages used by Codex.

## Loading Model

- Claude project memory lives in `.claude/CLAUDE.md`.
- Repo-wide product and workflow rules still live in `AGENTS.md`; `.claude/CLAUDE.md` should point Claude back to that file instead of duplicating it.
- Claude project skills live in `.claude/skills/<skill-name>/`.
- Each Claude skill entry should resolve back to the canonical package under `skills/<skill-name>/`.
- `.claude/docs` exists as a shim back to the real `docs/` tree so shared relative references inside `SKILL.md` continue to work when Claude loads skills from `.claude/skills/`.
- The distributable Claude plugin lives under `plugins/vgc-coach-claude/`, and this repo exposes it through `.claude-plugin/marketplace.json`.

## Adapter Rules

- Reuse `AGENTS.md`, `skills/`, `data/fixtures/`, and `data/rubrics/`.
- Keep Claude-specific instruction differences in this file and `.claude/CLAUDE.md` only.
- Do not fork shared coaching logic into Claude-only copies unless a Claude-specific limitation forces it.
- Keep `.claude/skills/` as a discovery layer, not a second editable skill tree.

## Expected Invocation Model

- Claude should be able to discover the project skills automatically from `.claude/skills/`.
- Direct invocation should work through slash commands such as `/vgc-meta-research`, `/vgc-team-builder`, and `/vgc-team-audit`.
- Natural-language requests should still be able to auto-trigger the matching skill when the frontmatter description is relevant.
- Shared `SKILL.md` files remain the source of truth for output shape and behavioral rules.

## Current-Info And Sourcing Rules

- Current format, legality, and meta claims are time-sensitive; verify them live before presenting them as current.
- Prefer official rules sources over community sources.
- Use community sources for usage, trends, and archetype interpretation only after format truth is locked.
- Use absolute dates when clarifying “current” claims.
- Distinguish sourced facts from inference explicitly.

## Tooling Boundary

- `vgc-calcs-assistant` exact-browser support still depends on local `agent-browser` plus `python3 tools/browser_damage_calc.py`.
- In Claude MVP, exact damage, KO, and survival support is only acceptable when that local tool chain is available and working.
- If Claude cannot use the local browser/tool path because of missing install, missing permissions, or runtime mismatch, say the exact path is blocked or unverified and fall back to assumption-framed guidance.
- Speed checks remain assumption-framed unless a verified exact backend is added later.

## Validation Expectations

- When changing shared skill logic, validate against the existing fixed eval cases and rubrics.
- For Claude-specific support changes, at minimum verify skill discovery, representative direct invocation, and reference-path resolution from `.claude/skills/`.

## Install

Add the repo marketplace, then install the packaged plugin:

```bash
claude plugin marketplace add NoahJenkins/vgc-coach --sparse .claude-plugin plugins
claude plugin install vgc-coach-claude@vgc-coach
```

## Update

Refresh the marketplace and installed plugin version:

```bash
claude plugin marketplace update vgc-coach
claude plugin update vgc-coach-claude@vgc-coach
```

If Claude reports a new version was installed, run `/reload-plugins`.

## Verify

Test the packaged plugin directly from this repo during development:

```bash
claude --plugin-dir ./plugins/vgc-coach-claude -p "/vgc-coach-claude:vgc-team-builder Mega Blastoise"
```

That command should load the generated plugin package and invoke the packaged team-builder skill through Claude's plugin namespace.
