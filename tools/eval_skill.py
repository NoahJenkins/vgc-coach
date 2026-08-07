#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from autoresearch.config import DEFAULT_REPORT_ROOT, choose_skill, parse_run_date
from autoresearch.standalone import run_standalone_eval


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate one vgc-coach skill against fixed cases.")
    parser.add_argument("--skill", default="auto", help="Skill name or auto")
    parser.add_argument("--date", default=None, help="Run date override in YYYY-MM-DD format")
    parser.add_argument(
        "--provider",
        choices=("github-token", "byok-openai"),
        default="github-token",
        help="Copilot SDK auth/provider mode",
    )
    parser.add_argument("--model", default=None, help="Model override")
    parser.add_argument(
        "--profile",
        choices=("daily_sentinel", "manual"),
        default="manual",
        help="Run profile",
    )
    parser.add_argument(
        "--case-limit",
        type=int,
        default=None,
        help="Limit evals to the first N cases for smoke testing",
    )
    parser.add_argument(
        "--session-timeout",
        type=float,
        default=900.0,
        help="Per-model-call timeout in seconds",
    )
    parser.add_argument(
        "--report-dir",
        default=str(DEFAULT_REPORT_ROOT),
        help="Base report directory",
    )
    return parser.parse_args(argv)


async def main() -> int:
    args = parse_args()
    run_date = parse_run_date(args.date)
    config = choose_skill(args.skill, run_date)
    report_dir = Path(args.report_dir) / run_date.isoformat() / config.name / "standalone-eval"
    result = await run_standalone_eval(
        config=config,
        provider_name=args.provider,
        model=args.model,
        run_profile=args.profile,
        case_limit=args.case_limit,
        session_timeout=args.session_timeout,
        report_dir=report_dir,
    )
    result_path = report_dir / "result.json"
    print(result_path)
    return 0 if result.status == "succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
