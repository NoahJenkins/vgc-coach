from __future__ import annotations

import re
import shlex
import subprocess
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: str) -> dict:
    return yaml.safe_load((REPO_ROOT / path).read_text())


def workflow_triggers(workflow: dict) -> dict:
    # PyYAML 1.1 treats the unquoted GitHub Actions key `on` as a boolean.
    return workflow.get("on", workflow.get(True, {}))


def marked_region(run: str, begin: str, end: str) -> str:
    start = run.index(begin)
    stop = run.index(end)
    return run[start:stop]


def iter_uses(node):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "uses" and isinstance(value, str):
                yield value.strip()
            else:
                yield from iter_uses(value)
    elif isinstance(node, list):
        for item in node:
            yield from iter_uses(item)


# actions/* and github/* are the GitHub-owned orgs. The only other allowed
# action is the pinned shared review workflow. A 40-char sha is required there
# because a tag would not match the repo's NoahJenkins/.github@* pattern.
ALLOWED_WORKFLOW_USES = re.compile(
    r"^(?:actions/\S+|github/\S+|NoahJenkins/\.github@[0-9a-f]{40})$"
)
REVIEW_GATE_PIN = (
    "NoahJenkins/.github@ae1d7fb9e465587524db10332f390d6abe1c7d37 # v1.1.0"
)


def rebase_workflow() -> dict:
    return load_yaml(".github/workflows/dependabot-rebase.yml")


def rebase_run() -> str:
    steps = rebase_workflow()["jobs"]["request-rebases"]["steps"]
    if len(steps) != 1:
        raise AssertionError(f"expected one rebase step, found {len(steps)}")
    return steps[0]["run"]


def run_bash(script: str, *args: str) -> str:
    completed = subprocess.run(
        ["bash", "-c", script, "decision", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


class DependabotWorkflowPolicyTests(unittest.TestCase):
    def test_routine_and_security_updates_use_separate_catch_all_groups(self):
        config = load_yaml(".github/dependabot.yml")
        update = next(
            item for item in config["updates"] if item["package-ecosystem"] == "npm"
        )

        self.assertEqual(update["directory"], "/site")
        self.assertNotIn("allow", update)
        self.assertEqual(
            update["groups"]["routine-site-dependencies"],
            {
                "applies-to": "version-updates",
                "patterns": ["*"],
                "update-types": ["minor", "patch"],
            },
        )
        self.assertEqual(
            update["groups"]["site-security-updates"],
            {
                "applies-to": "security-updates",
                "patterns": ["*"],
            },
        )

    def test_actions_and_pip_ecosystems_are_grouped_and_weekly(self):
        config = load_yaml(".github/dependabot.yml")
        by_ecosystem = {item["package-ecosystem"]: item for item in config["updates"]}

        self.assertEqual(
            set(by_ecosystem), {"npm", "github-actions", "pip"}
        )
        self.assertEqual(by_ecosystem["github-actions"]["directory"], "/")
        self.assertEqual(by_ecosystem["pip"]["directory"], "/tools")
        for ecosystem, update in by_ecosystem.items():
            with self.subTest(ecosystem=ecosystem):
                self.assertEqual(update["schedule"]["interval"], "weekly")
                # Majors must land in a group the auto-merge workflow recognises.
                majors = [
                    name
                    for name, group in update["groups"].items()
                    if group.get("update-types") == ["major"]
                ]
                self.assertEqual(len(majors), 1)
                self.assertIn("major-updates", majors[0])

    def test_auto_merge_runner_is_restricted_before_runner_allocation(self):
        workflow = load_yaml(".github/workflows/dependabot-auto-merge.yml")
        job = workflow["jobs"]["enable-auto-merge"]
        condition = job["if"]
        trigger = workflow_triggers(workflow)["pull_request_target"]

        self.assertEqual(
            trigger["types"],
            ["opened", "reopened", "synchronize", "ready_for_review"],
        )
        self.assertIn(
            "github.event.pull_request.user.login == 'dependabot[bot]'", condition
        )
        self.assertIn("github.event.pull_request.base.ref == 'main'", condition)
        self.assertIn("github.event.pull_request.draft == false", condition)
        self.assertEqual(job["timeout-minutes"], 5)
        self.assertTrue(workflow["concurrency"]["cancel-in-progress"])

    def test_auto_merge_uses_native_squash_without_closing_exceptions(self):
        workflow = load_yaml(".github/workflows/dependabot-auto-merge.yml")
        steps = workflow["jobs"]["enable-auto-merge"]["steps"]
        commands = "\n".join(step.get("run", "") for step in steps)
        merge_step = next(step for step in steps if step["name"] == "Enable auto-merge")
        merge_command = shlex.split(merge_step["run"])

        self.assertEqual(merge_command[:3], ["gh", "pr", "merge"])
        self.assertIn("--auto", merge_command)
        self.assertIn("--squash", merge_command)
        self.assertNotIn("--admin", merge_command)
        self.assertNotIn("gh pr close", commands)

    def test_auto_merge_holds_non_actions_majors_and_arms_actions_majors(self):
        workflow = load_yaml(".github/workflows/dependabot-auto-merge.yml")
        steps = workflow["jobs"]["enable-auto-merge"]["steps"]
        by_name = {step["name"]: step for step in steps}
        detect = by_name["Detect major updates"]
        decide = by_name["Decide whether to arm auto-merge"]
        enable = by_name["Enable auto-merge"]
        disable = by_name["Disable auto-merge"]

        self.assertIn("major-updates", detect["run"])
        self.assertNotIn("dependency-major", detect["run"])
        self.assertNotIn("Fetch Dependabot metadata", by_name)
        workflow_text = (REPO_ROOT / ".github/workflows/dependabot-auto-merge.yml").read_text()
        self.assertNotIn("fetch-metadata", workflow_text)
        self.assertNotIn("steps.meta", workflow_text)
        for step in steps:
            self.assertNotIn("uses", step)
        self.assertIn(
            'dependabot_update_signals "$HEAD_REF" "$PR_TITLE" "$PR_BODY"',
            detect["run"],
        )
        self.assertIn('echo "ecosystem=${signals[1]}"', detect["run"])
        self.assertIn('echo "update_type=${signals[2]}"', detect["run"])
        self.assertEqual(
            decide["env"]["PACKAGE_ECOSYSTEM"],
            "${{ steps.major.outputs.ecosystem }}",
        )
        self.assertEqual(
            decide["env"]["UPDATE_TYPE"],
            "${{ steps.major.outputs.update_type }}",
        )
        self.assertEqual(
            decide["if"],
            "steps.scope.outputs.eligible == 'true' && steps.major.outcome == 'success'",
        )
        self.assertNotIn("META_OUTCOME", decide["run"])
        self.assertIn(
            'dependabot_merge_decision "$MAJOR" "$PACKAGE_ECOSYSTEM" "$UPDATE_TYPE"',
            decide["run"],
        )
        self.assertLess(
            decide["run"].index('"$decision" = "hold"'),
            decide["run"].index("--add-label dependency-major"),
        )
        self.assertLess(
            decide["run"].index("--add-label dependency-major"),
            decide["run"].index("--remove-label dependency-major"),
        )
        self.assertEqual(
            enable["if"],
            "steps.scope.outputs.eligible == 'true' && steps.update_type.outputs.decision == 'merge'",
        )
        self.assertIn("always()", disable["if"])
        self.assertIn("steps.scope.outcome == 'success'", disable["if"])
        self.assertIn("steps.scope.outputs.eligible != 'true'", disable["if"])
        self.assertIn("steps.update_type.outputs.decision == 'hold'", disable["if"])
        self.assertNotIn("outputs.major", enable["if"])
        self.assertNotIn("--admin", enable["run"])
        self.assertNotIn("--admin", disable["run"])

    def test_merge_decision_arms_actions_majors_and_holds_every_other_major(self):
        workflow = load_yaml(".github/workflows/dependabot-auto-merge.yml")
        steps = workflow["jobs"]["enable-auto-merge"]["steps"]
        run = next(
            step["run"]
            for step in steps
            if step["name"] == "Decide whether to arm auto-merge"
        )
        script = (
            marked_region(
                run,
                "# BEGIN dependabot-merge-decision",
                "# END dependabot-merge-decision",
            )
            + '\ndependabot_merge_decision "$1" "$2" "$3"\n'
        )
        cases = (
            ("true", "github_actions", "version-update:semver-major", "merge"),
            ("true", "github_actions", "version-update:semver-minor", "merge"),
            ("true", "github_actions", "version-update:semver-patch", "merge"),
            ("false", "github_actions", "version-update:semver-major", "merge"),
            ("false", "github_actions", "", "merge"),
            ("true", "github_actions", "", "hold"),
            ("true", "github_actions", "security-update", "hold"),
            ("true", "github-actions", "version-update:semver-major", "hold"),
            ("true", "GITHUB_ACTIONS", "version-update:semver-major", "hold"),
            ("true", "npm", "version-update:semver-major", "hold"),
            ("true", "pip", "version-update:semver-major", "hold"),
            ("true", "docker", "version-update:semver-major", "hold"),
            ("true", "npm_and_yarn", "version-update:semver-major", "hold"),
            ("true", "", "version-update:semver-major", "hold"),
            ("false", "npm", "version-update:semver-major", "merge"),
            ("false", "pip", "", "merge"),
            ("false", "docker", "version-update:semver-major", "merge"),
        )
        for major, ecosystem, update_type, expected in cases:
            with self.subTest(major=major, ecosystem=ecosystem, update_type=update_type):
                self.assertEqual(
                    run_bash(script, major, ecosystem, update_type).strip(),
                    expected,
                )

    def test_auto_merge_limits_changed_files_to_dependency_manifests(self):
        workflow = load_yaml(".github/workflows/dependabot-auto-merge.yml")
        steps = workflow["jobs"]["enable-auto-merge"]["steps"]
        scope_step = next(
            step for step in steps if step["name"].startswith("Check changed files")
        )

        self.assertIn("site/*", scope_step["run"])
        self.assertIn(".github/workflows/*", scope_step["run"])
        self.assertIn("tools/requirements-autoresearch.txt", scope_step["run"])
        self.assertIn("eligible=false", scope_step["run"])
        self.assertEqual(
            next(step for step in steps if step["name"] == "Enable auto-merge")["if"],
            "steps.scope.outputs.eligible == 'true' && steps.update_type.outputs.decision == 'merge'",
        )

    def test_auto_merge_requires_every_commit_to_come_from_dependabot(self):
        workflow = load_yaml(".github/workflows/dependabot-auto-merge.yml")
        steps = workflow["jobs"]["enable-auto-merge"]["steps"]
        scope_run = next(
            step for step in steps if step["name"].startswith("Check changed files")
        )["run"]

        self.assertIn("pulls/$PR_NUMBER/commits", scope_run)
        self.assertIn('"$author" != "dependabot[bot]"', scope_run)
        self.assertIn("--paginate", scope_run)
        self.assertLess(
            scope_run.index("pulls/$PR_NUMBER/commits"),
            scope_run.index("pulls/$PR_NUMBER/files"),
        )

    def test_auto_merge_is_revoked_when_a_later_push_leaves_scope(self):
        workflow = load_yaml(".github/workflows/dependabot-auto-merge.yml")
        steps = workflow["jobs"]["enable-auto-merge"]["steps"]
        disable_step = next(step for step in steps if step["name"] == "Disable auto-merge")

        self.assertIn("steps.scope.outputs.eligible != 'true'", disable_step["if"])
        self.assertIn("autoMergeRequest", disable_step["run"])
        self.assertIn("--disable-auto", disable_step["run"])
        self.assertNotIn("--admin", disable_step["run"])

    def test_release_workflow_never_pushes_to_main_and_is_bounded(self):
        workflow = load_yaml(".github/workflows/plugin-release.yml")
        commands = "\n".join(
            step.get("run", "") for step in workflow["jobs"]["release"]["steps"]
        )

        self.assertNotIn("HEAD:main", commands)
        # An existing tag alone does not prove the release was created.
        self.assertIn("gh release view", commands)
        self.assertEqual(workflow["jobs"]["release"]["timeout-minutes"], 10)
        self.assertIn("concurrency", workflow)
        # Plugin releases start by hand (AGENTS.md), never on a push.
        self.assertEqual(set(workflow_triggers(workflow)), {"workflow_dispatch"})

    def test_required_checks_keep_exact_names_and_run_for_every_main_pr(self):
        expected = {
            ".github/workflows/site-ci.yml": ("site-build", 10),
            ".github/workflows/plugin-package-ci.yml": (
                "plugin-package-check",
                10,
            ),
        }

        for path, (job_name, timeout) in expected.items():
            with self.subTest(path=path):
                workflow = load_yaml(path)
                job = workflow["jobs"][job_name]
                pull_request = workflow_triggers(workflow)["pull_request"]

                self.assertEqual(job["name"], job_name)
                self.assertEqual(job["timeout-minutes"], timeout)
                self.assertEqual(pull_request["branches"], ["main"])
                self.assertNotIn("paths", pull_request)
                self.assertNotIn("paths-ignore", pull_request)
                self.assertTrue(workflow["concurrency"]["cancel-in-progress"])

    def test_update_signals_use_head_ref_and_major_version_pairs(self):
        workflow = load_yaml(".github/workflows/dependabot-auto-merge.yml")
        steps = workflow["jobs"]["enable-auto-merge"]["steps"]
        by_name = {step["name"]: step for step in steps}
        signals_script = (
            marked_region(
                by_name["Detect major updates"]["run"],
                "# BEGIN dependabot-update-signals",
                "# END dependabot-update-signals",
            )
            + '\ndependabot_update_signals "$1" "$2" "$3"\n'
        )
        decision_script = (
            marked_region(
                by_name["Decide whether to arm auto-merge"]["run"],
                "# BEGIN dependabot-merge-decision",
                "# END dependabot-merge-decision",
            )
            + '\ndependabot_merge_decision "$1" "$2" "$3"\n'
        )
        # Release-note noise includes other majors; the PR's own pair still wins.
        actions_group_body = "\n".join(
            (
                "Updates `actions/checkout` from 6.0.2 to 7.0.1",
                "Updates `actions/setup-python` from 6.2.0 to 7.1.0",
                "Bump flatted from 3.3.1 to 3.4.2",
                "Bump docker/login-action from 3.3.0 to 4.2.0",
            )
        )
        cases = (
            (
                "dependabot/github_actions/actions-major-updates-7f603b356f",
                "ci: bump the actions-major-updates group",
                actions_group_body,
                "merge",
            ),
            (
                "dependabot/github_actions/actions/checkout-7.0.1",
                "ci: bump actions/checkout from 6.0.2 to 7.0.1",
                "",
                "merge",
            ),
            (
                "dependabot/github_actions/actions/checkout-5",
                "ci: bump actions/checkout from v4 to v5",
                "",
                "merge",
            ),
            (
                "dependabot/github_actions/actions/checkout-5",
                "Bump `actions/checkout` from `4` to `5`",
                "",
                "merge",
            ),
            (
                "dependabot/github_actions/actions/checkout-6.0.3",
                "ci: bump actions/checkout from 6.0.2 to 6.0.3",
                "",
                "merge",
            ),
            (
                "dependabot/npm_and_yarn/site/next-15.1.0",
                "deps: bump next from 15.0.0 to 15.1.0",
                "",
                "merge",
            ),
            (
                "dependabot/npm_and_yarn/site/site-major-updates-abc",
                "deps: bump the site-major-updates group",
                "Updates `next` from 14.2.5 to 15.0.0",
                "hold",
            ),
            (
                "dependabot/pip/tools/python-major-updates-abc",
                "deps: bump PyYAML from 6.0.3 to 7.0.0",
                "",
                "hold",
            ),
            (
                "dependabot/docker/Dockerfile/nginx-2",
                "build: bump nginx from 1.27 to 2.0",
                "",
                "hold",
            ),
            (
                "dependabot/npm_and_yarn/site/site-major-updates-abc",
                "deps",
                "| `1.2.3` | `2.0.0` |",
                "hold",
            ),
            (
                "dependabot/github-actions/actions/checkout-5",
                "ci: bump",
                "from 4 to 5",
                "hold",
            ),
            (
                "dependabot/GITHUB_ACTIONS/actions/checkout-5",
                "ci: bump",
                "from 4 to 5",
                "hold",
            ),
            (
                "dependabot/github_actions",
                "ci: bump",
                "from 4 to 5",
                "hold",
            ),
            (
                "feature/github_actions-major-updates",
                "ci: bump",
                "from 4 to 5",
                "hold",
            ),
            (
                "dependabot/github_actions/actions-major-updates-abc",
                "ci: bump the actions-major-updates group",
                "No version pair in this body",
                "hold",
            ),
            (
                "dependabot/github_actions/actions-major-updates-abc",
                "ci: bump",
                "Updates `actions/checkout` from 6.0.2 to 6.0.3",
                "hold",
            ),
            (
                "",
                "",
                "",
                "merge",
            ),
        )
        for head_ref, title, body, expected in cases:
            with self.subTest(head_ref=head_ref, title=title):
                lines = run_bash(signals_script, head_ref, title, body).splitlines()
                self.assertEqual(len(lines), 3, lines)
                decision = run_bash(decision_script, *lines).strip()
                self.assertEqual(decision, expected)

    def test_workflow_uses_stay_on_the_actions_allowlist(self):
        workflows = sorted((REPO_ROOT / ".github/workflows").glob("*.yml"))
        self.assertGreaterEqual(len(workflows), 1)
        seen = []
        for path in workflows:
            workflow = load_yaml(path.relative_to(REPO_ROOT).as_posix())
            for uses in iter_uses(workflow):
                seen.append((path.name, uses))
                self.assertRegex(uses, ALLOWED_WORKFLOW_USES)
        self.assertGreaterEqual(len(seen), 1)
        self.assertRegex("actions/checkout@v6", ALLOWED_WORKFLOW_USES)
        self.assertRegex(
            "github/codeql-action/init@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            ALLOWED_WORKFLOW_USES,
        )
        self.assertRegex(
            "NoahJenkins/.github@" + "a" * 40,
            ALLOWED_WORKFLOW_USES,
        )
        for rejected in (
            "dependabot/fetch-metadata@25dd0e34f4fe68f24cc83900b1fe3fe149efef98",
            "NoahJenkins/.github@v1.1.0",
            "NoahJenkins/.github@" + "a" * 39,
            "NoahJenkins/.github@" + "a" * 41,
            "NoahJenkins/.github/review@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "NoahJenkins/other@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "./.github/actions/local",
            "docker://alpine:3.20",
        ):
            with self.subTest(rejected=rejected):
                self.assertNotRegex(rejected, ALLOWED_WORKFLOW_USES)
        review_gate = (REPO_ROOT / ".github/workflows/review-gate.yml").read_text()
        self.assertEqual(review_gate.count(REVIEW_GATE_PIN), 2)

    def test_rebase_workflow_triggers_on_main_push_weekdays_and_dispatch(self):
        workflow = rebase_workflow()
        triggers = workflow_triggers(workflow)
        cron = triggers["schedule"][0]["cron"]
        minute, hour, day_of_month, month, day_of_week = cron.split()

        self.assertEqual(set(triggers), {"push", "schedule", "workflow_dispatch"})
        self.assertEqual(triggers["push"]["branches"], ["main"])
        self.assertEqual(day_of_week, "1-5")
        self.assertNotEqual(day_of_month, "1-5")
        self.assertNotIn("pull_request", triggers)
        self.assertNotIn("pull_request_target", triggers)
        self.assertEqual(workflow["permissions"], {})
        self.assertNotIn("permissions", workflow["jobs"]["request-rebases"])
        self.assertEqual(
            workflow["jobs"]["request-rebases"]["if"],
            "github.ref == 'refs/heads/main'",
        )
        self.assertEqual(workflow["jobs"]["request-rebases"]["timeout-minutes"], 5)
        self.assertFalse(workflow["concurrency"]["cancel-in-progress"])
        self.assertEqual(workflow["concurrency"]["group"], "dependabot-rebase")
        self.assertEqual(list(iter_uses(workflow)), [])
        self.assertEqual(minute, "17")
        self.assertEqual(hour, "15")

    def test_rebase_workflow_uses_the_pat_and_skips_when_the_secret_is_missing(self):
        workflow_text = (REPO_ROOT / ".github/workflows/dependabot-rebase.yml").read_text()
        run = rebase_run()
        notice = run.index(
            'echo "::notice::DEPENDABOT_REBASE_TOKEN is unset; skipping Dependabot rebases."'
        )
        missing_exit = run.index("exit 0")
        export = run.index('export GH_TOKEN="$DEPENDABOT_REBASE_TOKEN"')
        first_gh = run.index("gh pr list")

        self.assertLess(run.index('if [ -z "${DEPENDABOT_REBASE_TOKEN}" ]'), notice)
        self.assertLess(notice, missing_exit)
        self.assertLess(missing_exit, export)
        self.assertLess(export, run.index("unset DEPENDABOT_REBASE_TOKEN"))
        self.assertLess(run.index("unset DEPENDABOT_REBASE_TOKEN"), first_gh)
        self.assertEqual(workflow_text.count("secrets.DEPENDABOT_REBASE_TOKEN"), 1)
        self.assertNotIn("secrets.GITHUB_TOKEN", workflow_text)
        self.assertNotIn("github.token", workflow_text)
        self.assertNotIn("set -x", run)
        self.assertNotIn("git push", run)
        self.assertNotIn("update-branch", run)
        self.assertNotIn("gh pr merge", run)
        self.assertNotIn("--admin", run)
        self.assertNotIn("@dependabot merge", run)
        self.assertNotIn("@dependabot recreate", run)
        self.assertIn("--body-file", run)
        self.assertIn("--app dependabot", run)
        self.assertIn("--limit 100", run)
        self.assertIn('if ! pr_numbers_text="$(gh pr list', run)
        self.assertLess(run.index('if ! pr_numbers_text="$(gh pr list'), run.index("exit 1"))
        self.assertNotIn("pull/82", workflow_text)
        self.assertNotIn("#82", workflow_text)

        completed = subprocess.run(
            ["bash", "-n"],
            input=run,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_rebase_workflow_copies_the_auto_merge_major_policy(self):
        auto = load_yaml(".github/workflows/dependabot-auto-merge.yml")
        auto_steps = auto["jobs"]["enable-auto-merge"]["steps"]
        rebase = rebase_run()
        copied = (
            (
                "Detect major updates",
                "# BEGIN dependabot-update-signals",
                "# END dependabot-update-signals",
            ),
            (
                "Decide whether to arm auto-merge",
                "# BEGIN dependabot-merge-decision",
                "# END dependabot-merge-decision",
            ),
        )
        for step_name, begin, end in copied:
            source = next(step["run"] for step in auto_steps if step["name"] == step_name)
            self.assertEqual(
                marked_region(source, begin, end),
                marked_region(rebase, begin, end),
            )
        self.assertLess(
            rebase.index("dependabot_merge_decision"),
            rebase.index("dependabot_rebase_eligibility"),
        )
        self.assertLess(
            rebase.index('dependabot_rebase_already_requested "$head_sha"'),
            rebase.index("gh pr comment"),
        )
        self.assertIn(
            'dependabot_update_signals "$head_ref" "$pr_title" "$pr_body"',
            rebase,
        )
        self.assertIn(
            'dependabot_merge_decision "${signals[0]}" "${signals[1]}" "${signals[2]}"',
            rebase,
        )
        self.assertIn(
            'dependabot_rebase_eligibility "$author" "$base_ref" "$armed" "$merge_state" "$decision"',
            rebase,
        )
        self.assertLess(
            rebase.index('[[ ! "$head_sha" =~ ^[0-9a-f]{40}$ ]]'),
            rebase.index('dependabot_rebase_already_requested "$head_sha"'),
        )

    def test_rebase_request_is_once_per_head_sha_and_skips_held_majors(self):
        run = rebase_run()
        request = (
            marked_region(
                run,
                "# BEGIN dependabot-rebase-request",
                "# END dependabot-rebase-request",
            )
            + "\n"
        )
        comment_script = request + 'dependabot_rebase_comment "$1"\n'
        already_script = request + 'dependabot_rebase_already_requested "$1" "$2"\n'
        eligibility_script = request + 'dependabot_rebase_eligibility "$1" "$2" "$3" "$4" "$5"\n'
        signals_script = (
            marked_region(
                run,
                "# BEGIN dependabot-update-signals",
                "# END dependabot-update-signals",
            )
            + '\ndependabot_update_signals "$1" "$2" "$3"\n'
        )
        decision_script = (
            marked_region(
                run,
                "# BEGIN dependabot-merge-decision",
                "# END dependabot-merge-decision",
            )
            + '\ndependabot_merge_decision "$1" "$2" "$3"\n'
        )

        sha_a = "a" * 40
        sha_b = "b" * 40
        comment = run_bash(comment_script, sha_a)
        lines = comment.splitlines()
        self.assertEqual(lines[0], "@dependabot rebase")
        self.assertEqual(lines[1], "")
        self.assertEqual(lines[2], f"<!-- dependabot-rebase-sha: {sha_a} -->")
        self.assertNotIn(sha_a, lines[0])
        self.assertEqual(run_bash(already_script, sha_a, comment).strip(), "yes")
        self.assertEqual(run_bash(already_script, sha_b, comment).strip(), "no")
        self.assertEqual(run_bash(already_script, "a" * 39, comment).strip(), "no")
        self.assertEqual(run_bash(already_script, sha_a, "").strip(), "no")
        self.assertEqual(
            run_bash(already_script, sha_a, "@dependabot rebase\n").strip(),
            "no",
        )

        eligible = ("dependabot[bot]", "main", "true", "BEHIND", "merge", "rebase")
        skipped = (
            ("dependabot[bot]", "main", "true", "BEHIND", "hold", "skip"),
            ("dependabot[bot]", "main", "false", "BEHIND", "merge", "skip"),
            ("dependabot[bot]", "main", "true", "CLEAN", "merge", "skip"),
            ("dependabot[bot]", "main", "true", "BLOCKED", "merge", "skip"),
            ("dependabot[bot]", "main", "true", "UNSTABLE", "merge", "skip"),
            ("dependabot[bot]", "main", "true", "behind", "merge", "skip"),
            ("dependabot[bot]", "develop", "true", "BEHIND", "merge", "skip"),
            ("github-actions[bot]", "main", "true", "BEHIND", "merge", "skip"),
            ("Dependabot[bot]", "main", "true", "BEHIND", "merge", "skip"),
            ("dependabot[bot]", "main", "true", "BEHIND", "", "skip"),
        )
        author, base_ref, armed, state, decision, expected = eligible
        self.assertEqual(
            run_bash(eligibility_script, author, base_ref, armed, state, decision).strip(),
            expected,
        )
        for author, base_ref, armed, state, decision, expected in skipped:
            with self.subTest(author=author, state=state, decision=decision, base_ref=base_ref):
                self.assertEqual(
                    run_bash(
                        eligibility_script, author, base_ref, armed, state, decision
                    ).strip(),
                    expected,
                )

        classified = (
            (
                "dependabot/pip/tools/routine-python-tools-abc",
                "deps: bump github-copilot-sdk from 1.0.33 to 1.0.34",
                "",
                "rebase",
            ),
            (
                "dependabot/github_actions/actions-major-updates-7f603b356f",
                "ci: bump the actions-major-updates group",
                "Updates `actions/checkout` from 6.0.2 to 7.0.1",
                "rebase",
            ),
            (
                "dependabot/npm_and_yarn/site/site-major-updates-abc",
                "deps: bump the site-major-updates group",
                "Updates `next` from 14.2.5 to 15.0.0",
                "skip",
            ),
            (
                "dependabot/pip/tools/python-major-updates-abc",
                "deps: bump PyYAML from 6.0.3 to 7.0.0",
                "",
                "skip",
            ),
            (
                "dependabot/github_actions/actions-major-updates-abc",
                "ci: bump the actions-major-updates group",
                "No version pair in this body",
                "skip",
            ),
        )
        for head_ref, title, body, expected in classified:
            with self.subTest(head_ref=head_ref):
                signal_lines = run_bash(signals_script, head_ref, title, body).splitlines()
                decision = run_bash(decision_script, *signal_lines).strip()
                action = run_bash(
                    eligibility_script,
                    "dependabot[bot]",
                    "main",
                    "true",
                    "BEHIND",
                    decision,
                ).strip()
                self.assertEqual(action, expected)

    def test_rebase_runbook_states_scope_and_expiry(self):
        runbook = (REPO_ROOT / "docs/maintenance/dependabot-rebase.md").read_text()
        readme = (REPO_ROOT / "README.md").read_text()
        contributing = (REPO_ROOT / "CONTRIBUTING.md").read_text()

        self.assertIn("DEPENDABOT_REBASE_TOKEN", runbook)
        self.assertIn("90 days", runbook)
        self.assertIn("No expiration", runbook)
        self.assertIn("Pull requests: Read and write", runbook)
        self.assertIn("NoahJenkins/vgc-coach", runbook)
        self.assertIn("Only select repositories", runbook)
        self.assertIn("author_association", runbook)
        self.assertIn("dependabot/dependabot-core#9147", runbook)
        self.assertIn("Repository secrets", runbook)
        self.assertIn("not an environment secret", runbook)
        self.assertIn("Dependabot secret", runbook)
        self.assertIn("Revoke the old token", runbook)
        self.assertIn("does not push", runbook)
        self.assertIn("does not change branch protection", runbook)
        self.assertIn("::notice::", (REPO_ROOT / ".github/workflows/dependabot-rebase.yml").read_text())
        for page in (readme, contributing):
            self.assertIn("docs/maintenance/dependabot-rebase.md", page)


if __name__ == "__main__":
    unittest.main()
