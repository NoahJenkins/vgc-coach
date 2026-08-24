from __future__ import annotations

import shlex
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
        update = config["updates"][0]

        self.assertEqual(update["package-ecosystem"], "npm")
        self.assertEqual(update["directory"], "/site")
        self.assertNotIn("allow", update)
        self.assertNotIn("ignore", update)
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
        self.assertNotIn("update-type", commands)

    def test_auto_merge_retains_site_only_changed_file_scope(self):
        workflow = load_yaml(".github/workflows/dependabot-auto-merge.yml")
        steps = workflow["jobs"]["enable-auto-merge"]["steps"]
        scope_step = next(
            step for step in steps if step["name"] == "Check changed files stay under site/"
        )

        self.assertIn("site/*)", scope_step["run"])
        self.assertIn("eligible=false", scope_step["run"])
        self.assertEqual(
            next(step for step in steps if step["name"] == "Enable auto-merge")["if"],
            "steps.scope.outputs.eligible == 'true'",
        )

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
