#!/usr/bin/env python3
"""Browser-assisted exact damage calc wrapper for vgc-coach.

This module keeps the request/result contract backend-agnostic while using
Pikalytics plus `agent-browser` as the first exact backend.
"""

from __future__ import annotations

import argparse
import base64
import dataclasses
from dataclasses import dataclass, field as dc_field
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Callable
from urllib.parse import parse_qs, quote, urlparse


DEFAULT_RULESET = "champions"
DEFAULT_FORMAT = "Doubles"
DEFAULT_TERRAIN = "None"
DEFAULT_WEATHER = "None"
SUPPORTED_EXACT_TYPES = {"damage", "ko", "survival"}
STAT_ORDER = ("hp", "at", "df", "sa", "sd", "sp")
IV_STAT_ORDER = ("hp", "atk", "def", "spa", "spd", "spe")


class BrowserCalcError(RuntimeError):
    """Raised when browser-backed exact execution fails."""


@dataclass
class CalcSide:
    species: str
    level: int = 50
    ability: str = ""
    item: str = ""
    nature: str = "Hardy"
    evs: dict[str, int] = dc_field(default_factory=dict)
    ivs: dict[str, int] = dc_field(default_factory=dict)
    moves: list[str] = dc_field(default_factory=list)
    boosts: dict[str, int] = dc_field(default_factory=dict)
    current_hp_percent: int | None = None
    status: str = "Healthy"
    tera_type: str = ""
    terastallized: bool = False

    def normalized_evs(self) -> dict[str, int]:
        return {key: int(self.evs.get(key, 0)) for key in STAT_ORDER}

    def normalized_ivs(self) -> dict[str, int]:
        incoming = self.ivs or {}
        return {
            "hp": int(incoming.get("hp", 31)),
            "atk": int(incoming.get("atk", incoming.get("at", 31))),
            "def": int(incoming.get("def", incoming.get("df", 31))),
            "spa": int(incoming.get("spa", incoming.get("sa", 31))),
            "spd": int(incoming.get("spd", incoming.get("sd", 31))),
            "spe": int(incoming.get("spe", incoming.get("sp", 31))),
        }

    def normalized_boosts(self) -> dict[str, int]:
        return {
            "atk": int(self.boosts.get("atk", self.boosts.get("at", 0))),
            "def": int(self.boosts.get("def", self.boosts.get("df", 0))),
            "spa": int(self.boosts.get("spa", self.boosts.get("sa", 0))),
            "spd": int(self.boosts.get("spd", self.boosts.get("sd", 0))),
        }


@dataclass
class FieldState:
    format: str = DEFAULT_FORMAT
    weather: str = DEFAULT_WEATHER
    terrain: str = DEFAULT_TERRAIN


@dataclass
class CalcRequest:
    goal: str
    calc_type: str
    move: str
    attacker: CalcSide
    defender: CalcSide
    field: FieldState = dc_field(default_factory=FieldState)
    notes: list[str] = dc_field(default_factory=list)
    ruleset: str = DEFAULT_RULESET


@dataclass
class CalcResult:
    status: str
    backend: str
    site: str | None
    numeric_result: dict[str, Any] | None
    assumptions_used: dict[str, Any]
    retrieval_timestamp: str
    failure_reason: str | None

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def _normalize_calc_type(raw: str | None) -> str:
    value = (raw or "").strip().lower()
    if value in {"damage", "ko", "survival", "speed"}:
        return value
    return "damage"


def _normalize_evs(raw: dict[str, Any] | None) -> dict[str, int]:
    if not raw:
        return {}
    normalized = {}
    for key in STAT_ORDER:
        normalized[key] = int(raw.get(key, 0))
    return normalized


def _normalize_ivs(raw: dict[str, Any] | None) -> dict[str, int]:
    if not raw:
        return {}
    return {
        "hp": int(raw.get("hp", 31)),
        "atk": int(raw.get("atk", raw.get("at", 31))),
        "def": int(raw.get("def", raw.get("df", 31))),
        "spa": int(raw.get("spa", raw.get("sa", 31))),
        "spd": int(raw.get("spd", raw.get("sd", 31))),
        "spe": int(raw.get("spe", raw.get("sp", 31))),
    }


def parse_side(payload: dict[str, Any], *, default_moves: list[str] | None = None) -> CalcSide:
    return CalcSide(
        species=(payload.get("species") or "").strip(),
        level=int(payload.get("level", 50)),
        ability=(payload.get("ability") or "").strip(),
        item=(payload.get("item") or "").strip(),
        nature=(payload.get("nature") or "Hardy").strip(),
        evs=_normalize_evs(payload.get("evs")),
        ivs=_normalize_ivs(payload.get("ivs")),
        moves=[move for move in payload.get("moves", default_moves or []) if move],
        boosts=payload.get("boosts", {}) or {},
        current_hp_percent=payload.get("current_hp_percent"),
        status=(payload.get("status") or "Healthy").strip(),
        tera_type=(payload.get("tera_type") or "").strip(),
        terastallized=bool(payload.get("terastallized", False)),
    )


def parse_request(payload: dict[str, Any]) -> CalcRequest:
    move = (payload.get("move") or "").strip()
    attacker_default_moves = [move] if move else []
    return CalcRequest(
        goal=(payload.get("goal") or "").strip(),
        calc_type=_normalize_calc_type(payload.get("calc_type")),
        move=move,
        attacker=parse_side(payload.get("attacker", {}), default_moves=attacker_default_moves),
        defender=parse_side(payload.get("defender", {}), default_moves=["Protect"]),
        field=FieldState(
            format=(payload.get("field", {}).get("format") or DEFAULT_FORMAT).strip(),
            weather=(payload.get("field", {}).get("weather") or DEFAULT_WEATHER).strip(),
            terrain=(payload.get("field", {}).get("terrain") or DEFAULT_TERRAIN).strip(),
        ),
        notes=list(payload.get("notes", []) or []),
        ruleset=(payload.get("ruleset") or DEFAULT_RULESET).strip(),
    )


def is_exact_eligible(request: CalcRequest) -> bool:
    return not validation_errors(request)


def validation_errors(request: CalcRequest) -> list[str]:
    errors = []
    if request.calc_type not in SUPPORTED_EXACT_TYPES:
        errors.append("Only damage, ko, and survival requests are eligible for exact browser execution.")
    if not request.move:
        errors.append("A move is required for exact browser execution.")
    if not request.attacker.species or not request.defender.species:
        errors.append("Both attacker and defender species are required for exact browser execution.")

    if request.ruleset == "champions":
        for label, side in (("attacker", request.attacker), ("defender", request.defender)):
            ev_total = sum(side.normalized_evs().values())
            if ev_total > 66:
                errors.append(f"The {label} stat-point total exceeds the Champions cap of 66.")
            per_stat_over = [stat for stat, value in side.normalized_evs().items() if value > 32]
            if per_stat_over:
                errors.append(f"The {label} has Champions stat points above 32 in: {', '.join(per_stat_over)}.")
    return errors


def _encode_set_payload(species: str, ruleset: str, side: CalcSide) -> str:
    moves = list(side.moves[:4])
    while len(moves) < 4:
        moves.append("Protect")
    payload = {
        "name": species,
        "ruleset": ruleset,
        "set": {
            "ability": side.ability,
            "evs": side.normalized_evs(),
            "item": side.item,
            "level": side.level,
            "moves": moves,
            "ivs": side.normalized_ivs(),
            "nature": side.nature,
        },
    }
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(raw).decode("ascii")


def build_calc_url(request: CalcRequest) -> str:
    att_set = _encode_set_payload(request.attacker.species, request.ruleset, request.attacker)
    def_set = _encode_set_payload(request.defender.species, request.ruleset, request.defender)
    return f"https://www.pikalytics.com/calc?attSet={quote(att_set)}&defSet={quote(def_set)}"


def decode_calc_url(url: str) -> dict[str, Any]:
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    output = {}
    for key in ("attSet", "defSet"):
        raw = qs[key][0]
        padding = "=" * (-len(raw) % 4)
        output[key] = json.loads(base64.b64decode(raw + padding))
    return output


def blocked_result(request: CalcRequest, reason: str) -> CalcResult:
    return CalcResult(
        status="blocked",
        backend="agent-browser",
        site="pikalytics",
        numeric_result=None,
        assumptions_used=request_summary(request),
        retrieval_timestamp=timestamp_now(),
        failure_reason=reason,
    )


def fallback_result(request: CalcRequest, reason: str) -> CalcResult:
    return CalcResult(
        status="fallback",
        backend="agent-browser",
        site="pikalytics",
        numeric_result=None,
        assumptions_used=request_summary(request),
        retrieval_timestamp=timestamp_now(),
        failure_reason=reason,
    )


def request_summary(request: CalcRequest) -> dict[str, Any]:
    return {
        "calc_type": request.calc_type,
        "goal": request.goal,
        "move": request.move,
        "attacker": {
            "species": request.attacker.species,
            "level": request.attacker.level,
            "ability": request.attacker.ability,
            "item": request.attacker.item,
            "nature": request.attacker.nature,
            "evs": request.attacker.normalized_evs(),
        },
        "defender": {
            "species": request.defender.species,
            "level": request.defender.level,
            "ability": request.defender.ability,
            "item": request.defender.item,
            "nature": request.defender.nature,
            "evs": request.defender.normalized_evs(),
        },
        "field": dataclasses.asdict(request.field),
        "ruleset": request.ruleset,
    }


def timestamp_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def execute_exact_calc(
    request: CalcRequest,
    *,
    runner: Callable[[CalcRequest], CalcResult] | None = None,
) -> CalcResult:
    errors = validation_errors(request)
    if errors:
        return blocked_result(request, " ".join(errors))

    runner = runner or run_agent_browser_backend
    try:
        return runner(request)
    except BrowserCalcError as exc:
        return fallback_result(request, str(exc))


def run_from_payload(
    payload: dict[str, Any],
    *,
    runner: Callable[[CalcRequest], CalcResult] | None = None,
) -> dict[str, Any]:
    request = parse_request(payload)
    result = execute_exact_calc(request, runner=runner)
    return result.to_dict()


def _run_agent_browser_command(args: list[str], *, stdin: str | None = None) -> str:
    if not shutil.which("agent-browser"):
        raise BrowserCalcError("agent-browser is not installed on this machine")

    result = subprocess.run(
        ["agent-browser", *args],
        input=stdin,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "agent-browser command failed"
        raise BrowserCalcError(detail)
    return result.stdout.strip()


def _build_apply_script(request: CalcRequest) -> str:
    payload = {
        "format": request.field.format,
        "weather": request.field.weather,
        "terrain": request.field.terrain,
        "attacker": {
            "boosts": request.attacker.normalized_boosts(),
            "current_hp_percent": request.attacker.current_hp_percent,
            "status": request.attacker.status,
            "tera_type": request.attacker.tera_type,
            "terastallized": request.attacker.terastallized,
        },
        "defender": {
            "boosts": request.defender.normalized_boosts(),
            "current_hp_percent": request.defender.current_hp_percent,
            "status": request.defender.status,
            "tera_type": request.defender.tera_type,
            "terastallized": request.defender.terastallized,
        },
    }
    js_payload = json.dumps(payload)
    return f"""
(() => {{
  const payload = {js_payload};
  function dispatch(el) {{
    el.dispatchEvent(new Event('input', {{ bubbles: true }}));
    el.dispatchEvent(new Event('change', {{ bubbles: true }}));
  }}
  function clickRadio(name, value) {{
    const radio = Array.from(document.querySelectorAll('input[type="radio"]')).find((el) => el.value === value && !el.closest('.panel.poke-info') && (!name || el.name === name || el.className.includes(name)));
    if (radio) {{
      radio.click();
      dispatch(radio);
    }}
  }}
  function setPanel(panelIndex, side) {{
    const panel = document.querySelectorAll('.panel.poke-info')[panelIndex];
    if (!panel) return;
    const boosts = Array.from(panel.querySelectorAll('select.boost'));
    const mapping = [side.boosts.atk, side.boosts.def, side.boosts.spa, side.boosts.spd];
    mapping.forEach((value, idx) => {{
      if (boosts[idx] && Number.isFinite(value)) {{
        boosts[idx].value = String(value);
        dispatch(boosts[idx]);
      }}
    }});
    const hpPercent = panel.querySelector('input.percent-hp');
    if (hpPercent && side.current_hp_percent !== null && side.current_hp_percent !== undefined) {{
      hpPercent.value = String(side.current_hp_percent);
      dispatch(hpPercent);
    }}
    const status = panel.querySelector('select.status');
    if (status && side.status) {{
      status.value = side.status;
      dispatch(status);
    }}
    const teraType = panel.querySelector('select.teraType');
    const teraToggle = panel.querySelector('input.teraToggle');
    if (teraType && side.tera_type) {{
      teraType.value = side.tera_type;
      dispatch(teraType);
    }}
    if (teraToggle) {{
      const shouldBeChecked = Boolean(side.terastallized);
      if (teraToggle.checked !== shouldBeChecked) teraToggle.click();
      dispatch(teraToggle);
    }}
  }}
  clickRadio('calc-trigger', payload.format === 'Singles' ? 'Singles' : 'Doubles');
  clickRadio('calc-trigger', payload.weather === 'None' ? '' : payload.weather);
  clickRadio('terrain-trigger', payload.terrain === 'None' ? '' : payload.terrain);
  setPanel(0, payload.attacker);
  setPanel(1, payload.defender);
  return JSON.stringify({{ ok: true }});
}})()
""".strip()


EXTRACT_SCRIPT = r"""
(() => {
  const group = document.querySelector('.main-result-group');
  if (!group) return JSON.stringify({ error: 'main-result-group not found' });
  const summary = group.textContent.replace(/\s+/g, ' ').trim();
  return JSON.stringify({ summary });
})()
""".strip()


def run_agent_browser_backend(request: CalcRequest) -> CalcResult:
    url = build_calc_url(request)
    try:
        _run_agent_browser_command(["open", url])
        _run_agent_browser_command(["wait", "--load", "networkidle"])
        _run_agent_browser_command(["eval", "--stdin"], stdin=_build_apply_script(request))
        _run_agent_browser_command(["wait", "800"])
        extracted = _run_agent_browser_command(["eval", "--stdin"], stdin=EXTRACT_SCRIPT)
    finally:
        try:
            _run_agent_browser_command(["close"])
        except BrowserCalcError:
            pass

    try:
        parsed = json.loads(extracted)
        if isinstance(parsed, str):
            parsed = json.loads(parsed)
    except json.JSONDecodeError as exc:
        raise BrowserCalcError(f"Could not parse extracted calc result: {exc}") from exc

    if parsed.get("error"):
        raise BrowserCalcError(parsed["error"])

    summary = parsed.get("summary", "")
    match = re.search(r"Damage:\s*(.*?)\s*Chance to KO:\s*(.*)$", summary)
    if match:
        parsed["damage"] = match.group(1).strip()
        parsed["ko_chance"] = match.group(2).strip()
    else:
        parsed["damage"] = None
        parsed["ko_chance"] = None

    assumptions = request_summary(request)
    assumptions["calc_url"] = url

    return CalcResult(
        status="exact",
        backend="agent-browser",
        site="pikalytics",
        numeric_result=parsed,
        assumptions_used=assumptions,
        retrieval_timestamp=timestamp_now(),
        failure_reason=None,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run an exact browser-backed damage calc.")
    parser.add_argument("--request-file", help="Path to a JSON CalcRequest payload.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print the JSON result.")
    args = parser.parse_args(argv)

    if args.request_file:
        with open(args.request_file, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    else:
        payload = json.load(sys.stdin)

    result = run_from_payload(payload)
    if args.pretty:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(json.dumps(result, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
