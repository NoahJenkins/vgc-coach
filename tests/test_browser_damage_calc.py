import base64
import importlib.util
import json
import os
import pathlib
import signal
import sys
import tempfile
import time
import unittest
from unittest import mock


MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "tools" / "browser_damage_calc.py"


def load_module():
    spec = importlib.util.spec_from_file_location("browser_damage_calc", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class BrowserDamageCalcTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def sample_request(self):
        return {
            "goal": "Check whether bulky Charizard survives Pelipper rain pressure long enough to justify the spread.",
            "calc_type": "survival",
            "move": "Hurricane",
            "attacker": {
                "species": "Pelipper",
                "level": 50,
                "ability": "Drizzle",
                "item": "Choice Specs",
                "nature": "Modest",
                "evs": {"hp": 0, "at": 0, "df": 0, "sa": 32, "sd": 2, "sp": 32},
            },
            "defender": {
                "species": "Charizard",
                "level": 50,
                "ability": "Blaze",
                "item": "Sitrus Berry",
                "nature": "Timid",
                "evs": {"hp": 32, "at": 0, "df": 12, "sa": 0, "sd": 20, "sp": 2},
            },
            "field": {
                "weather": "Rain",
                "format": "Doubles",
                "helping_hand": False,
                "terrain": "None",
            },
        }

    def test_complete_damage_request_is_exact_eligible(self):
        request = self.module.parse_request(self.sample_request())

        self.assertTrue(self.module.is_exact_eligible(request))
        self.assertEqual(request.calc_type, "survival")

    def test_speed_requests_stay_out_of_exact_browser_path(self):
        payload = self.sample_request()
        payload["calc_type"] = "speed"
        payload["move"] = ""
        request = self.module.parse_request(payload)

        self.assertFalse(self.module.is_exact_eligible(request))

    def test_url_encoding_places_requested_move_first(self):
        request = self.module.parse_request(self.sample_request())

        url = self.module.build_calc_url(request)
        parsed = self.module.decode_calc_url(url)

        self.assertEqual(parsed["attSet"]["name"], "Pelipper")
        self.assertEqual(parsed["attSet"]["set"]["moves"][0], "Hurricane")
        self.assertEqual(parsed["defSet"]["name"], "Charizard")
        self.assertEqual(parsed["attSet"]["ruleset"], "champions")

    def test_missing_move_causes_blocked_result(self):
        payload = self.sample_request()
        payload["move"] = ""

        result = self.module.run_from_payload(payload, runner=lambda req: None)

        self.assertEqual(result["status"], "blocked")
        self.assertIn("move", result["failure_reason"].lower())

    def test_runner_failure_downgrades_to_fallback(self):
        request = self.module.parse_request(self.sample_request())

        def failing_runner(_request):
            raise self.module.BrowserCalcError("selector drift")

        result = self.module.execute_exact_calc(request, runner=failing_runner)

        self.assertEqual(result.status, "fallback")
        self.assertEqual(result.site, "pikalytics")
        self.assertIn("selector drift", result.failure_reason)

    def test_extracted_result_preserves_assumptions(self):
        request = self.module.parse_request(self.sample_request())

        def successful_runner(_request):
            return self.module.CalcResult(
                status="exact",
                backend="agent-browser",
                site="pikalytics",
                numeric_result={
                    "damage": "145-171 (92.3 - 108.9%)",
                    "ko_chance": "50% chance to OHKO",
                    "summary": "252+ SpA Pelipper Hurricane vs. 252 HP / 116 SpD Charizard in Rain: 145-171 (92.3 - 108.9%) -- 50% chance to OHKO",
                },
                assumptions_used={
                    "weather": "Rain",
                    "format": "Doubles",
                    "move": "Hurricane",
                },
                retrieval_timestamp="2026-04-20T14:00:00Z",
                failure_reason=None,
            )

        result = self.module.execute_exact_calc(request, runner=successful_runner)

        self.assertEqual(result.status, "exact")
        self.assertEqual(result.numeric_result["ko_chance"], "50% chance to OHKO")
        self.assertEqual(result.assumptions_used["weather"], "Rain")

    def fake_agent_browser(self, directory, body):
        executable = pathlib.Path(directory) / "agent-browser"
        executable.write_text(f"#!{sys.executable}\n" + body)
        executable.chmod(0o755)
        return executable

    def exact_runner_after_command(self, args, *, stdin=None):
        def runner(_request):
            self.module._run_agent_browser_command(args, stdin=stdin)
            return self.module.CalcResult(
                status="exact",
                backend="agent-browser",
                site="pikalytics",
                numeric_result={},
                assumptions_used={},
                retrieval_timestamp="2026-08-06T00:00:00Z",
                failure_reason=None,
            )

        return runner

    def process_exists(self, pid):
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        return True

    def test_agent_browser_timeout_terminates_and_returns_clear_fallback(self):
        request = self.module.parse_request(self.sample_request())

        with tempfile.TemporaryDirectory() as tmp:
            self.fake_agent_browser(tmp, "import time\ntime.sleep(1)\n")
            started = time.monotonic()
            with mock.patch.dict(os.environ, {"PATH": tmp}), mock.patch.object(
                self.module, "AGENT_BROWSER_TIMEOUT_SECONDS", 0.05, create=True
            ), mock.patch.object(
                self.module, "PROCESS_TERMINATE_GRACE_SECONDS", 0.05, create=True
            ):
                result = self.module.execute_exact_calc(
                    request,
                    runner=lambda req: self.module.run_agent_browser_backend(req),
                )
            elapsed = time.monotonic() - started

        self.assertEqual(result.status, "fallback")
        self.assertIn("timed out", result.failure_reason.lower())
        self.assertLess(elapsed, 0.8)

    def test_agent_browser_stdout_limit_returns_clear_fallback(self):
        request = self.module.parse_request(self.sample_request())

        with tempfile.TemporaryDirectory() as tmp:
            self.fake_agent_browser(tmp, "print('x' * 1024)\n")

            with mock.patch.dict(os.environ, {"PATH": tmp}), mock.patch.object(
                self.module, "MAX_AGENT_BROWSER_STDOUT_BYTES", 128, create=True
            ):
                result = self.module.execute_exact_calc(
                    request,
                    runner=self.exact_runner_after_command(["open", "test"]),
                )

        self.assertEqual(result.status, "fallback")
        self.assertIn("stdout exceeded", result.failure_reason.lower())
        self.assertNotIn("x" * 128, result.failure_reason)

    def test_agent_browser_stderr_limit_returns_clear_fallback(self):
        request = self.module.parse_request(self.sample_request())

        with tempfile.TemporaryDirectory() as tmp:
            self.fake_agent_browser(
                tmp,
                "import sys\nsys.stderr.write('e' * 1024)\nsys.exit(1)\n",
            )
            with mock.patch.dict(os.environ, {"PATH": tmp}), mock.patch.object(
                self.module, "MAX_AGENT_BROWSER_STDERR_BYTES", 128, create=True
            ):
                result = self.module.execute_exact_calc(
                    request,
                    runner=lambda _req: self.module._run_agent_browser_command(["open", "test"]),
                )

        self.assertEqual(result.status, "fallback")
        self.assertIn("stderr exceeded", result.failure_reason.lower())
        self.assertNotIn("e" * 128, result.failure_reason)

    def test_agent_browser_stdin_backpressure_obeys_command_deadline(self):
        request = self.module.parse_request(self.sample_request())
        payload = "x" * (2 * 1024 * 1024)

        with tempfile.TemporaryDirectory() as tmp:
            self.fake_agent_browser(tmp, "import time\ntime.sleep(1)\n")
            started = time.monotonic()
            with mock.patch.dict(os.environ, {"PATH": tmp}), mock.patch.object(
                self.module, "MAX_AGENT_BROWSER_STDIN_BYTES", len(payload) + 1, create=True
            ), mock.patch.object(
                self.module, "AGENT_BROWSER_TIMEOUT_SECONDS", 0.05
            ), mock.patch.object(self.module, "PROCESS_TERMINATE_GRACE_SECONDS", 0.05):
                result = self.module.execute_exact_calc(
                    request,
                    runner=self.exact_runner_after_command(
                        ["eval", "--stdin"],
                        stdin=payload,
                    ),
                )
            elapsed = time.monotonic() - started

        self.assertEqual(result.status, "fallback")
        self.assertIn("timed out", result.failure_reason.lower())
        self.assertLess(elapsed, 0.8)

    def test_agent_browser_stdin_limit_fails_before_process_start(self):
        request = self.module.parse_request(self.sample_request())

        with tempfile.TemporaryDirectory() as tmp:
            marker = pathlib.Path(tmp) / "started"
            self.fake_agent_browser(
                tmp,
                f"from pathlib import Path\nPath({str(marker)!r}).write_text('started')\n",
            )
            with mock.patch.dict(os.environ, {"PATH": tmp}), mock.patch.object(
                self.module, "MAX_AGENT_BROWSER_STDIN_BYTES", 128, create=True
            ):
                result = self.module.execute_exact_calc(
                    request,
                    runner=self.exact_runner_after_command(
                        ["eval", "--stdin"],
                        stdin="x" * 1024,
                    ),
                )

            self.assertFalse(marker.exists())

        self.assertEqual(result.status, "fallback")
        self.assertIn("stdin exceeded", result.failure_reason.lower())

    @unittest.skipUnless(os.name == "posix", "POSIX process-group regression")
    def test_timeout_kills_sigterm_ignoring_process_group_descendant(self):
        request = self.module.parse_request(self.sample_request())
        child_pid = None

        with tempfile.TemporaryDirectory() as tmp:
            pid_file = pathlib.Path(tmp) / "child.pid"
            child_code = (
                "import os, signal, sys, time; "
                "signal.signal(signal.SIGTERM, signal.SIG_IGN); "
                "open(sys.argv[1], 'w').write(str(os.getpid())); "
                "time.sleep(30)"
            )
            body = (
                "import subprocess, sys, time\n"
                f"subprocess.Popen([sys.executable, '-c', {child_code!r}, sys.argv[-1]])\n"
                "time.sleep(30)\n"
            )
            self.fake_agent_browser(tmp, body)
            try:
                with mock.patch.dict(os.environ, {"PATH": tmp}), mock.patch.object(
                    self.module, "AGENT_BROWSER_TIMEOUT_SECONDS", 0.5
                ), mock.patch.object(
                    self.module, "PROCESS_TERMINATE_GRACE_SECONDS", 0.5
                ):
                    result = self.module.execute_exact_calc(
                        request,
                        runner=self.exact_runner_after_command(
                            ["test-descendant", str(pid_file)]
                        ),
                    )
                child_pid = int(pid_file.read_text())
                self.assertFalse(self.process_exists(child_pid))
            finally:
                if child_pid is None and pid_file.exists():
                    child_pid = int(pid_file.read_text())
                if child_pid is not None and self.process_exists(child_pid):
                    os.kill(child_pid, signal.SIGKILL)

        self.assertEqual(result.status, "fallback")
        self.assertIn("timed out", result.failure_reason.lower())

    def test_non_posix_platform_fails_closed_before_process_start(self):
        request = self.module.parse_request(self.sample_request())

        with tempfile.TemporaryDirectory() as tmp:
            marker = pathlib.Path(tmp) / "started"
            self.fake_agent_browser(
                tmp,
                f"from pathlib import Path\nPath({str(marker)!r}).write_text('started')\n",
            )
            with mock.patch.dict(os.environ, {"PATH": tmp}), mock.patch.object(
                self.module.os, "name", "nt"
            ):
                result = self.module.execute_exact_calc(
                    request,
                    runner=self.exact_runner_after_command(["open", "test"]),
                )

            self.assertFalse(marker.exists())

        self.assertEqual(result.status, "fallback")
        self.assertIn("posix", result.failure_reason.lower())

    def test_oversized_extracted_remote_text_returns_clear_fallback(self):
        request = self.module.parse_request(self.sample_request())
        oversized = json.dumps({"summary": "remote" * 100})
        responses = iter(["", "", "", "", oversized, ""])

        with mock.patch.object(
            self.module,
            "_run_agent_browser_command",
            side_effect=lambda *_args, **_kwargs: next(responses),
        ), mock.patch.object(
            self.module, "MAX_EXTRACTED_TEXT_BYTES", 128, create=True
        ):
            result = self.module.execute_exact_calc(
                request,
                runner=self.module.run_agent_browser_backend,
            )

        self.assertEqual(result.status, "fallback")
        self.assertIn("extracted calc text exceeded", result.failure_reason.lower())

    def test_bounded_browser_backend_preserves_exact_damage_contract(self):
        request = self.module.parse_request(self.sample_request())
        extracted = json.dumps(
            {
                "summary": "Damage: 145-171 (92.3 - 108.9%) Chance to KO: 50% chance to OHKO"
            }
        )
        responses = iter(["", "", "", "", extracted, ""])

        with mock.patch.object(
            self.module,
            "_run_agent_browser_command",
            side_effect=lambda *_args, **_kwargs: next(responses),
        ):
            result = self.module.run_agent_browser_backend(request)

        self.assertEqual(result.status, "exact")
        self.assertEqual(result.numeric_result["damage"], "145-171 (92.3 - 108.9%)")
        self.assertEqual(result.numeric_result["ko_chance"], "50% chance to OHKO")

    def test_speed_request_remains_blocked_without_invoking_browser(self):
        payload = self.sample_request()
        payload["calc_type"] = "speed"
        payload["move"] = ""
        runner = mock.Mock(side_effect=AssertionError("browser must not run"))

        result = self.module.run_from_payload(payload, runner=runner)

        self.assertEqual(result["status"], "blocked")
        self.assertIn("only damage, ko, and survival", result["failure_reason"].lower())
        runner.assert_not_called()


if __name__ == "__main__":
    unittest.main()
