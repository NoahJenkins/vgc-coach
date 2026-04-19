# Plugin Eval Workflow

Use `plugin-eval` to measure whether skill changes actually improve output quality.

## What To Evaluate

- format correctness
- current-meta accuracy
- practical usefulness
- coherence of recommendations
- failure handling

## Repo Inputs

- `data/fixtures/evals/`
- `data/rubrics/`
- target `skills/*/SKILL.md`

## Recommended Loop

1. Pick one skill to change.
2. Run the fixed eval cases for that skill.
3. Review failures by category, not just by score.
4. Update the skill instructions or examples.
5. Re-run the same eval cases.
6. Record regressions before merging changes.

## Rule

A skill is not better just because it sounds smoother. It is better when it scores better against fixed cases without increasing hallucination or stale-source risk.

