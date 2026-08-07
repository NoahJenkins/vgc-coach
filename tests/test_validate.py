from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATE_PATH = REPO_ROOT / "tools" / "validate.py"


def load_validate_module():
    spec = importlib.util.spec_from_file_location("validate_module", VALIDATE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ValidateTests(unittest.TestCase):
    def test_scope_selects_expected_commands(self):
        module = load_validate_module()

        core = module.build_validation_steps(
            "core",
            python_executable="/controlled/python",
            pnpm_executable="controlled-pnpm",
        )
        site = module.build_validation_steps(
            "site",
            python_executable="/controlled/python",
            pnpm_executable="controlled-pnpm",
        )
        all_steps = module.build_validation_steps(
            "all",
            python_executable="/controlled/python",
            pnpm_executable="controlled-pnpm",
        )

        self.assertEqual(
            [(step.name, step.argv) for step in core],
            [
                (
                    "Python tests",
                    (
                        "/controlled/python",
                        "-m",
                        "unittest",
                        "discover",
                        "-s",
                        "tests",
                        "-p",
                        "test_*.py",
                    ),
                ),
                (
                    "source-registry render check",
                    (
                        "/controlled/python",
                        "tools/render_source_registry_docs.py",
                        "check",
                    ),
                ),
                (
                    "current-format freshness check",
                    (
                        "/controlled/python",
                        "tools/check_format_freshness.py",
                    ),
                ),
                (
                    "generated-plugin drift check",
                    (
                        "/controlled/python",
                        "tools/build_plugins.py",
                        "check",
                    ),
                ),
            ],
        )
        self.assertEqual(
            [(step.name, step.argv) for step in site],
            [
                (
                    "production site build",
                    ("controlled-pnpm", "--dir", "site", "run", "build"),
                )
            ],
        )
        self.assertEqual(all_steps, (*core, *site))

    def test_command_failure_propagates_exit_code_and_stops_later_steps(self):
        module = load_validate_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            log_path = tmp_path / "commands.log"
            success_path = tmp_path / "success.py"
            failure_path = tmp_path / "failure.py"
            never_path = tmp_path / "never.py"
            success_path.write_text(
                "from pathlib import Path\n"
                f"Path({str(log_path)!r}).open('a').write('success\\n')\n"
            )
            failure_path.write_text(
                "from pathlib import Path\n"
                "import sys\n"
                f"Path({str(log_path)!r}).open('a').write('failure\\n')\n"
                "sys.exit(7)\n"
            )
            never_path.write_text(
                "from pathlib import Path\n"
                f"Path({str(log_path)!r}).open('a').write('never\\n')\n"
            )
            steps = (
                module.ValidationStep(
                    "successful controlled command",
                    (sys.executable, str(success_path)),
                ),
                module.ValidationStep(
                    "failing controlled command",
                    (sys.executable, str(failure_path)),
                ),
                module.ValidationStep(
                    "unreached controlled command",
                    (sys.executable, str(never_path)),
                ),
            )

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = module.run_validation_steps(steps, repo_root=REPO_ROOT)

            commands_run = log_path.read_text().splitlines()

        self.assertEqual(exit_code, 7)
        self.assertEqual(commands_run, ["success", "failure"])
        self.assertIn("failing controlled command", stderr.getvalue())
        self.assertIn("exit code 7", stderr.getvalue())

    def test_missing_prerequisite_fails_before_running_commands(self):
        module = load_validate_module()
        step = module.ValidationStep(
            "missing controlled command",
            ("vgc-coach-command-that-does-not-exist",),
        )

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = module.run_validation_steps((step,), repo_root=REPO_ROOT)

        self.assertEqual(exit_code, 2)
        self.assertIn("Missing prerequisite", stderr.getvalue())
        self.assertIn("vgc-coach-command-that-does-not-exist", stderr.getvalue())
        self.assertIn("missing controlled command", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
