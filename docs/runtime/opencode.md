# OpenCode Runtime

OpenCode support should be treated as a thin adapter over the same shared repo artifacts.

## Adapter Rules

- Reuse `AGENTS.md`, `skills/`, `data/fixtures/`, and `data/rubrics/`.
- Keep OpenCode-specific loading and formatting notes here.
- Avoid runtime-specific copies of the same skill unless absolutely necessary.

## Portability Goal

If a skill works in Codex, the default expectation is that OpenCode support should require only adapter guidance, not a full rewrite.

