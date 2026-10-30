from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "tools" / "check_site_bundle.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_site_bundle", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_assets(root: Path, files: dict[str, bytes]) -> None:
    assets = root / "site/dist/assets"
    assets.mkdir(parents=True)
    for name, payload in files.items():
        (assets / name).write_bytes(payload)


class SiteBundleBudgetTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_sizes_sum_gzip_bytes_per_asset_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_assets(
                root,
                {
                    "a.js": b"a" * 1000,
                    "b.js": b"b" * 1000,
                    "c.css": b"c" * 1000,
                    "font.woff2": b"\x00" * 50_000,
                },
            )

            sizes = self.module.measure_gzip_sizes(root / "site/dist/assets")

        self.assertGreater(sizes[".js"], 0)
        self.assertGreater(sizes[".css"], 0)
        self.assertLess(sizes[".js"], 200)
        self.assertEqual(set(sizes), {".js", ".css"})

    def test_overruns_report_only_types_over_budget(self):
        overruns = self.module.find_budget_overruns(
            {".js": 101, ".css": 100},
            {".js": 100, ".css": 100},
        )

        self.assertEqual(len(overruns), 1)
        self.assertIn(".js assets are 101 gzip bytes; budget is 100", overruns[0])

    def test_main_fails_closed_without_a_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stdout(io.StringIO()) as output:
                exit_code = self.module.main(Path(tmp))

        self.assertEqual(exit_code, 2)
        self.assertIn("needs a production build", output.getvalue())

    def test_main_fails_when_bundle_exceeds_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_assets(root, {"index.js": bytes(range(256)) * 2000})
            original = dict(self.module.BUNDLE_BUDGETS_BYTES)
            self.module.BUNDLE_BUDGETS_BYTES.update({".js": 10, ".css": 10})
            try:
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    exit_code = self.module.main(root)
            finally:
                self.module.BUNDLE_BUDGETS_BYTES.clear()
                self.module.BUNDLE_BUDGETS_BYTES.update(original)

        self.assertEqual(exit_code, 1)
        self.assertIn("Site bundle exceeds its budget", output.getvalue())


if __name__ == "__main__":
    unittest.main()
