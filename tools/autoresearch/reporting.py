from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


def current_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def reset_report_dir(report_dir: Path) -> None:
    if report_dir.exists():
        shutil.rmtree(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_summary(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def write_run_status(
    report_dir: Path,
    *,
    kind: str,
    status: str,
    started_at: str,
    finished_at: str | None,
    summary: str,
    errors: Sequence[str],
    result_path: str | None = None,
    summary_path: str | None = None,
) -> Path:
    path = report_dir / "run-status.json"
    payload = {
        "kind": kind,
        "status": status,
        "started_at": started_at,
        "finished_at": finished_at,
        "summary": summary,
        "errors": list(errors),
        "result_path": result_path,
        "summary_path": summary_path,
    }
    write_json(path, payload)
    return path
