# Dependabot Rebase

`.github/workflows/dependabot-rebase.yml` asks Dependabot to rebase a pull request that is stuck behind `main`.

Branch protection requires the head branch to be up to date. Auto-merge stays armed, and the checks stay green, but the pull request does not merge once `main` moves. The workflow runs on every push to `main`, on weekdays at 15:17 UTC, and from Actions → Dependabot Rebase → Run workflow.

It comments `@dependabot rebase` only when all of these are true:

- the author is `dependabot[bot]`
- the base branch is `main`
- auto-merge is armed
- GitHub reports `mergeStateStatus` `BEHIND`
- the same major-update rules as `.github/workflows/dependabot-auto-merge.yml` would arm auto-merge

A held major is left alone. That is any update the auto-merge workflow decides to `hold`: npm and pip majors, and a GitHub Actions major whose title and body do not show a major version pair. GitHub Actions majors that the auto-merge workflow arms are rebased.

The workflow posts at most one comment per head SHA. The comment's first line is the command. An HTML comment under it records the SHA. A later run sees that marker and does not comment again until Dependabot pushes a new head.

The workflow does not push, does not call `update-branch`, and does not change branch protection. Dependabot force-pushes the rebase itself. A merge commit from this repository would make Dependabot treat the branch as edited and refuse later rebases. A push made with `GITHUB_TOKEN` would also leave the required checks waiting for approval.

## Why this token exists

Dependabot ignores `@dependabot rebase` when `github-actions[bot]` posts it. Those comments have `author_association` `NONE`. See [dependabot/dependabot-core#9147](https://github.com/dependabot/dependabot-core/issues/9147).

`DEPENDABOT_REBASE_TOKEN` is a fine-grained personal access token for a user who can write to this repository. The comment is then from that user, so Dependabot accepts the command.

Do not put the token in a workflow file, a pull request, or a Dependabot secret. Dependabot secrets are a different store. This workflow reads the Actions secret only.

## Create the token

Use a GitHub account that can write to `NoahJenkins/vgc-coach`. The comment is attributed to that account. A collaborator with write access is `COLLABORATOR`; the repository owner is `OWNER`. Either is enough. An account that cannot write is `NONE`, and Dependabot will ignore the command.

1. Open GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token.
2. Resource owner: `NoahJenkins`.
3. Expiration: 90 days. Do not choose "No expiration" if the screen offers it. A custom date is fine when it is sooner than 90 days. Fine-grained tokens are not renewed in place. Rotation means a new token.
4. Repository access: Only select repositories → `NoahJenkins/vgc-coach`.
5. Repository permissions:
   - Pull requests: Read and write
   - Leave every other permission at No access. GitHub adds Metadata: Read-only on its own. That is required, and it is the only extra permission.
6. Generate the token and copy it. GitHub shows it once.

The Pull requests permission covers the conversation comment (`POST /repos/{owner}/{repo}/issues/{pull_number}/comments`). Do not add Issues, Contents, or Workflows. Contents would let the token push. This workflow must not push.

## Store the secret

In `NoahJenkins/vgc-coach` → Settings → Secrets and variables → Actions → Repository secrets, create:

| Name | Value |
| --- | --- |
| `DEPENDABOT_REBASE_TOKEN` | the token from the step above |

Use a repository secret, not an environment secret. The workflow does not select an environment.

Until this secret exists, the workflow succeeds and emits the notice `DEPENDABOT_REBASE_TOKEN is unset; skipping Dependabot rebases.` It does not comment.

After saving the secret, run the workflow on `main`. A green run that does not show that notice means the token authenticated. The run comments only on a pull request that meets the rules above.

## Rotate the token

Do this before the 90 days are up. An expired token fails the job on the first `gh` call. A missing secret does not fail the job.

1. Generate a new fine-grained token with the same resource owner, the same repository, Pull requests: Read and write, and a new 90-day expiration.
2. Update the existing `DEPENDABOT_REBASE_TOKEN` Actions secret to the new value.
3. Revoke the old token under Developer settings → Fine-grained tokens.
4. Run Dependabot Rebase on `main` again. A green run with no unset notice means the new token works.

If the token leaks, revoke it before updating the secret, then follow the same steps. The workflow never prints the token.
