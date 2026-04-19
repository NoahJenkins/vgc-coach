# Claude Code Runtime

Claude Code support should reuse the same core skill content under `skills/`.

## Adapter Rules

- Reuse repo `AGENTS.md` and shared fixtures.
- Keep Claude-specific instruction differences in this file only.
- Do not fork the skill content unless a Claude-specific limitation forces it.

## Expected Differences

- Tool syntax and connector behavior may differ from Codex.
- Prompt wrappers may need light formatting changes, but the output contracts should stay identical.

