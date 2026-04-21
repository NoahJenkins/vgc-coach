#!/usr/bin/env python3
"""Install the generated Codex plugin into the user's local plugin marketplace."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAME = "vgc-coach-codex"
SOURCE_PLUGIN = ROOT / "plugins" / PLUGIN_NAME


def install_plugin(home: Path) -> Path:
    if not SOURCE_PLUGIN.exists():
        raise FileNotFoundError(
            f"Build the plugin first with `python3 tools/build_plugins.py build`: {SOURCE_PLUGIN} is missing."
        )

    destination = home / "plugins" / PLUGIN_NAME
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(SOURCE_PLUGIN, destination)

    marketplace_path = home / ".agents" / "plugins" / "marketplace.json"
    marketplace_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "name": "vgc-coach",
        "interface": {
            "displayName": "VGC Coach"
        },
        "plugins": [
            {
                "name": PLUGIN_NAME,
                "source": {
                    "source": "local",
                    "path": f"./plugins/{PLUGIN_NAME}"
                },
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL"
                },
                "category": "Productivity"
            }
        ]
    }
    marketplace_path.write_text(json.dumps(payload, indent=2) + "\n")
    return destination


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--home", type=Path, default=Path.home())
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    destination = install_plugin(args.home)
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
