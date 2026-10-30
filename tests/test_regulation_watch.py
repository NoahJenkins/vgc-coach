from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def feed_item(entry_id: str, title: str, *, rom=("CHP",), kind="Regulations", pub=100):
    return {
        "id": entry_id,
        "title": title,
        "kindTxt": kind,
        "stAt": 10,
        "endAt": "20",
        "pubAt": pub,
        "link": f"page/{entry_id}.html",
        "linkRom": list(rom),
    }


def workflow_triggers(workflow: dict) -> dict:
    return workflow.get("on", workflow.get(True, {}))


class RegulationFeedTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module("regulation_watch")

    def test_only_champions_regulation_entries_are_tracked(self):
        feed = {
            "data": [
                feed_item("900", "Regulation Set M-D"),
                feed_item("700", "Regulation Set I", rom=("SC", "VI"), kind="Other Games"),
                feed_item("860", "Face a Mighty Hydreigon!", kind="Other Games"),
                feed_item("816", "Regulation Set M-C (Updated on September 9)"),
            ]
        }

        entries = self.module.champions_regulation_entries(feed)

        self.assertEqual([entry["id"] for entry in entries], ["816", "900"])
        self.assertEqual(entries[0]["endAt"], 20)

    def test_feed_without_champions_regulations_fails_loudly(self):
        with self.assertRaisesRegex(ValueError, "format may have changed"):
            self.module.champions_regulation_entries(
                {"data": [feed_item("1", "News", kind="Other Games")]}
            )
        with self.assertRaisesRegex(ValueError, "data list"):
            self.module.champions_regulation_entries({"items": []})

    def test_compare_reports_new_and_changed_entries_with_stable_signature(self):
        baseline = self.module.champions_regulation_entries(
            {"data": [feed_item("816", "Regulation Set M-C")]}
        )
        live = self.module.champions_regulation_entries(
            {
                "data": [
                    feed_item("816", "Regulation Set M-C (Updated)", pub=200),
                    feed_item("900", "Regulation Set M-D"),
                ]
            }
        )

        first = self.module.compare_entries(baseline, live)
        second = self.module.compare_entries(baseline, live)
        unchanged = self.module.compare_entries(live, live)

        self.assertEqual([entry["id"] for entry in first["new"]], ["900"])
        self.assertEqual(first["changed"][0]["changes"]["pubAt"], [100, 200])
        self.assertEqual(first["signature"], second["signature"])
        self.assertEqual(len(first["signature"]), 12)
        self.assertEqual(unchanged, {"new": [], "changed": [], "signature": None})

    def test_checked_in_baseline_matches_the_feed_entry_shape(self):
        payload = json.loads((REPO_ROOT / self.module.BASELINE_PATH).read_text())

        self.assertEqual(payload["feed_url"], self.module.FEED_URL)
        self.assertNotIn("regulation_id", json.dumps(payload))
        for entry in payload["entries"]:
            self.assertEqual(set(entry), {"id", *self.module.TRACKED_FIELDS})
        self.assertIn(
            "Regulation Set M-C", [entry["title"].split(" (")[0] for entry in payload["entries"]]
        )


class RegulationFetchBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module("regulation_watch")

    def test_only_https_allowlisted_hosts_are_fetched(self):
        for url in (
            "http://news.pokemon-home.com/en/json/list.json",
            "https://www.pokemon.com/uk/news",
            "https://news.pokemon-home.com.evil.example/en/json/list.json",
            "file:///etc/passwd",
        ):
            with self.subTest(url=url), self.assertRaisesRegex(ValueError, "non-allowlisted"):
                self.module.fetch(url)

    def test_redirects_to_other_hosts_are_refused(self):
        handler = self.module._AllowlistRedirectHandler()
        with self.assertRaisesRegex(ValueError, "non-allowlisted"):
            handler.redirect_request(None, None, 302, "Found", {}, "https://example.com/")

    def test_page_text_drops_scripts_and_keeps_links(self):
        text, links = self.module.extract_page(
            "<html><script>ignore()</script><p>Duration</p><p>Sept&nbsp;9</p>"
            '<a href="https://web-view.app.pokemonchampions.jp/x/pokemon.html">Eligible</a></html>'
        )

        self.assertEqual(text, "Duration\nSept 9\nEligible")
        self.assertEqual(links, ["https://web-view.app.pokemonchampions.jp/x/pokemon.html"])

    def test_eligible_pokemon_are_read_from_the_embedded_array(self):
        page = 'const pokemons = [["0003-000",1,"Venusaur"],["0006-000",0,"Charizard"]];'

        self.assertEqual(self.module.extract_eligible_pokemon(page), ["Venusaur"])
        self.assertEqual(self.module.extract_eligible_pokemon("<p>none</p>"), [])


class SourceRefreshTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module("regulation_watch")

    def write_repo(self, root: Path, fetched_at: str) -> None:
        snapshots = root / "data/snapshots"
        snapshots.mkdir(parents=True)
        (snapshots / "champions-reg-m-c-x.json").write_text(
            json.dumps(
                {
                    "temporal_status": "current",
                    "sources": [{"fetched_at": fetched_at}],
                }
            )
        )
        registry = root / self.module.REGISTRY_PATH
        registry.parent.mkdir(parents=True)
        registry.write_text(
            yaml.safe_dump(
                {
                    "sources": [
                        {
                            "role": "official_regulation",
                            "temporal_status": "current",
                            "canonical_url": "https://example.test/rules",
                            "freshness": {"max_age_days": 30},
                        }
                    ]
                }
            )
        )

    def test_refresh_is_due_three_days_before_the_freshness_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_repo(root, "2026-10-01T00:00:00Z")

            early = self.module.source_refresh_status(
                root, datetime(2026, 10, 27, 23, tzinfo=timezone.utc)
            )
            due = self.module.source_refresh_status(
                root, datetime(2026, 10, 28, tzinfo=timezone.utc)
            )

        self.assertFalse(early["due"])
        self.assertTrue(due["due"])
        self.assertEqual(due["due_at"], "2026-10-31T00:00:00Z")


class DrafterScopeTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module("draft_regulation_update")

    def test_write_scope_covers_runbook_artifacts_only(self):
        roots = self.module.allowed_write_roots()
        allowed = (
            "data/snapshots/champions-reg-m-d-2026-12-01.json",
            "docs/skills/shared/references/champions-reg-m-d-legality.md",
            "docs/skills/shared/references/live-source-registry.yaml",
            "data/fixtures/battle-state-v1.example.json",
            "skills/vgc-team-builder/SKILL.md",
            ".opencode/skills/opencode-vgc-team-audit/SKILL.md",
            "tests/test_format_freshness.py",
        )
        denied = (
            "data/official-regulation-feed.json",
            "data/fixtures/evals/team-audit/case-01.md",
            "skills/vgc-team-builder/notes.md",
            "plugins/vgc-coach-claude/README.md",
            "site/src/generated/trustData.ts",
            "tools/regulation_watch.py",
            ".github/workflows/regulation-watch.yml",
            "tests/test_regulation_watch.py",
        )

        self.assertEqual(self.module.out_of_scope_paths(list(allowed), roots), [])
        self.assertEqual(self.module.out_of_scope_paths(list(denied), roots), list(denied))

    def test_prompt_lists_changes_and_evidence(self):
        prompt = self.module.build_prompt(
            {
                "new": [{"id": "900", "title": "Regulation Set M-D"}],
                "changed": [
                    {"id": "816", "title": "Regulation Set M-C", "changes": {"endAt": [1, 2]}}
                ],
            },
            [Path("official-page-900.md")],
        )

        self.assertIn("New entry 900: Regulation Set M-D", prompt)
        self.assertIn("Updated entry 816: Regulation Set M-C (changed: endAt)", prompt)
        self.assertIn("official-page-900.md", prompt)


class RegulationWatchWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.workflow = yaml.safe_load(
            (REPO_ROOT / ".github/workflows/regulation-watch.yml").read_text()
        )

    def test_schedule_runs_every_third_day_on_protected_main(self):
        triggers = workflow_triggers(self.workflow)

        self.assertEqual(triggers["schedule"], [{"cron": "23 9 */3 * *"}])
        self.assertIn("workflow_dispatch", triggers)
        self.assertEqual(self.workflow["permissions"], {"contents": "read"})
        for job in self.workflow["jobs"].values():
            self.assertIn("github.ref == 'refs/heads/main'", job["if"])

    def test_copilot_secret_reaches_only_the_draft_step(self):
        text = (REPO_ROOT / ".github/workflows/regulation-watch.yml").read_text()
        watch_steps = self.workflow["jobs"]["watch"]["steps"]
        draft_steps = self.workflow["jobs"]["draft"]["steps"]
        secret_steps = [
            step["name"]
            for step in draft_steps
            if "secrets." in json.dumps(step.get("env", {}))
        ]

        self.assertEqual(text.count("secrets."), 2)
        self.assertNotIn("secrets.", json.dumps(watch_steps))
        self.assertEqual(
            secret_steps,
            ["Draft the transition with Copilot", "Repair a failing draft with Copilot"],
        )

    def test_workflow_and_drafter_share_the_default_model(self):
        default_model = load_module("draft_regulation_update").DEFAULT_MODEL
        draft_steps = self.workflow["jobs"]["draft"]["steps"]
        models = {
            step["env"]["DRAFT_MODEL"]
            for step in draft_steps
            if "DRAFT_MODEL" in step.get("env", {})
        }

        self.assertEqual(default_model, "claude-sonnet-5.5")
        self.assertEqual(
            models, {f"${{{{ vars.REGULATION_DRAFT_MODEL || '{default_model}' }}}}"}
        )

    def test_validation_steps_fail_on_validator_errors_and_repair_runs_once(self):
        steps = {step["name"]: step for step in self.workflow["jobs"]["draft"]["steps"]}

        for name in ("Validate the draft", "Regenerate and revalidate the repaired draft"):
            with self.subTest(step=name):
                self.assertIn("set -euo pipefail", steps[name]["run"])
                self.assertTrue(steps[name]["continue-on-error"])
        self.assertEqual(
            steps["Repair a failing draft with Copilot"]["if"],
            "steps.validate.outcome == 'failure'",
        )
        self.assertIn("--validation-log", steps["Repair a failing draft with Copilot"]["run"])
        self.assertEqual(
            steps["Push the draft branch and open a draft pull request"]["env"]["VALIDATION"],
            "${{ steps.validate.outcome == 'failure' && steps.revalidate.outcome "
            "|| steps.validate.outcome }}",
        )
        self.assertEqual(
            self.workflow["jobs"]["draft"]["permissions"],
            {"contents": "write", "pull-requests": "write"},
        )

    def test_checkouts_do_not_persist_credentials(self):
        for job_name in ("watch", "draft"):
            checkout = self.workflow["jobs"][job_name]["steps"][0]
            with self.subTest(job=job_name):
                self.assertTrue(checkout["uses"].startswith("actions/checkout@"))
                self.assertFalse(checkout["with"]["persist-credentials"])

    def test_draft_runs_once_per_change_and_opens_only_a_draft_pr(self):
        draft = self.workflow["jobs"]["draft"]
        push_step = next(step for step in draft["steps"] if step["name"].startswith("Push"))

        self.assertIn("needs.watch.outputs.changed == 'true'", draft["if"])
        self.assertIn("needs.watch.outputs.draft_exists != 'true'", draft["if"])
        self.assertIn("gh pr create", push_step["run"])
        self.assertIn("--draft", push_step["run"])
        self.assertNotIn("gh pr merge", push_step["run"])
        self.assertIn("github_pat_", push_step["run"])
        self.assertLess(
            push_step["run"].index("git diff --cached | grep"),
            push_step["run"].index("git push"),
        )

    def test_required_checks_start_when_a_draft_is_marked_ready(self):
        for path in (".github/workflows/site-ci.yml", ".github/workflows/plugin-package-ci.yml"):
            workflow = yaml.safe_load((REPO_ROOT / path).read_text())
            with self.subTest(path=path):
                self.assertEqual(
                    workflow_triggers(workflow)["pull_request"]["types"],
                    ["opened", "synchronize", "reopened", "ready_for_review"],
                )


if __name__ == "__main__":
    unittest.main()
