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

1. Complete the isolated virtual-environment setup in [CONTRIBUTING.md](../../CONTRIBUTING.md#local-development-setup).
2. Pick one skill to change.
3. Run the fixed eval cases for that skill with `python3 tools/eval_skill.py --skill <skill-name> --provider github-token --model claude-sonnet-5.5 --profile manual`.
4. Review failures by category, not just by score.
5. Update the skill instructions or examples.
6. Re-run the same eval cases.
7. Record regressions before merging changes.

For a bounded smoke test, add `--case-limit 1 --session-timeout 180`. Here `--session-timeout` means inactivity timeout, not total wall-clock time. Pass a model that the Copilot account currently offers; `gpt-5.4` and `gpt-5.4-mini` are no longer available. The examples use `claude-sonnet-5.5`.

## Local Reports

- `python3 tools/eval_skill.py` writes `run-status.json`, `result.json`, `summary.md`, and per-case `research-trace.json` files under `.artifacts/autoresearch/<date>/<skill>/standalone-eval/`.
- `python3 tools/full_eval.py` runs the whole configured local suite by default and writes the aggregate `run-status.json`, `result.json`, and `summary.md` under `.artifacts/autoresearch/<date>/full-eval/`.
- Full-suite runs also write one per-skill report directory under `.artifacts/autoresearch/<date>/full-eval/skills/<skill>/`.
- Both local runners clear their target artifact directory before each run so stale case folders or old success reports do not survive a rerun.
- `result.json` now includes `verification_state`, `research_trace_summary`, and the fixed score scale descriptor so a run can be judged on evidence quality instead of score alone.

## Local Autoresearch Harness

The repo has no hosted autoresearch workflow. The scheduled GitHub workflow was removed on 2026-10-30 to avoid recurring model cost. Run `python3 tools/autoresearch.py` locally when you want an improvement pass; each run uses your own Copilot or OpenAI credentials and costs model requests.

With `--profile daily_sentinel`, the harness evaluates one configured sentinel case per priority skill and skips the improve attempt entirely when the baseline is both rubric-clean and evidence-valid. Because live web research fails closed, currentness-sensitive sentinel cases report `inconclusive` rather than clean.

- `--skill auto` rotates across the current MVP priority skills one at a time.
- It evaluates the baseline behavior first.
- It treats missing live-research evidence on currentness-sensitive cases as `inconclusive`, not clean.
- It uses a fixed per-dimension grading scale of `0..2` and rejects mismatched grader totals.
- If a sentinel candidate looks better, it must pass a follow-up full-skill confirmation run before it can become PR-eligible.
- It keeps generated plugin outputs out of the agent edit scope; rebuild them with `python3 tools/build_plugins.py build` after accepting a candidate.

## Rule

A skill is not better just because it sounds smoother. It is better when it scores better against fixed cases without increasing hallucination or stale-source risk.
