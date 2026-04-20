# Codex Runtime

Codex is the primary runtime for this repo.

## Loading Model

- Prefer repo-root `AGENTS.md` as the shared operating contract.
- Keep canonical skill logic in `skills/` so Codex can share the same core content as future runtimes.
- Expose repo-local Codex skills through `.agents/skills/` as a thin discovery layer that points back to `skills/`.
- Use web verification for current meta, rules, and recommendations.

## Expected Behavior

- Verify current format assumptions before giving meta or legality guidance.
- Distinguish sourced facts from inference.
- Use repo fixtures and rubrics when validating skill changes.

## Runtime-Specific Notes

- Codex can combine local repo artifacts with live web verification cleanly.
- `.agents/skills/` should not become a second editable skill tree; keep it as wrappers or symlinks only.
- Keep Codex-specific behavior in this file, not inside shared skill logic.
