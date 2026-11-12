---
name: ship
description: Take a change in this repository from request to a merged pull request with no person in the loop. Use for every change in this repository, and when the user says "ship".
---

# Ship

Finished work in this repository is a merged pull request. When `AGENTS.md`
sets `Mode: stop at ready`, it is a pull request that is ready to merge.
Nobody watches the thread. Do not stop between steps.

## Steps

1. **Branch.** Start a new branch from the latest `origin/main`. Use a worktree
   when the main checkout has other changes. Make the smallest change that
   does the goal.
2. **Prove it.** See "Proof".
3. **File the PR.** See "Pull request".
4. **Queue the merge.** In `auto-merge` mode, run
   `gh pr merge <n> --auto --squash`. GitHub merges when the required checks
   pass. Never use `--admin` or another bypass. In `stop at ready` mode, do
   not queue a merge.
5. **Watch.** In T3 Code, call `watch_pull_request` and end the turn. It wakes
   you when checks fail or pass, and on reviews, comments, and conflicts.
   Elsewhere, run `gh pr checks <n> --required --watch`, then read new reviews
   and comments. Never write your own polling loop.
6. **Fix.** On each wake, handle the news (see "Findings"). Get proof for each
   fix before you push. If `gh pr view <n> --json mergeStateStatus` shows
   `BEHIND`, run `gh pr update-branch <n>`.
7. **Finish.** The work is done when the PR is merged. In `stop at ready`
   mode, it is done when the required checks pass and no finding is open.
   Call `unwatch_pull_request` before you stop for any other reason. Report
   the PR link, the merge commit or ready state, the proof, and each decision
   you made.

## Proof

Proof is evidence that you saw in this session: command output, a
reproduction, or a screenshot.

- Reproduce the failure, fix it, then see the same reproduction pass.
- Run the checks that CI runs for the files you changed.
- For UI or content changes, run the app and look at the result.
- Obey this repository's test rules. This skill does not permit a test that
  `AGENTS.md` or `CONTRIBUTING.md` forbids.

## Pull request

- Make sure that no PR exists for the branch.
- Title: match recent merged PR titles. Say why the change matters, not which
  files changed.
- Body: match recent merged PRs. Start with the problem in one or two plain
  sentences, then the fix. Add one line,
  `Proof: <what you ran or saw>`. End with `Created with <model> in <harness>.`
  Use the model name that the harness reports.
- Open a real PR, not a draft, so that review runs.
- Make sure that the title and body contain no secrets.

## Findings

Act on check results for the latest push only. Act on every unresolved review
thread and every comment without a reply, whatever its age.

- Examine each review finding against the code before you change anything.
- Fix real bugs in the intended case with the smallest change. Prefer a fix
  that removes or narrows code.
- Decline the rest in a reply with a one-line reason: other paths, rare cases,
  extra tests or guards, small performance costs. List them as follow-ups in
  the report.
- For a failed check, find if the code or the infrastructure caused it. Rerun
  an infrastructure failure one time with `gh run rerun <id> --failed`.
- Start each comment that you post with `> 🤖 <model>, for Noah` on its own
  line.

## Asking

Ask only when you cannot continue alone:

- You cannot prove the change.
- The goal is not clear, and the result depends on it.
- The next step is outside this task: deleting data, changing repository
  settings or secrets, touching systems outside the repository, closing a PR,
  or force-pushing a branch that you did not create.
- The PR gets the `needs-human` label, or the same check fails after two fixes.

Use the question tool (`AskUserQuestion` in Claude Code, `request_user_input`
in Codex). Include the PR link, the blocker, and the options, with your
recommendation first. If there is no question tool or no answer, run
`gh pr merge <n> --disable-auto`, leave the PR open, and start the final
message with the question. Decide all other things yourself, and list them in
the report.
