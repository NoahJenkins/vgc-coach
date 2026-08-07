from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "ingest_battle_state.py"
PACKAGED_CLI_PATH = (
    REPO_ROOT / "plugins" / "vgc-coach-codex" / "tools" / "ingest_battle_state.py"
)
ALL_CLI_PATHS = (
    CLI_PATH,
    PACKAGED_CLI_PATH,
    REPO_ROOT / "plugins" / "vgc-coach-claude" / "tools" / "ingest_battle_state.py",
    REPO_ROOT / "plugins" / "vgc-coach-opencode" / "tools" / "ingest_battle_state.py",
)
SCHEMA_PATH = REPO_ROOT / "data" / "schemas" / "battle-state-v1.schema.json"
EXAMPLE_PATH = REPO_ROOT / "data" / "fixtures" / "battle-state-v1.example.json"


def minimal_document() -> dict:
    return {
        "schema_version": "battle-state-v1",
        "format_provenance": {
            "game": "pokemon-champions",
            "battle_mode": "doubles",
            "regulation_id": "regulation-m-b",
            "official_source_url": "https://news.pokemon-home.com/en/page/776.html",
            "verified_at": "2026-08-06T12:00:00Z",
        },
        "battle": {
            "source_type": "manual_transcription",
            "player_sides": [
                {"side": "self"},
                {"side": "opponent"},
            ],
        },
        "teams": {
            "self": {"preview_roster": []},
            "opponent": {"preview_roster": []},
        },
    }


class BattleStateIngestionTests(unittest.TestCase):
    maxDiff = None

    def run_cli(
        self,
        input_path: str,
        *arguments: str,
        stdin: bytes | None = None,
        cli_path: Path = CLI_PATH,
    ) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            [sys.executable, str(cli_path), input_path, *arguments],
            cwd=REPO_ROOT,
            input=stdin,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def run_document(
        self,
        document: dict,
        *arguments: str,
        cli_path: Path = CLI_PATH,
    ):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "battle.json"
            input_path.write_text(json.dumps(document))
            return self.run_cli(str(input_path), *arguments, cli_path=cli_path)

    def test_schema_is_draft_2020_12_with_stable_identifier(self):
        schema = json.loads(SCHEMA_PATH.read_text())

        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(
            schema["$id"],
            "https://vgccoach.com/schemas/battle-state-v1.schema.json",
        )
        self.assertEqual(schema["properties"]["schema_version"]["const"], "battle-state-v1")

    def test_valid_minimal_document_is_canonical_and_does_not_invent_unknowns(self):
        result = self.run_document(minimal_document())

        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(result.stderr, b"")
        decoded = json.loads(result.stdout)
        self.assertNotIn("occurred_at", decoded["battle"])
        self.assertNotIn("selected", decoded["teams"]["opponent"])
        self.assertNotIn("outcome", decoded)
        self.assertEqual(decoded["turn_events"], [])
        self.assertEqual(decoded["revealed_information"], [])
        self.assertEqual(
            result.stdout,
            (json.dumps(decoded, sort_keys=True, separators=(",", ":")) + "\n").encode(),
        )

    def test_full_example_is_valid_and_pretty_output_is_deterministic(self):
        first = self.run_cli(str(EXAMPLE_PATH), "--pretty")
        second = self.run_cli(str(EXAMPLE_PATH), "--pretty")

        self.assertEqual(first.returncode, 0, first.stderr.decode())
        self.assertEqual(first.stdout, second.stdout)
        decoded = json.loads(first.stdout)
        self.assertEqual(decoded["schema_version"], "battle-state-v1")
        self.assertEqual(decoded["format_provenance"]["regulation_id"], "regulation-m-b")
        self.assertEqual(decoded["outcome"]["winner"], "self")
        self.assertEqual(
            decoded["teams"]["self"]["active"],
            [{"species_id": "whimsicott"}, {"species_id": "charizard"}],
        )
        self.assertEqual(
            decoded["teams"]["self"]["bench"],
            [{"species_id": "rillaboom"}, {"species_id": "incineroar"}],
        )
        self.assertTrue(first.stdout.endswith(b"\n"))

    def test_stdin_to_stdout_uses_same_canonical_representation(self):
        encoded = json.dumps(minimal_document()).encode()
        result = self.run_cli("-", stdin=encoded)

        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(
            json.loads(result.stdout),
            json.loads(encoded)
            | {
                "turn_events": [],
                "revealed_information": [],
            },
        )

    def test_explicit_output_is_the_only_written_path_and_input_is_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "battle.json"
            output_path = Path(tmp) / "nested" / "canonical.json"
            original = json.dumps(minimal_document(), indent=3).encode()
            input_path.write_bytes(original)

            result = self.run_cli(str(input_path), "--output", str(output_path), "--pretty")

            self.assertEqual(result.returncode, 0, result.stderr.decode())
            self.assertEqual(result.stdout, b"")
            self.assertEqual(input_path.read_bytes(), original)
            self.assertEqual(json.loads(output_path.read_text()), json.loads(original) | {
                "turn_events": [],
                "revealed_information": [],
            })

    def test_output_cannot_replace_the_input_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "battle.json"
            original = json.dumps(minimal_document(), indent=3).encode()
            input_path.write_bytes(original)

            result = self.run_cli(str(input_path), "--output", str(input_path))

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, b"")
            self.assertEqual(input_path.read_bytes(), original)
            self.assertIn(b"output path must differ from input path", result.stderr)

    def test_invalid_document_does_not_create_or_replace_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "invalid.json"
            output_path = Path(tmp) / "existing.json"
            input_path.write_text("{not json")
            output_path.write_bytes(b"keep-me")

            result = self.run_cli(str(input_path), "--output", str(output_path))

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, b"")
            self.assertEqual(output_path.read_bytes(), b"keep-me")
            self.assertIn(b"invalid JSON", result.stderr)

    def test_input_over_one_mebibyte_is_rejected_without_parsing(self):
        oversized = b" " * (1024 * 1024 + 1)
        result = self.run_cli("-", stdin=oversized)

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, b"")
        self.assertIn(b"exceeds 1048576-byte limit", result.stderr)

    def test_unsupported_schema_version_is_rejected(self):
        document = minimal_document()
        document["schema_version"] = "battle-state-v2"

        result = self.run_document(document)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"unsupported schema_version", result.stderr)

    def test_missing_format_provenance_is_rejected(self):
        document = minimal_document()
        del document["format_provenance"]

        result = self.run_document(document)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"format_provenance is required", result.stderr)

    def test_active_window_end_before_start_is_rejected(self):
        document = minimal_document()
        document["format_provenance"]["active_window"] = {
            "start": "2026-09-02T01:59:00Z",
            "end": "2026-06-17T02:00:00Z",
        }

        result = self.run_document(document)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"active_window.end must not precede", result.stderr)

    def test_rfc3339_offsets_are_accepted_by_root_and_packaged_clis(self):
        document = minimal_document()
        document["format_provenance"]["verified_at"] = "2026-08-06T07:00:00-05:00"
        document["format_provenance"]["active_window"] = {
            "start": "2026-06-17T02:00:00+00:00",
            "end": "2026-09-09T01:59:00Z",
        }

        for cli_path in (CLI_PATH, PACKAGED_CLI_PATH):
            with self.subTest(cli=cli_path):
                result = self.run_document(document, cli_path=cli_path)
                self.assertEqual(result.returncode, 0, result.stderr.decode())

    def test_non_rfc3339_date_time_spellings_are_rejected_by_root_and_package(self):
        for value in ("20260806T120000Z", "2026-08-06X12:00:00Z"):
            for cli_path in (CLI_PATH, PACKAGED_CLI_PATH):
                with self.subTest(value=value, cli=cli_path):
                    document = minimal_document()
                    document["format_provenance"]["verified_at"] = value

                    result = self.run_document(document, cli_path=cli_path)

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(b"RFC 3339", result.stderr)
                    self.assertNotIn(b"Traceback", result.stderr)

    def test_rfc3339_component_bounds_are_enforced_by_every_cli(self):
        invalid_values = (
            "2026-08-06T24:00:00Z",
            "2026-08-06T24:00:00.0000001Z",
            "2026-08-06T23:60:00Z",
            "2026-08-06T23:59:61Z",
            "2026-08-06T12:00:00+00:60",
            "2026-08-06T12:00:00-22:99",
            "2026-08-06T12:00:00+24:00",
            "2026-08-06T12:00:00-23:60",
        )
        for value in invalid_values:
            for cli_path in ALL_CLI_PATHS:
                with self.subTest(value=value, cli=cli_path):
                    document = minimal_document()
                    document["format_provenance"]["verified_at"] = value

                    result = self.run_document(document, cli_path=cli_path)

                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, b"")
                    self.assertIn(b"RFC 3339", result.stderr)
                    self.assertNotIn(b"Traceback", result.stderr)

    def test_rfc3339_clock_offset_and_leap_second_boundaries_pass_every_cli(self):
        valid_values = (
            "0001-01-01T00:00:00-23:59",
            "2026-08-06T23:59:59+23:59",
            "2026-12-31T23:59:60Z",
            "2026-08-06t12:00:00.123456789z",
            "9999-12-31T23:59:59Z",
        )
        for value in valid_values:
            for cli_path in ALL_CLI_PATHS:
                with self.subTest(value=value, cli=cli_path):
                    document = minimal_document()
                    document["format_provenance"]["verified_at"] = value

                    result = self.run_document(document, cli_path=cli_path)

                    self.assertEqual(result.returncode, 0, result.stderr.decode())
                    self.assertEqual(
                        json.loads(result.stdout)["format_provenance"]["verified_at"],
                        value,
                    )

    def test_calendar_and_year_bounds_are_enforced_by_every_cli(self):
        invalid_values = (
            "0000-01-01T00:00:00Z",
            "2026-00-01T00:00:00Z",
            "2026-01-00T00:00:00Z",
            "2023-02-29T00:00:00Z",
            "1900-02-29T00:00:00Z",
            "2026-04-31T00:00:00Z",
        )
        valid_values = (
            "2000-02-29T00:00:00Z",
            "2024-02-29T00:00:00Z",
        )
        cases = [(value, False) for value in invalid_values]
        cases.extend((value, True) for value in valid_values)
        for value, expected_success in cases:
            for cli_path in ALL_CLI_PATHS:
                with self.subTest(value=value, cli=cli_path):
                    document = minimal_document()
                    document["format_provenance"]["verified_at"] = value

                    result = self.run_document(document, cli_path=cli_path)

                    if expected_success:
                        self.assertEqual(result.returncode, 0, result.stderr.decode())
                    else:
                        self.assertNotEqual(result.returncode, 0)
                        self.assertEqual(result.stdout, b"")
                        self.assertIn(b"RFC 3339", result.stderr)
                        self.assertNotIn(b"Traceback", result.stderr)

    def test_high_precision_active_window_ordering_is_exact_in_every_cli(self):
        cases = (
            (
                "2026-06-17T02:00:00.0000009Z",
                "2026-06-17T02:00:00.0000001Z",
                False,
            ),
            (
                "2026-06-17T02:00:00.1234569Z",
                "2026-06-17T02:00:00.1234561Z",
                False,
            ),
            (
                "2026-06-17T02:00:00.0000001Z",
                "2026-06-17T02:00:00.0000009Z",
                True,
            ),
            (
                "2026-06-17T02:00:00.1Z",
                "2026-06-17T02:00:00.100000000000000000Z",
                True,
            ),
            (
                "2026-06-17T03:00:00.123456789123456789+01:00",
                "2026-06-17T02:00:00.123456789123456789Z",
                True,
            ),
            (
                "2026-06-30T23:59:60.999999999Z",
                "2026-07-01T00:00:00Z",
                True,
            ),
            (
                "2026-07-01T00:00:00Z",
                "2026-06-30T23:59:60.999999999Z",
                False,
            ),
        )
        for start, end, expected_success in cases:
            for cli_path in ALL_CLI_PATHS:
                with self.subTest(start=start, end=end, cli=cli_path):
                    document = minimal_document()
                    document["format_provenance"]["active_window"] = {
                        "start": start,
                        "end": end,
                    }

                    result = self.run_document(document, cli_path=cli_path)

                    if expected_success:
                        self.assertEqual(result.returncode, 0, result.stderr.decode())
                    else:
                        self.assertNotEqual(result.returncode, 0)
                        self.assertEqual(result.stdout, b"")
                        self.assertIn(b"must not precede", result.stderr)
                        self.assertNotIn(b"Traceback", result.stderr)

    def test_malformed_http_authorities_are_rejected_without_traceback_in_both_clis(self):
        invalid_urls = (
            "https://@",
            "https://:443",
            "https://example.com:not-a-port",
            "https://example.com\\redirect",
            "https://example.com\n.evil",
            "https://[",
        )
        for value in invalid_urls:
            for cli_path in (CLI_PATH, PACKAGED_CLI_PATH):
                with self.subTest(value=value, cli=cli_path):
                    document = minimal_document()
                    document["format_provenance"]["official_source_url"] = value

                    result = self.run_document(document, cli_path=cli_path)

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(b"absolute HTTP(S) URL", result.stderr)
                    self.assertNotIn(b"Traceback", result.stderr)

    def test_non_uri_path_query_and_fragment_text_is_rejected_by_both_clis(self):
        invalid_urls = (
            "https://example.com/a b",
            "https://example.com/a\u00a0b",
            "https://example.com/%",
            "https://example.com/%2",
            "https://example.com/%zz",
            "https://example.com/a#b#c",
            "https://example.com/\u0085x",
            "https://example.com/café",
        )
        for value in invalid_urls:
            for cli_path in (CLI_PATH, PACKAGED_CLI_PATH):
                with self.subTest(value=value, cli=cli_path):
                    document = minimal_document()
                    document["format_provenance"]["official_source_url"] = value

                    result = self.run_document(document, cli_path=cli_path)

                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, b"")
                    self.assertIn(b"absolute HTTP(S) URL", result.stderr)
                    self.assertNotIn(b"Traceback", result.stderr)

    def test_valid_percent_encoded_query_fragment_and_ipv6_urls_pass_both_clis(self):
        valid_urls = (
            "https://example.com/a%20b/%E2%9C%93?next=%2Fteams%3Fa%3D1&label=a+b#section-1",
            "http://[2001:db8::1]:65535/a;b?x=@%2F#frag?ok",
        )
        for value in valid_urls:
            for cli_path in (CLI_PATH, PACKAGED_CLI_PATH):
                with self.subTest(value=value, cli=cli_path):
                    document = minimal_document()
                    document["format_provenance"]["official_source_url"] = value

                    result = self.run_document(document, cli_path=cli_path)

                    self.assertEqual(result.returncode, 0, result.stderr.decode())
                    self.assertEqual(
                        json.loads(result.stdout)["format_provenance"][
                            "official_source_url"
                        ],
                        value,
                    )

    def test_invalid_uri_never_replaces_explicit_output(self):
        document = minimal_document()
        document["format_provenance"]["official_source_url"] = (
            "https://example.com/\u0085x"
        )
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "battle.json"
            output_path = Path(tmp) / "existing.json"
            input_path.write_text(json.dumps(document))
            output_path.write_bytes(b"keep-me")

            result = self.run_cli(str(input_path), "--output", str(output_path))

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, b"")
            self.assertNotIn(b"Traceback", result.stderr)
            self.assertEqual(output_path.read_bytes(), b"keep-me")

    def test_duplicate_or_non_monotonic_event_order_is_rejected(self):
        for pairs in (
            [(1, 1), (1, 1)],
            [(2, 1), (1, 1)],
            [(1, 2), (1, 1)],
        ):
            with self.subTest(pairs=pairs):
                document = minimal_document()
                document["turn_events"] = [
                    {
                        "turn": turn,
                        "sequence": sequence,
                        "side": "self",
                        "kind": "observation",
                        "observations": ["Known at this point."],
                    }
                    for turn, sequence in pairs
                ]

                result = self.run_document(document)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(b"strictly increasing", result.stderr)

    def test_unknown_event_kind_and_side_are_rejected(self):
        for field, value in (("kind", "execute_instruction"), ("side", "spectator")):
            with self.subTest(field=field):
                document = minimal_document()
                event = {
                    "turn": 1,
                    "sequence": 1,
                    "side": "self",
                    "kind": "observation",
                }
                event[field] = value
                document["turn_events"] = [event]

                result = self.run_document(document)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(field.encode(), result.stderr)

    def test_invalid_actor_and_target_sides_are_rejected(self):
        for field in ("actor", "target"):
            with self.subTest(field=field):
                document = minimal_document()
                document["turn_events"] = [
                    {
                        "turn": 1,
                        "sequence": 1,
                        "side": "self",
                        "kind": "move",
                        field: {"side": "spectator", "species_id": "charizard"},
                    }
                ]

                result = self.run_document(document)

                self.assertNotEqual(result.returncode, 0)
                expected_path = "actor.side" if field == "actor" else "target"
                self.assertIn(expected_path.encode(), result.stderr)

    def test_field_is_a_valid_event_target_but_not_an_actor(self):
        valid = minimal_document()
        valid["turn_events"] = [
            {
                "turn": 1,
                "sequence": 1,
                "side": "self",
                "kind": "weather",
                "target": {"side": "field"},
            }
        ]
        invalid = minimal_document()
        invalid["turn_events"] = [
            {
                "turn": 1,
                "sequence": 1,
                "side": "field",
                "kind": "weather",
                "actor": {"side": "field"},
            }
        ]

        valid_result = self.run_document(valid)
        invalid_result = self.run_document(invalid)

        self.assertEqual(valid_result.returncode, 0, valid_result.stderr.decode())
        self.assertNotEqual(invalid_result.returncode, 0)
        self.assertIn(b"actor.side", invalid_result.stderr)

    def test_field_target_cannot_claim_a_pokemon_or_slot(self):
        for extra in (
            {"species_id": "pelipper"},
            {"form_id": "male"},
            {"position": "bench"},
        ):
            with self.subTest(extra=extra):
                document = minimal_document()
                document["turn_events"] = [
                    {
                        "turn": 1,
                        "sequence": 1,
                        "side": "field",
                        "kind": "weather",
                        "target": {"side": "field"} | extra,
                    }
                ]

                result = self.run_document(document)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(b"target", result.stderr)

    def test_game_number_cannot_exceed_known_series_length(self):
        document = minimal_document()
        document["battle"]["best_of"] = 1
        document["battle"]["game_number"] = 3

        result = self.run_document(document)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"game_number must not exceed best_of", result.stderr)

    def test_team_member_cannot_be_active_and_benched_at_once(self):
        document = minimal_document()
        document["teams"]["self"] |= {
            "active": [{"species_id": "charizard"}],
            "bench": [{"species_id": "charizard"}],
        }

        result = self.run_document(document)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"active and bench", result.stderr)

    def test_revealed_value_and_evidence_must_contain_non_whitespace_text(self):
        for field, value in (("value", ""), ("evidence", "   \n")):
            with self.subTest(field=field):
                document = minimal_document()
                reveal = {
                    "turn": 1,
                    "side": "opponent",
                    "kind": "item",
                    "value": "focus-sash",
                    "evidence": "The item activated.",
                }
                reveal[field] = value
                document["revealed_information"] = [reveal]

                result = self.run_document(document)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(field.encode(), result.stderr)

    def test_trailing_line_terminator_identifiers_are_rejected_by_every_cli(self):
        def regulation(document: dict) -> None:
            document["format_provenance"]["regulation_id"] = "regulation-m-b\n"

        def species(document: dict) -> None:
            document["teams"]["self"]["preview_roster"] = [
                {"species_id": "charizard\n"}
            ]

        def form(document: dict) -> None:
            document["teams"]["self"]["preview_roster"] = [
                {"species_id": "charizard", "form_id": "mega-x\n"}
            ]

        def action(document: dict) -> None:
            document["turn_events"] = [
                {
                    "turn": 1,
                    "sequence": 1,
                    "side": "self",
                    "kind": "move",
                    "action": {"identifier": "tailwind\n"},
                }
            ]

        for field, mutate in (
            ("regulation_id", regulation),
            ("species_id", species),
            ("form_id", form),
            ("action.identifier", action),
        ):
            for cli_path in ALL_CLI_PATHS:
                with self.subTest(field=field, cli=cli_path):
                    document = minimal_document()
                    mutate(document)

                    result = self.run_document(document, cli_path=cli_path)

                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, b"")
                    self.assertNotIn(b"Traceback", result.stderr)

    def test_unicode_nel_alone_is_whitespace_in_reveals_for_every_cli(self):
        for field in ("value", "evidence"):
            for cli_path in ALL_CLI_PATHS:
                with self.subTest(field=field, cli=cli_path):
                    document = minimal_document()
                    reveal = {
                        "turn": 1,
                        "side": "opponent",
                        "kind": "item",
                        "value": "focus-sash",
                        "evidence": "The item activated.",
                    }
                    reveal[field] = "\u0085"
                    document["revealed_information"] = [reveal]

                    result = self.run_document(document, cli_path=cli_path)

                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, b"")
                    self.assertNotIn(b"Traceback", result.stderr)

    def test_schema_patterns_have_expected_ecmascript_boundaries(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is unavailable for ECMAScript regex comparison")
        schema = json.loads(SCHEMA_PATH.read_text())
        anchored_patterns = {
            schema["$defs"]["pokemonRef"]["properties"]["species_id"]["pattern"],
            schema["$defs"]["eventDetail"]["properties"]["identifier"]["pattern"],
            schema["$defs"]["formatProvenance"]["properties"]["regulation_id"][
                "pattern"
            ],
        }
        reveal_pattern = schema["$defs"]["revealedFact"]["properties"]["value"][
            "pattern"
        ]
        date_pattern = schema["$defs"]["rfc3339DateTime"]["pattern"]

        def javascript_matches(pattern: str, value: str) -> bool:
            completed = subprocess.run(
                [
                    node,
                    "-e",
                    "const [p,v]=process.argv.slice(1); process.exit(new RegExp(p, 'u').test(v) ? 0 : 1)",
                    pattern,
                    value,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertIn(completed.returncode, (0, 1), completed.stderr.decode())
            return completed.returncode == 0

        for pattern in anchored_patterns:
            with self.subTest(pattern=pattern):
                self.assertTrue(javascript_matches(pattern, "regulation-m-b"))
                self.assertFalse(javascript_matches(pattern, "regulation-m-b\n"))
        self.assertTrue(javascript_matches(reveal_pattern, "useful evidence"))
        self.assertFalse(javascript_matches(reveal_pattern, "\u0085"))
        for value in (
            "2026-08-06T24:00:00Z",
            "2026-08-06T12:00:00+00:60",
            "0000-01-01T00:00:00Z",
        ):
            with self.subTest(date=value):
                self.assertFalse(javascript_matches(date_pattern, value))
        for value in (
            "2026-08-06T23:59:59+23:59",
            "2026-12-31T23:59:60Z",
            "2026-08-06t12:00:00.123456789z",
        ):
            with self.subTest(date=value):
                self.assertTrue(javascript_matches(date_pattern, value))

    def test_outcome_result_is_from_self_perspective_and_matches_winner(self):
        invalid_outcomes = (
            {"result": "win", "winner": "opponent"},
            {"result": "loss", "winner": "self"},
            {"result": "draw", "winner": "self"},
            {"result": "unknown", "winner": "opponent"},
            {"result": "win"},
        )
        for outcome in invalid_outcomes:
            with self.subTest(outcome=outcome):
                document = minimal_document()
                document["outcome"] = outcome

                result = self.run_document(document)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(b"outcome", result.stderr)

    def test_huge_integer_is_a_safe_error_and_preserves_explicit_output(self):
        document_text = json.dumps(minimal_document())
        huge_number = "9" * 5000
        payload = document_text.replace(
            '"source_type": "manual_transcription"',
            f'"source_type": "manual_transcription", "game_number": {huge_number}',
        ).encode()

        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "battle.json"
            output_path = Path(tmp) / "existing.json"
            input_path.write_bytes(payload)
            output_path.write_bytes(b"keep-me")

            result = self.run_cli(str(input_path), "--output", str(output_path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b"invalid JSON", result.stderr)
            self.assertNotIn(b"Traceback", result.stderr)
            self.assertEqual(output_path.read_bytes(), b"keep-me")

    def test_unpaired_surrogate_is_a_safe_error_and_preserves_explicit_output(self):
        document = minimal_document()
        document["battle"]["player_sides"][0]["display_name"] = "\ud800"
        payload = json.dumps(document).encode()

        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "battle.json"
            output_path = Path(tmp) / "existing.json"
            input_path.write_bytes(payload)
            output_path.write_bytes(b"keep-me")

            result = self.run_cli(str(input_path), "--output", str(output_path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b"Unicode scalar", result.stderr)
            self.assertNotIn(b"Traceback", result.stderr)
            self.assertEqual(output_path.read_bytes(), b"keep-me")

    def test_malformed_json_is_reported_without_traceback(self):
        result = self.run_cli("-", stdin=b'{"schema_version":')

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"invalid JSON", result.stderr)
        self.assertNotIn(b"Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
