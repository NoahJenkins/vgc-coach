# VGC Coach Claude Adapter

Use [AGENTS.md](../AGENTS.md) as the repo source of truth for product goals, quality bar, and shared operating rules.

Use [docs/runtime/claude-code.md](../docs/runtime/claude-code.md) for Claude-specific behavior in this repo.

## Runtime Contract

- Keep `skills/` as the canonical shared skill source.
- Use `.claude/skills/` only as the Claude discovery layer for those same shared skills.
- Do not create Claude-only forks of the coaching logic unless a Claude limitation forces it.
- Keep runtime-specific differences in `docs/runtime/claude-code.md`, not inside shared skill behavior.

## Coaching Rules

- Treat current format, legality, and meta claims as time-sensitive and verify them live before presenting them as current.
- Prefer official rules sources over community sources.
- Label inference clearly when a claim is not directly sourced.
- Do not invent legality, usage, or matchup facts.

## Tooling Boundary

- `vgc-calcs-assistant` exact-browser support depends on local `agent-browser` plus `python3 tools/browser_damage_calc.py`.
- If that local tool path or permissions are unavailable in Claude, say the exact path is blocked or unverified and fall back to assumption-framed guidance instead of inventing exact results.
