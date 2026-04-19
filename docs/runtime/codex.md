# Codex Runtime

Codex is the primary runtime for this repo.

## Loading Model

- Prefer repo-root `AGENTS.md` as the shared operating contract.
- Keep skill logic in `skills/` so Codex can use the same core content as future runtimes.
- Use web verification for current meta, rules, and recommendations.

## Expected Behavior

- Verify current format assumptions before giving meta or legality guidance.
- Distinguish sourced facts from inference.
- Use repo fixtures and rubrics when validating skill changes.

## Runtime-Specific Notes

- Codex can combine local repo artifacts with live web verification cleanly.
- Keep Codex-specific behavior in this file, not inside shared skill logic.

