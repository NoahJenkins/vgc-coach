#!/usr/bin/env python3
"""Validate and normalize a battle-state-v1 JSON document.

Input is capped at 1 MiB. The command performs no network access and does not
open paths referenced by document fields.
"""

from __future__ import annotations

import argparse
import copy
import ipaddress
import json
import os
import re
import sys
import tempfile
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "data" / "schemas" / "battle-state-v1.schema.json"
SUPPORTED_SCHEMA_VERSION = "battle-state-v1"
MAX_INPUT_BYTES = 1024 * 1024
RFC3339_PATTERN = re.compile(
    r"^(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})[Tt]"
    r"(?P<hour>[0-9]{2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2})"
    r"(?P<fraction>\.[0-9]+)?(?P<offset>[Zz]|[+-][0-9]{2}:[0-9]{2})$"
)
HOSTNAME_PATTERN = re.compile(
    r"^(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)"
    r"(?:\.(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?))*$"
)
RFC3986_PCHAR = r"(?:[A-Za-z0-9._~!$&'()*+,;=:@-]|%[0-9A-Fa-f]{2})"
RFC3986_PATH_PATTERN = re.compile(rf"^(?:/{RFC3986_PCHAR}*)*$")
RFC3986_QUERY_FRAGMENT_PATTERN = re.compile(
    rf"^(?:{RFC3986_PCHAR}|[/?])*$"
)
MALFORMED_PERCENT_ESCAPE_PATTERN = re.compile(r"%(?![0-9A-Fa-f]{2})")


class BattleStateError(ValueError):
    """A safe, user-facing validation failure."""


def _json_type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    raise RuntimeError(f"unsupported schema type: {expected}")


def _resolve_ref(root_schema: dict[str, Any], reference: str) -> dict[str, Any]:
    if not reference.startswith("#/"):
        raise RuntimeError(f"unsupported schema reference: {reference}")
    value: Any = root_schema
    for component in reference[2:].split("/"):
        value = value[component.replace("~1", "/").replace("~0", "~")]
    return value


def _format_path(path: tuple[str | int, ...]) -> str:
    if not path:
        return "document"
    rendered = ""
    for component in path:
        if isinstance(component, int):
            rendered += f"[{component}]"
        else:
            rendered += ("." if rendered else "") + component
    return rendered


def _parse_datetime(
    value: str,
    path: str,
    schema_pattern: str | None = None,
) -> datetime:
    match = RFC3339_PATTERN.fullmatch(value)
    if match is None or (
        schema_pattern is not None and re.fullmatch(schema_pattern, value) is None
    ):
        raise BattleStateError(f"{path} must be an RFC 3339 date-time")

    normalized = value[:10] + "T" + value[11:]
    if normalized.endswith(("Z", "z")):
        normalized = normalized[:-1] + "+00:00"
    leap_second = match.group("second") == "60"
    if leap_second:
        normalized = normalized[:17] + "59" + normalized[19:]
    try:
        parsed = datetime.fromisoformat(normalized)
        if leap_second:
            parsed += timedelta(seconds=1)
    except (OverflowError, ValueError) as exc:
        raise BattleStateError(f"{path} must be an RFC 3339 date-time") from exc
    if parsed.tzinfo is None:
        raise BattleStateError(f"{path} must include a timezone")
    return parsed


def _validate_uri(
    value: str,
    path: str,
    schema_pattern: str | None = None,
) -> None:
    def invalid() -> BattleStateError:
        return BattleStateError(f"{path} must be an absolute HTTP(S) URL")

    if (
        "\\" in value
        or any(
            character.isspace() or unicodedata.category(character) == "Cc"
            for character in value
        )
        or value.count("#") > 1
        or MALFORMED_PERCENT_ESCAPE_PATTERN.search(value) is not None
        or (schema_pattern is not None and re.fullmatch(schema_pattern, value) is None)
    ):
        raise invalid()
    try:
        parsed = urlsplit(value)
        hostname = parsed.hostname
        port = parsed.port
    except (UnicodeError, ValueError) as exc:
        raise invalid() from exc
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.netloc
        or hostname is None
        or parsed.username is not None
        or parsed.password is not None
        or (port is not None and not (0 <= port <= 65535))
    ):
        raise invalid()
    if ":" in hostname:
        try:
            ipaddress.IPv6Address(hostname)
        except ValueError as exc:
            raise invalid() from exc
    elif len(hostname) > 253 or HOSTNAME_PATTERN.fullmatch(hostname) is None:
        raise invalid()
    if (
        RFC3986_PATH_PATTERN.fullmatch(parsed.path) is None
        or RFC3986_QUERY_FRAGMENT_PATTERN.fullmatch(parsed.query) is None
        or RFC3986_QUERY_FRAGMENT_PATTERN.fullmatch(parsed.fragment) is None
    ):
        raise invalid()


def _require_unicode_scalar(value: str, path: str) -> None:
    if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
        raise BattleStateError(f"{path} must contain only Unicode scalar values")


def _validate_one_of(
    value: Any,
    options: list[dict[str, Any]],
    root_schema: dict[str, Any],
    path: tuple[str | int, ...],
) -> None:
    matches = 0
    for option in options:
        try:
            _validate_against_schema(value, option, root_schema, path)
        except BattleStateError:
            continue
        matches += 1
    if matches != 1:
        raise BattleStateError(
            f"{_format_path(path)} must match exactly one allowed schema shape"
        )


def _matches_schema_pattern(pattern: str, value: str) -> bool:
    """Match the repository's portable JSON Schema pattern subset.

    Anchored identifier patterns define the whole string, so fullmatch avoids
    Python's special end-before-final-newline behavior for ``$``. Unanchored
    patterns retain JSON Schema search semantics.
    """

    if pattern.startswith("^") and pattern.endswith("$"):
        return re.fullmatch(pattern, value) is not None
    return re.search(pattern, value) is not None


def _validate_against_schema(
    value: Any,
    schema: dict[str, Any],
    root_schema: dict[str, Any],
    path: tuple[str | int, ...] = (),
) -> None:
    if "$ref" in schema:
        _validate_against_schema(
            value,
            _resolve_ref(root_schema, schema["$ref"]),
            root_schema,
            path,
        )
        return

    if "oneOf" in schema:
        _validate_one_of(value, schema["oneOf"], root_schema, path)

    label = _format_path(path)
    expected = schema.get("type")
    if expected is not None:
        accepted = [expected] if isinstance(expected, str) else expected
        if not any(_json_type_matches(value, item) for item in accepted):
            raise BattleStateError(f"{label} must have type {' or '.join(accepted)}")

    if "const" in schema and value != schema["const"]:
        raise BattleStateError(f"{label} must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        allowed = ", ".join(repr(item) for item in schema["enum"])
        raise BattleStateError(f"{label} has an unknown value; expected one of: {allowed}")

    if isinstance(value, dict):
        for key in value:
            _require_unicode_scalar(key, f"{label} object key")
        for required in schema.get("required", []):
            if required not in value:
                missing = _format_path((*path, required))
                raise BattleStateError(f"{missing} is required")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            unknown = sorted(set(value) - set(properties))
            if unknown:
                raise BattleStateError(f"{label} has unknown field {unknown[0]!r}")
        for key, child in value.items():
            if key in properties:
                _validate_against_schema(child, properties[key], root_schema, (*path, key))

    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            raise BattleStateError(f"{label} has too few items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            raise BattleStateError(f"{label} has too many items")
        if schema.get("uniqueItems"):
            encoded = [
                json.dumps(item, sort_keys=True, separators=(",", ":"))
                for item in value
            ]
            if len(encoded) != len(set(encoded)):
                raise BattleStateError(f"{label} must not contain duplicate items")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                _validate_against_schema(item, item_schema, root_schema, (*path, index))

    if isinstance(value, str):
        _require_unicode_scalar(value, label)
        if len(value) < schema.get("minLength", 0):
            raise BattleStateError(f"{label} must not be empty")
        if schema.get("format") == "date-time":
            _parse_datetime(value, label, schema.get("pattern"))
        elif schema.get("format") == "uri":
            _validate_uri(value, label, schema.get("pattern"))
        elif "pattern" in schema and not _matches_schema_pattern(
            schema["pattern"], value
        ):
            raise BattleStateError(
                f"{label} does not match the required identifier format"
            )

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            raise BattleStateError(f"{label} must be at least {schema['minimum']}")


def validate_and_normalize(document: Any) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise BattleStateError("document must have type object")
    if "schema_version" not in document:
        raise BattleStateError("schema_version is required")
    if document["schema_version"] != SUPPORTED_SCHEMA_VERSION:
        raise BattleStateError(
            f"unsupported schema_version {document['schema_version']!r}; "
            f"expected {SUPPORTED_SCHEMA_VERSION!r}"
        )

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    _validate_against_schema(document, schema, schema)

    provenance = document["format_provenance"]
    active_window = provenance.get("active_window")
    if active_window:
        start = _parse_datetime(
            active_window["start"],
            "format_provenance.active_window.start",
        )
        end = _parse_datetime(
            active_window["end"],
            "format_provenance.active_window.end",
        )
        if end < start:
            raise BattleStateError(
                "format_provenance.active_window.end must not precede "
                "format_provenance.active_window.start"
            )

    sides = [entry["side"] for entry in document["battle"]["player_sides"]]
    if sorted(sides) != ["opponent", "self"]:
        raise BattleStateError("battle.player_sides must map self and opponent exactly once")

    battle = document["battle"]
    if (
        "best_of" in battle
        and "game_number" in battle
        and battle["game_number"] > battle["best_of"]
    ):
        raise BattleStateError("battle.game_number must not exceed best_of")

    for side, team in document["teams"].items():
        active = {
            (member["species_id"], member.get("form_id"))
            for member in team.get("active", [])
        }
        bench = {
            (member["species_id"], member.get("form_id"))
            for member in team.get("bench", [])
        }
        if active & bench:
            raise BattleStateError(
                f"teams.{side} cannot list the same Pokemon identity as active and bench"
            )

    previous: tuple[int, int] | None = None
    for index, event in enumerate(document.get("turn_events", [])):
        current = (event["turn"], event["sequence"])
        if previous is not None and current <= previous:
            raise BattleStateError(
                "turn_events must use strictly increasing, unique (turn, sequence) pairs; "
                f"event {index} has {current} after {previous}"
            )
        previous = current

    normalized = copy.deepcopy(document)
    normalized.setdefault("turn_events", [])
    normalized.setdefault("revealed_information", [])
    return normalized


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise BattleStateError(f"invalid JSON: duplicate object key {key!r}")
        result[key] = value
    return result


def _reject_nonfinite_number(value: str) -> None:
    raise BattleStateError(f"invalid JSON: non-finite number {value!r}")


def read_limited_input(path: str) -> bytes:
    try:
        if path == "-":
            payload = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
        else:
            with Path(path).open("rb") as handle:
                payload = handle.read(MAX_INPUT_BYTES + 1)
    except OSError as exc:
        raise BattleStateError(f"could not read input: {exc}") from exc
    if len(payload) > MAX_INPUT_BYTES:
        raise BattleStateError(f"input exceeds {MAX_INPUT_BYTES}-byte limit")
    return payload


def parse_document(payload: bytes) -> Any:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BattleStateError("input must be UTF-8 JSON") from exc
    try:
        return json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonfinite_number,
        )
    except BattleStateError:
        raise
    except json.JSONDecodeError as exc:
        raise BattleStateError(
            f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    except ValueError as exc:
        raise BattleStateError(
            "invalid JSON: numeric value is too large or malformed"
        ) from exc
    except RecursionError as exc:
        raise BattleStateError("invalid JSON: document nesting is too deep") from exc


def render_document(document: dict[str, Any], pretty: bool) -> bytes:
    if pretty:
        rendered = json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False)
    else:
        rendered = json.dumps(
            document,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )
    try:
        return (rendered + "\n").encode("utf-8")
    except UnicodeEncodeError as exc:
        raise BattleStateError(
            "document strings must contain only Unicode scalar values"
        ) from exc


def write_atomic(path: Path, payload: bytes) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            dir=path.parent,
            prefix=f".{path.name}.",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(payload)
        os.replace(temporary, path)
    except OSError as exc:
        if "temporary" in locals():
            temporary.unlink(missing_ok=True)
        raise BattleStateError(f"could not write output: {exc}") from exc


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="JSON input path, or - for stdin")
    parser.add_argument("--output", type=Path, help="write canonical JSON to this explicit path")
    parser.add_argument("--pretty", action="store_true", help="indent canonical JSON")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if (
            args.output is not None
            and args.input != "-"
            and Path(args.input).resolve(strict=False) == args.output.resolve(strict=False)
        ):
            raise BattleStateError("output path must differ from input path")
        document = parse_document(read_limited_input(args.input))
        normalized = validate_and_normalize(document)
        payload = render_document(normalized, args.pretty)
        if args.output:
            write_atomic(args.output, payload)
        else:
            sys.stdout.buffer.write(payload)
    except BattleStateError as exc:
        print(f"battle-state validation failed: {exc}", file=sys.stderr)
        return 2
    except RecursionError:
        print(
            "battle-state validation failed: document nesting is too deep",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
