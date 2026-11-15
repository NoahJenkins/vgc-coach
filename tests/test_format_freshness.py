from __future__ import annotations

import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "tools" / "check_format_freshness.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_format_freshness", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_designated_artifacts(
    root: Path,
    *,
    current_end: str,
    current_start: str = "2026-06-17T02:00:00Z",
    current_regulation: str = "m-b",
) -> None:
    registry = root / "docs/skills/shared/references/live-source-registry.yaml"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        "sources:\n"
        f"  - id: regulation-set-{current_regulation}\n"
        "    role: official_regulation\n"
        f"    regulation_id: regulation-{current_regulation}\n"
        "    temporal_status: current\n"
        "    active_window:\n"
        f"      start: '{current_start}'\n"
        f"      end: '{current_end}'\n"
    )

    current_ref = registry.parent / f"champions-reg-{current_regulation}-current-legality.md"
    current_ref.write_text(
        "---\n"
        "temporal_status: current\n"
        f"regulation_id: regulation-{current_regulation}\n"
        "active_window:\n"
        f"  start: '{current_start}'\n"
        f"  end: '{current_end}'\n"
        "---\n"
        "# Current reference\n"
    )

    historical_ref = registry.parent / "champions-reg-m-a-legality.md"
    historical_ref.write_text(
        "---\n"
        "temporal_status: historical\n"
        "regulation_id: regulation-m-a\n"
        "active_window:\n"
        "  start: '2026-04-08T02:00:00Z'\n"
        "  end: '2026-06-17T01:59:00Z'\n"
        "---\n"
        "# Historical reference\n"
    )

    snapshots = root / "data/snapshots"
    snapshots.mkdir(parents=True)
    (snapshots / "current.json").write_text(
        json.dumps(
            {
                "snapshot_id": "current",
                "temporal_status": "current",
                "format": {
                    "regulation_id": f"regulation-{current_regulation}",
                    "active_window": {
                        "start": current_start,
                        "end": current_end,
                    },
                },
            }
        )
    )
    (snapshots / "historical.json").write_text(
        json.dumps(
            {
                "snapshot_id": "historical-m-a",
                "temporal_status": "historical",
                "format": {
                    "regulation_id": "regulation-m-a",
                    "active_window": {
                        "start": "2026-04-08T02:00:00Z",
                        "end": "2026-06-17T01:59:00Z",
                    },
                },
            }
        )
    )

    fixtures = root / "data/fixtures"
    fixtures.mkdir(parents=True)
    (fixtures / "request.example.json").write_text(
        json.dumps(
            {
                "temporal_status": "current",
                "format": {
                    "regulation_id": f"regulation-{current_regulation}",
                    "active_window": {
                        "start": current_start,
                        "end": current_end,
                    },
                },
            }
        )
    )


def write_empty_registry(root: Path) -> None:
    registry = root / "docs/skills/shared/references/live-source-registry.yaml"
    registry.parent.mkdir(parents=True)
    registry.write_text("sources: []\n")


class FormatFreshnessTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_current_designations_pass_inside_window_and_at_exact_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_designated_artifacts(root, current_end="2026-09-09T01:59:00Z")

            inside = self.module.find_expired_current_artifacts(
                root, now=datetime(2026, 8, 6, 12, tzinfo=timezone.utc)
            )
            boundary = self.module.find_expired_current_artifacts(
                root, now=datetime(2026, 9, 9, 1, 59, tzinfo=timezone.utc)
            )

        self.assertEqual(inside, ())
        self.assertEqual(boundary, ())

    def test_current_designations_fail_after_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_designated_artifacts(root, current_end="2026-09-09T01:59:00Z")

            expired = self.module.find_expired_current_artifacts(
                root, now=datetime(2026, 9, 9, 1, 59, 1, tzinfo=timezone.utc)
            )

        self.assertEqual(len(expired), 4)
        self.assertTrue(all("2026-09-09T01:59:00Z" in item for item in expired))

    def test_expiry_warning_starts_inside_warning_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_designated_artifacts(root, current_end="2026-09-09T01:59:00Z")

            outside = self.module.find_expiring_current_windows(
                root, now=datetime(2026, 8, 10, 1, 58, tzinfo=timezone.utc)
            )
            inside = self.module.find_expiring_current_windows(
                root, now=datetime(2026, 8, 10, 1, 59, tzinfo=timezone.utc)
            )
            at_end = self.module.find_expiring_current_windows(
                root, now=datetime(2026, 9, 9, 1, 59, tzinfo=timezone.utc)
            )
            after_end = self.module.find_expiring_current_windows(
                root, now=datetime(2026, 9, 9, 1, 59, 1, tzinfo=timezone.utc)
            )

        self.assertEqual(outside, ())
        self.assertEqual(len(inside), 1)
        self.assertIn("4 current-format artifact(s)", inside[0])
        self.assertIn("2026-09-09T01:59:00Z", inside[0])
        self.assertIn("in 30d 0h", inside[0])
        self.assertIn("regulation-transition.md", inside[0])
        self.assertEqual(len(at_end), 1)
        self.assertEqual(after_end, ())

    def test_window_status_is_due_within_14_days_and_after_the_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_designated_artifacts(root, current_end="2026-09-09T01:59:00Z")

            def status(*args):
                return self.module.current_window_status(
                    root, now=datetime(*args, tzinfo=timezone.utc)
                )

            far = status(2026, 8, 25, 1, 58)
            edge = status(2026, 8, 26, 1, 59)
            ended = status(2026, 9, 10)

        self.assertFalse(far["due"])
        self.assertTrue(edge["due"])
        self.assertFalse(edge["ended"])
        self.assertEqual(edge["ends_at"], "2026-09-09T01:59:00Z")
        self.assertTrue(ended["due"])
        self.assertTrue(ended["ended"])

    def test_window_report_cli_writes_outputs_and_never_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_designated_artifacts(root, current_end="2026-09-09T01:59:00Z")
            status = self.module.current_window_status(
                root, now=datetime(2026, 9, 1, tzinfo=timezone.utc)
            )
            output = root / "gh-output"
            body = root / "out/issue.md"
            self.module.write_window_report(
                status, github_output=output, issue_body=body
            )

            self.assertIn("window_due=true", output.read_text())
            self.assertIn("window_ends_at=2026-09-09T01:59:00Z", output.read_text())
            self.assertIn("2026-09-09T01:59:00Z", body.read_text())

    def test_expiry_warning_does_not_fail_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_designated_artifacts(root, current_end="2026-09-09T01:59:00Z")
            now = datetime(2026, 9, 1, tzinfo=timezone.utc)

            with mock.patch.dict(
                "os.environ", {"GITHUB_ACTIONS": "true"}
            ), redirect_stdout(io.StringIO()) as output:
                exit_code = self.module.main(repo_root=root, now=now)

        self.assertEqual(exit_code, 0)
        self.assertTrue(
            output.getvalue().startswith("::warning title=Current format expires soon::")
        )

    def _git_repo_with_change(self, root: Path, changed: str) -> str:
        """Commit the fixture tree, then a change to `changed`; return the base sha."""

        def git(*args: str) -> str:
            return subprocess.run(
                ("git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args),
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()

        git("init", "-q")
        git("add", "-A")
        git("commit", "-q", "-m", "base")
        base = git("rev-parse", "HEAD")
        target = root / changed
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(target.read_text() + "x\n" if target.exists() else "x\n")
        git("add", "-A")
        git("commit", "-q", "-m", "change")
        return base

    def _run_main(self, root: Path, argv: list[str], *, env: dict[str, str] | None = None):
        now = datetime(2026, 9, 10, tzinfo=timezone.utc)  # after the window end
        environ = {"GITHUB_ACTIONS": "true", **(env or {})}
        with mock.patch.dict("os.environ", environ), redirect_stdout(
            io.StringIO()
        ) as output:
            if env is None:
                os.environ.pop(self.module.BASE_REF_ENV, None)
            code = self.module.main(argv, repo_root=root, now=now)
        return code, output.getvalue()

    def test_expired_window_with_unrelated_change_warns_and_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_designated_artifacts(root, current_end="2026-09-09T01:59:00Z")
            base = self._git_repo_with_change(root, "site/package.json")

            code, output = self._run_main(root, ["--base-ref", base])

        self.assertEqual(code, 0)
        self.assertIn("::warning title=Current format is stale::", output)
        self.assertNotIn("are stale:", output)

    def test_base_ref_can_come_from_the_environment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_designated_artifacts(root, current_end="2026-09-09T01:59:00Z")
            base = self._git_repo_with_change(root, ".github/workflows/ci.yml")

            code, _ = self._run_main(
                root, [], env={self.module.BASE_REF_ENV: base}
            )

        self.assertEqual(code, 0)

    def test_expired_window_with_format_change_fails(self):
        for changed in (
            "data/snapshots/README.md",
            "skills/vgc-team-builder/SKILL.md",
            "docs/skills/shared/references/champions-reg-m-d-legality.md",
            "tools/check_format_freshness.py",
        ):
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                write_designated_artifacts(root, current_end="2026-09-09T01:59:00Z")
                base = self._git_repo_with_change(root, changed)

                code, output = self._run_main(root, ["--base-ref", base])

                self.assertEqual(code, 1)
                self.assertIn("Current-format artifacts are stale:", output)
                self.assertIn(changed, output)

    def test_expired_window_without_context_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_designated_artifacts(root, current_end="2026-09-09T01:59:00Z")
            self._git_repo_with_change(root, "site/package.json")

            code, output = self._run_main(root, [])

        self.assertEqual(code, 1)
        self.assertIn("Current-format artifacts are stale:", output)

    def test_expired_window_fails_safe_when_the_diff_cannot_be_computed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_designated_artifacts(root, current_end="2026-09-09T01:59:00Z")
            self._git_repo_with_change(root, "site/package.json")

            for base in ("no-such-ref", "0" * 40):
                with self.subTest(base=base):
                    code, output = self._run_main(root, ["--base-ref", base])
                    self.assertEqual(code, 1)
                    self.assertIn("failing safe", output)

    def test_runtime_reference_issue_fails_even_for_unrelated_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_designated_artifacts(root, current_end="2026-09-09T01:59:00Z")
            wrapper = root / ".opencode/skills/opencode-vgc-team-builder/SKILL.md"
            wrapper.parent.mkdir(parents=True)
            wrapper.write_text(
                "Read `docs/skills/shared/references/champions-reg-m-a-legality.md`.\n"
            )
            base = self._git_repo_with_change(root, "site/package.json")

            code, output = self._run_main(root, ["--base-ref", base])

        self.assertEqual(code, 1)
        self.assertIn("historical regulation reference", output)

    def test_runtime_reference_issue_fails_inside_the_window_too(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_designated_artifacts(root, current_end="2026-09-09T01:59:00Z")
            wrapper = root / ".opencode/skills/opencode-vgc-team-builder/SKILL.md"
            wrapper.parent.mkdir(parents=True)
            wrapper.write_text(
                "Read `docs/skills/shared/references/champions-reg-m-a-legality.md`.\n"
            )
            base = self._git_repo_with_change(root, "site/package.json")
            with mock.patch.dict("os.environ", {}), redirect_stdout(io.StringIO()):
                code = self.module.main(
                    ["--base-ref", base],
                    repo_root=root,
                    now=datetime(2026, 8, 6, tzinfo=timezone.utc),
                )

        self.assertEqual(code, 1)

    def test_format_artifact_patterns_cover_the_runbook_step_two_paths(self):
        runbook = (REPO_ROOT / "docs/maintenance/regulation-transition.md").read_text()
        step_two = runbook.split("## 2.")[1].split("Find the remaining")[0]
        self.assertTrue(
            self.module.touched_format_artifacts(
                [
                    "data/snapshots/champions-reg-m-d-2027-01-01.json",
                    "docs/skills/shared/references/champions-reg-m-d-legality.md",
                    "docs/skills/shared/references/live-source-registry.yaml",
                    "data/official-regulation-feed.json",
                    "data/fixtures/battle-state-v1.example.json",
                    "skills/vgc-meta-research/SKILL.md",
                    ".opencode/skills/opencode-vgc-meta-research/SKILL.md",
                    "docs/evals/meta-live-checklist.md",
                    "tools/check_format_freshness.py",
                    "tests/test_format_freshness.py",
                    "tests/test_source_registry.py",
                    "tests/test_ingest_battle_state.py",
                ]
            ),
        )
        self.assertEqual(
            self.module.touched_format_artifacts(
                [
                    "site/package.json",
                    ".github/workflows/plugin-package-ci.yml",
                    "plugins/vgc-coach/README.md",
                    "docs/runtime/codex.md",
                    "tests/test_validate.py",
                ]
            ),
            (),
        )
        self.assertIn("data/snapshots/", step_two)

    def test_current_designations_fail_before_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_designated_artifacts(
                root,
                current_start="2026-09-10T02:00:00Z",
                current_end="2026-12-01T01:59:00Z",
            )

            upcoming = self.module.find_expired_current_artifacts(
                root, now=datetime(2026, 9, 10, 1, 59, 59, tzinfo=timezone.utc)
            )

        self.assertEqual(len(upcoming), 4)
        self.assertTrue(all("2026-09-10T02:00:00Z" in item for item in upcoming))

    def test_stale_current_m_a_fails_while_historical_m_a_is_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_designated_artifacts(
                root,
                current_regulation="m-a",
                current_start="2026-04-08T02:00:00Z",
                current_end="2026-06-17T01:59:00Z",
            )

            expired = self.module.find_expired_current_artifacts(
                root, now=datetime(2026, 8, 6, 12, tzinfo=timezone.utc)
            )

        self.assertEqual(len(expired), 4)
        self.assertFalse(any("historical" in item for item in expired))

    def test_runtime_wrapper_cannot_route_current_coaching_to_historical_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_designated_artifacts(root, current_end="2026-09-09T01:59:00Z")
            wrapper = root / ".opencode/skills/opencode-vgc-team-builder/SKILL.md"
            wrapper.parent.mkdir(parents=True)
            wrapper.write_text(
                "Read `docs/skills/shared/references/champions-reg-m-a-legality.md`.\n"
            )

            issues = self.module.find_expired_current_artifacts(
                root, now=datetime(2026, 8, 6, 12, tzinfo=timezone.utc)
            )

        self.assertEqual(len(issues), 1)
        self.assertIn("historical regulation reference", issues[0])
        self.assertIn("champions-reg-m-b-legality.md", issues[0])

    def test_regulation_bearing_paths_require_temporal_status(self):
        scenarios = {
            "registry": (
                "docs/skills/shared/references/live-source-registry.yaml",
                "sources:\n"
                "  - id: regulation-set-future\n"
                "    role: official_regulation\n"
                "    active_window:\n"
                "      start: '2027-01-01T00:00:00Z'\n"
                "      end: '2027-02-01T00:00:00Z'\n",
            ),
            "snapshot": (
                "data/snapshots/future/nested/future-format.json",
                json.dumps(
                    {
                        "format": {
                            "regulation_id": "regulation-future",
                            "active_window": {
                                "start": "2027-01-01T00:00:00Z",
                                "end": "2027-02-01T00:00:00Z",
                            },
                        }
                    }
                ),
            ),
            "reference": (
                "docs/skills/shared/references/future-format.md",
                "---\n"
                "regulation_id: regulation-future\n"
                "active_window:\n"
                "  start: '2027-01-01T00:00:00Z'\n"
                "  end: '2027-02-01T00:00:00Z'\n"
                "---\n# Future format\n",
            ),
            "ambiguous fixture": (
                "data/fixtures/future/nested/anything.example.json",
                json.dumps(
                    {
                        "format": {
                            "regulation_id": "regulation-future",
                            "active_window": {
                                "start": "2027-01-01T00:00:00Z",
                                "end": "2027-02-01T00:00:00Z",
                            },
                        }
                    }
                ),
            ),
            "ambiguous provenance fixture": (
                "data/fixtures/future/nested/provenance.example.json",
                json.dumps(
                    {
                        "schema_version": "future-state-v1",
                        "format_provenance": {
                            "regulation_id": "regulation-future",
                            "active_window": {
                                "start": "2027-01-01T00:00:00Z",
                                "end": "2027-02-01T00:00:00Z",
                            },
                        },
                    }
                ),
            ),
        }

        for label, (relative, content) in scenarios.items():
            with self.subTest(path=label), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                write_empty_registry(root)
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)

                with self.assertRaisesRegex(ValueError, "temporal_status"):
                    self.module.find_expired_current_artifacts(
                        root, now=datetime(2026, 8, 6, 12, tzinfo=timezone.utc)
                    )

    def test_regulation_bearing_snapshot_and_fixture_require_active_window(self):
        for relative in (
            "data/snapshots/future/nested/future-format.json",
            "data/fixtures/future/nested/anything.example.json",
        ):
            with self.subTest(path=relative), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                write_empty_registry(root)
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    json.dumps(
                        {
                            "temporal_status": "historical",
                            "format": {"regulation_id": "regulation-future"},
                        }
                    )
                )

                with self.assertRaisesRegex(ValueError, "active_window"):
                    self.module.find_expired_current_artifacts(
                        root, now=datetime(2026, 8, 6, 12, tzinfo=timezone.utc)
                    )

    def test_checked_in_request_examples_use_current_m_c_provenance(self):
        for filename in (
            "team-build-request-v1.example.json",
            "battle-review-request-v1.example.json",
        ):
            with self.subTest(filename=filename):
                payload = json.loads((REPO_ROOT / "data/fixtures" / filename).read_text())
                self.assertEqual(payload["temporal_status"], "current")
                self.assertEqual(payload["format"]["regulation_id"], "regulation-m-c")
                self.assertEqual(
                    payload["format"]["active_window"]["end"],
                    "2026-12-02T01:59:00Z",
                )
                self.assertEqual(
                    payload["format_provenance"]["source_url"],
                    "https://www.pokemon.com/uk/news/get-ready-for-regulation-set-m-c-in-pokemon-champions",
                )

    def test_checked_in_battle_state_example_is_a_current_designation(self):
        designations = {
            label: (status, start, end)
            for label, status, start, end in self.module._iter_designations(REPO_ROOT)
        }

        status, start, end = designations[
            "data/fixtures/battle-state-v1.example.json"
        ]
        self.assertEqual(status, "current")
        self.assertEqual(start, datetime(2026, 9, 9, 2, tzinfo=timezone.utc))
        self.assertEqual(end, datetime(2026, 12, 2, 1, 59, tzinfo=timezone.utc))

    def test_battle_state_example_fails_after_its_provenance_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_designated_artifacts(
                root,
                current_start="2026-01-01T00:00:00Z",
                current_end="2026-12-31T23:59:59Z",
            )
            fixture = root / "data/fixtures/battle-state-v1.example.json"
            fixture.parent.mkdir(parents=True, exist_ok=True)
            fixture.write_text(
                json.dumps(
                    {
                        "schema_version": "battle-state-v1",
                        "format_provenance": {
                            "regulation_id": "regulation-expired",
                            "active_window": {
                                "start": "2026-01-01T00:00:00Z",
                                "end": "2026-02-01T00:00:00Z",
                            },
                        },
                    }
                )
            )

            expired = self.module.find_expired_current_artifacts(
                root, now=datetime(2026, 2, 1, 0, 0, 1, tzinfo=timezone.utc)
            )

        self.assertEqual(len(expired), 1)
        self.assertIn("battle-state-v1.example.json", expired[0])
        self.assertIn("2026-02-01T00:00:00Z", expired[0])

    def test_checked_in_meta_snapshot_example_is_explicitly_historical(self):
        payload = json.loads(
            (REPO_ROOT / "data/snapshots/meta-snapshot-v1.example.json").read_text()
        )

        self.assertEqual(payload["temporal_status"], "historical")
        self.assertEqual(payload["format"]["regulation_id"], "regulation-m-a")
        self.assertEqual(
            payload["format"]["active_window"],
            {
                "start": "2026-04-08T02:00:00Z",
                "end": "2026-06-17T01:59:00Z",
            },
        )
        self.assertTrue(any("historical" in note.lower() for note in payload["notes"]))

    def test_repository_current_designations_are_fresh_on_verified_date(self):
        expired = self.module.find_expired_current_artifacts(
            REPO_ROOT, now=datetime(2026, 9, 13, 12, tzinfo=timezone.utc)
        )

        self.assertEqual(expired, ())
