#!/usr/bin/env python3
"""Fail when the built site's gzip-compressed JS or CSS exceeds its budget."""

from __future__ import annotations

import gzip
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = Path("site/dist/assets")

# gzip level 9 bytes, summed across every emitted asset of the type.
# Raise a budget only on purpose, in the same change that explains the growth.
BUNDLE_BUDGETS_BYTES = {
    ".js": 84_000,
    ".css": 9_000,
}


def measure_gzip_sizes(assets_dir: Path) -> dict[str, int]:
    sizes = {suffix: 0 for suffix in BUNDLE_BUDGETS_BYTES}
    for path in sorted(assets_dir.iterdir()):
        if path.is_file() and path.suffix in sizes:
            sizes[path.suffix] += len(gzip.compress(path.read_bytes(), compresslevel=9))
    return sizes


def find_budget_overruns(
    sizes: dict[str, int],
    budgets: dict[str, int] = BUNDLE_BUDGETS_BYTES,
) -> tuple[str, ...]:
    return tuple(
        f"{suffix} assets are {sizes[suffix]:,} gzip bytes; budget is {budget:,}"
        for suffix, budget in budgets.items()
        if sizes.get(suffix, 0) > budget
    )


def main(repo_root: Path = REPO_ROOT) -> int:
    assets_dir = repo_root / ASSETS_DIR
    if not assets_dir.is_dir():
        print(f"Site bundle check needs a production build at {ASSETS_DIR.as_posix()}.")
        return 2
    sizes = measure_gzip_sizes(assets_dir)
    if sizes[".js"] == 0:
        print(f"Site bundle check found no JavaScript assets in {ASSETS_DIR.as_posix()}.")
        return 2
    for suffix, budget in BUNDLE_BUDGETS_BYTES.items():
        print(f"{suffix}: {sizes[suffix]:,} / {budget:,} gzip bytes")
    overruns = find_budget_overruns(sizes)
    if not overruns:
        return 0
    print("Site bundle exceeds its budget:")
    for item in overruns:
        print(f"- {item}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
