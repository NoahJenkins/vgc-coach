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

1. Install the local eval dependency with `python3 -m pip install -r tools/requirements-autoresearch.txt`.
2. Pick one skill to change.
3. Run the fixed eval cases for that skill with `python3 tools/eval_skill.py --skill <skill-name> --provider github-token --model gpt-5.4-mini --profile manual`.
4. Review failures by category, not just by score.
5. Update the skill instructions or examples.
6. Re-run the same eval cases.
7. Record regressions before merging changes.

For a bounded smoke test, add `--case-limit 1 --session-timeout 180`. Here `--session-timeout` means inactivity timeout, not total wall-clock time. For routine manual testing, prefer `gpt-5.4-mini`; keep the scheduled nightly run on `gpt-5.4`.

## Local Reports

- `python3 tools/eval_skill.py` writes `run-status.json`, `result.json`, and `summary.md` under `.artifacts/autoresearch/<date>/<skill>/standalone-eval/`.
- `python3 tools/full_eval.py` runs the whole configured local suite by default and writes the aggregate `run-status.json`, `result.json`, and `summary.md` under `.artifacts/autoresearch/<date>/full-eval/`.
- Full-suite runs also write one per-skill report directory under `.artifacts/autoresearch/<date>/full-eval/skills/<skill>/`.
- Both local runners clear their target artifact directory before each run so stale case folders or old success reports do not survive a rerun.

## Nightly Automation

The repo also ships a nightly GitHub Actions loop in `.github/workflows/nightly-skill-autoresearch.yml`.
Scheduled runs stay in `improve` mode but use the `daily_sentinel` profile, so they evaluate one configured sentinel case per priority skill and skip the improve attempt entirely when the baseline is already clean.

- It rotates across the current MVP priority skills one at a time.
- It evaluates the baseline behavior first.
- It only proposes a draft PR when the candidate score improves without regressions.
- It pins the Copilot SDK model to `gpt-5.4` instead of relying on the account default.
- It keeps generated plugin outputs out of the agent edit scope and refreshes them only in the workflow validation step.

## Rule

A skill is not better just because it sounds smoother. It is better when it scores better against fixed cases without increasing hallucination or stale-source risk.
