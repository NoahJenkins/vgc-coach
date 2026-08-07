from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = REPO_ROOT / "site"


class SiteDeliveryContractTests(unittest.TestCase):
    def test_user_facing_site_copy_avoids_em_and_en_dashes(self):
        rendered_sources = (
            SITE_ROOT / "src/App.tsx",
            SITE_ROOT / "src/siteContent.ts",
            SITE_ROOT / "index.html",
        )

        for path in rendered_sources:
            with self.subTest(path=path.name):
                content = path.read_text()
                self.assertNotIn("—", content)
                self.assertNotIn("–", content)

    def test_section_anchors_clear_the_sticky_header_on_desktop_and_mobile(self):
        css = (SITE_ROOT / "src/styles.css").read_text()

        root_offset = re.search(
            r":root\s*\{.*?--anchor-offset:\s*([^;]+);",
            css,
            flags=re.DOTALL,
        )
        mobile_block = re.search(
            r"@media \(max-width: 760px\)\s*\{(.*?)\n\}",
            css,
            flags=re.DOTALL,
        )
        wrapped_desktop_block = re.search(
            r"@media \(max-width: 1180px\)\s*\{(.*?)\n\}",
            css,
            flags=re.DOTALL,
        )

        self.assertIsNotNone(root_offset)
        self.assertGreaterEqual(float(root_offset.group(1).removesuffix("rem")), 9)
        self.assertIn("scroll-margin-top: var(--anchor-offset)", css)
        self.assertIsNotNone(wrapped_desktop_block)
        self.assertRegex(
            wrapped_desktop_block.group(1), r"--anchor-offset:\s*1[01](?:\.\d+)?rem"
        )
        self.assertIsNotNone(mobile_block)
        mobile_offset = re.search(
            r"--anchor-offset:\s*([\d.]+)rem", mobile_block.group(1)
        )
        self.assertIsNotNone(mobile_offset)
        self.assertGreaterEqual(float(mobile_offset.group(1)), 6)

    def test_fonts_are_local_woff2_assets_with_upstream_licenses(self):
        index = (SITE_ROOT / "index.html").read_text()
        css = (SITE_ROOT / "src/styles.css").read_text()

        self.assertNotIn("fonts.googleapis.com", index + css)
        self.assertNotIn("fonts.gstatic.com", index + css)
        self.assertIn("/fonts/manrope-latin-variable.woff2", index + css)
        self.assertIn("/fonts/sora-latin-variable.woff2", index + css)

        for name in ("manrope-latin-variable.woff2", "sora-latin-variable.woff2"):
            path = SITE_ROOT / "public/fonts" / name
            self.assertTrue(path.is_file(), path)
            self.assertGreater(path.stat().st_size, 1_000)

        for family in ("manrope", "sora"):
            license_path = SITE_ROOT / "public/fonts/licenses" / f"{family}-OFL.txt"
            self.assertIn("SIL OPEN FONT LICENSE Version 1.1", license_path.read_text())

    def test_vercel_headers_cover_all_routes_and_required_boundaries(self):
        config = json.loads((SITE_ROOT / "vercel.json").read_text())
        global_headers = next(
            entry["headers"] for entry in config["headers"] if entry["source"] == "/(.*)"
        )
        headers = {item["key"].lower(): item["value"] for item in global_headers}

        csp = headers["content-security-policy"]
        self.assertIn("default-src 'self'", csp)
        self.assertIn("font-src 'self'", csp)
        self.assertIn("object-src 'none'", csp)
        self.assertIn("base-uri 'self'", csp)
        self.assertIn("frame-ancestors 'none'", csp)
        self.assertEqual(headers["x-content-type-options"], "nosniff")
        self.assertEqual(headers["referrer-policy"], "strict-origin-when-cross-origin")
        self.assertIn("camera=()", headers["permissions-policy"])
        self.assertIn("microphone=()", headers["permissions-policy"])
        self.assertIn("geolocation=()", headers["permissions-policy"])


if __name__ == "__main__":
    unittest.main()
