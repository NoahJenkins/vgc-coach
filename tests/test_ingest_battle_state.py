from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "ingest_battle_state.py"
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
    ) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            [sys.executable, str(CLI_PATH), input_path, *arguments],
            cwd=REPO_ROOT,
            input=stdin,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def run_document(self, document: dict, *arguments: str):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "battle.json"
            input_path.write_text(json.dumps(document))
            return self.run_cli(str(input_path), *arguments)

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
                self.assertIn(f"{field}.side".encode(), result.stderr)

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

    def test_malformed_json_is_reported_without_traceback(self):
        result = self.run_cli("-", stdin=b'{"schema_version":')

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"invalid JSON", result.stderr)
        self.assertNotIn(b"Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
