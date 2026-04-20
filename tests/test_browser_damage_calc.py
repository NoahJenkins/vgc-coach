import base64
import importlib.util
import json
import pathlib
import sys
import unittest


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


if __name__ == "__main__":
    unittest.main()
