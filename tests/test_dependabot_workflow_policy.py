from __future__ import annotations

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
        meta = by_name["Fetch Dependabot metadata"]
        decide = by_name["Decide whether to arm auto-merge"]
        enable = by_name["Enable auto-merge"]
        disable = by_name["Disable auto-merge"]

        self.assertIn("major-updates", detect["run"])
        self.assertNotIn("dependency-major", detect["run"])
        self.assertEqual(
            meta["uses"],
            "dependabot/fetch-metadata@25dd0e34f4fe68f24cc83900b1fe3fe149efef98",
        )
        workflow_text = (REPO_ROOT / ".github/workflows/dependabot-auto-merge.yml").read_text()
        self.assertIn(
            "dependabot/fetch-metadata@25dd0e34f4fe68f24cc83900b1fe3fe149efef98 # v3.1.0",
            workflow_text,
        )
        self.assertEqual(
            meta["if"],
            "steps.scope.outputs.eligible == 'true' && steps.major.outputs.major == 'true'",
        )
        self.assertEqual(meta["with"]["github-token"], "${{ github.token }}")
        self.assertNotIn("skip-verification", meta["with"])
        self.assertNotIn("skip-commit-verification", meta["with"])
        self.assertNotIn("alert-lookup", meta["with"])
        self.assertEqual(
            decide["env"]["PACKAGE_ECOSYSTEM"],
            "${{ steps.meta.outputs.package-ecosystem }}",
        )
        self.assertEqual(
            decide["env"]["UPDATE_TYPE"],
            "${{ steps.meta.outputs.update-type }}",
        )
        self.assertEqual(
            decide["if"],
            "always() && steps.scope.outcome == 'success' && steps.scope.outputs.eligible == 'true' && steps.major.outcome == 'success' && (steps.major.outputs.major != 'true' || steps.meta.outcome == 'success' || steps.meta.outcome == 'failure')",
        )
        self.assertIn(
            '[ "$MAJOR" = "true" ] && [ "$META_OUTCOME" != "success" ]',
            decide["run"],
        )
        self.assertLess(
            decide["run"].index('"$META_OUTCOME" != "success"'),
            decide["run"].index('dependabot_merge_decision "$MAJOR"'),
        )
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
            "steps.scope.outputs.eligible == 'true' && steps.update_type.outputs.decision == 'merge' && steps.meta.outcome != 'failure'",
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
        start = run.index("# BEGIN dependabot-merge-decision")
        end = run.index("# END dependabot-merge-decision")
        script = (
            run[start:end]
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
                completed = subprocess.run(
                    ["bash", "-c", script, "decision", major, ecosystem, update_type],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(completed.stdout.strip(), expected)

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
            "steps.scope.outputs.eligible == 'true' && steps.update_type.outputs.decision == 'merge' && steps.meta.outcome != 'failure'",
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


if __name__ == "__main__":
    unittest.main()
