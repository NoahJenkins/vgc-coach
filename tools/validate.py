#!/usr/bin/env python3
"""Run the repository's supported validation scopes."""

from __future__ import annotations

import argparse
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ValidationStep:
    name: str
    argv: tuple[str, ...]


def build_validation_steps(
    scope: str,
    *,
    python_executable: str = sys.executable,
    pnpm_executable: str = "pnpm",
) -> tuple[ValidationStep, ...]:
    core_steps = (
        ValidationStep(
            "Python tests",
            (
                python_executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                "tests",
                "-p",
                "test_*.py",
            ),
        ),
        ValidationStep(
            "source-registry render check",
            (python_executable, "tools/render_source_registry_docs.py", "check"),
        ),
        ValidationStep(
            "current-format freshness check",
            (python_executable, "tools/check_format_freshness.py"),
        ),
        ValidationStep(
            "generated-plugin drift check",
            (python_executable, "tools/build_plugins.py", "check"),
        ),
    )
    site_steps = (
        ValidationStep(
            "production site build",
            (pnpm_executable, "--dir", "site", "run", "build"),
        ),
    )
    if scope == "core":
        return core_steps
    if scope == "site":
        return site_steps
    if scope == "all":
        return (*core_steps, *site_steps)
    raise ValueError(f"Unsupported validation scope: {scope}")


def run_validation_steps(
    steps: Iterable[ValidationStep],
    *,
    repo_root: Path = REPO_ROOT,
) -> int:
    selected_steps = tuple(steps)
    for step in selected_steps:
        executable = step.argv[0]
        if shutil.which(executable) is None:
            print(
                f"Missing prerequisite for {step.name}: executable {executable!r} "
                "was not found on PATH.",
                file=sys.stderr,
            )
            return 2

    for step in selected_steps:
        print(f"==> {step.name}", flush=True)
        print(f"$ {shlex.join(step.argv)}", flush=True)
        try:
            completed = subprocess.run(step.argv, cwd=repo_root, check=False)
        except OSError as exc:
            print(
                f"Could not run validation step {step.name}: {exc}",
                file=sys.stderr,
            )
            return 2
        if completed.returncode != 0:
            print(
                f"Validation step {step.name} failed with exit code "
                f"{completed.returncode}: {shlex.join(step.argv)}",
                file=sys.stderr,
            )
            return completed.returncode if completed.returncode > 0 else 1
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scope",
        choices=("all", "core", "site"),
        default="all",
        help="Validation scope to run (default: all).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return run_validation_steps(build_validation_steps(args.scope))


if __name__ == "__main__":
    raise SystemExit(main())
