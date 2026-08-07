import copy
import importlib.util
import pathlib
import sys
import tempfile
import unittest
from unittest import mock


MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "tools" / "build_plugins.py"


def load_module():
    spec = importlib.util.spec_from_file_location("build_plugins", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class BuildPluginsTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def minimal_manifest(self, shared_copy):
        return {
            "repository": {
                "homepage": "https://example.test",
                "repository": "https://example.test/repo",
                "license": "Apache-2.0",
                "author": {"name": "Test", "url": "https://example.test"},
            },
            "skills": [],
            "shared_copy": shared_copy,
            "plugins": [
                {
                    "name": "test-plugin",
                    "runtime": "opencode",
                    "manifest_path": "package.json",
                    "description": "Test plugin",
                    "keywords": [],
                    "runtime_docs": [],
                }
            ],
        }

    def test_build_creates_expected_runtime_manifests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            self.module.build_all(root)

            self.assertTrue((root / "plugins" / "vgc-coach-codex" / ".codex-plugin" / "plugin.json").exists())
            self.assertTrue((root / "plugins" / "vgc-coach-claude" / ".claude-plugin" / "plugin.json").exists())
            self.assertTrue((root / "plugins" / "vgc-coach-opencode" / "package.json").exists())
            self.assertTrue((root / ".agents" / "plugins" / "marketplace.json").exists())
            self.assertTrue((root / ".claude-plugin" / "marketplace.json").exists())
            self.assertTrue((root / "package.json").exists())

    def test_build_copies_docs_and_tools_into_plugin(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            self.module.build_all(root)

            plugin_root = root / "plugins" / "vgc-coach-opencode"
            self.assertTrue((plugin_root / "docs" / "skills" / "vgc-team-builder" / "references" / "build-principles.md").exists())
            self.assertTrue((plugin_root / "docs" / "skills" / "shared" / "references" / "live-source-registry.yaml").exists())
            self.assertTrue((plugin_root / "docs" / "skills" / "shared" / "references" / "live-source-map.md").exists())
            self.assertTrue((plugin_root / "tools" / "browser_damage_calc.py").exists())
            self.assertTrue((plugin_root / "skills" / "vgc-team-builder" / "agents" / "openai.yaml").exists())

    def test_validation_rejects_workspace_only_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            plugin_root = root / "plugins" / "vgc-coach-codex"
            plugin_root.mkdir(parents=True, exist_ok=True)
            bad_file = plugin_root / "README.md"
            bad_file.write_text("See .agents/skills/foo for source")

            issues = self.module.validate_generated_outputs(root)

            self.assertEqual(len(issues), 1)
            self.assertIn(".agents/skills/", issues[0])

    def test_codex_installer_copies_plugin_and_marketplace(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            self.module.build_all(root)

            installer_path = pathlib.Path(__file__).resolve().parents[1] / "tools" / "install_codex_plugin.py"
            spec = importlib.util.spec_from_file_location("install_codex_plugin", installer_path)
            installer = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = installer
            spec.loader.exec_module(installer)

            original_source = installer.SOURCE_PLUGIN
            installer.SOURCE_PLUGIN = root / "plugins" / "vgc-coach-codex"
            try:
                destination = installer.install_plugin(root / "home")
            finally:
                installer.SOURCE_PLUGIN = original_source

            self.assertTrue((destination / ".codex-plugin" / "plugin.json").exists())
            marketplace = root / "home" / ".agents" / "plugins" / "marketplace.json"
            self.assertTrue(marketplace.exists())
            self.assertIn("./plugins/vgc-coach-codex", marketplace.read_text())

    def test_runtime_docs_reference_packaged_installs(self):
        repo_root = pathlib.Path(__file__).resolve().parents[1]
        codex_doc = (repo_root / "docs" / "runtime" / "codex.md").read_text()
        claude_doc = (repo_root / "docs" / "runtime" / "claude-code.md").read_text()
        opencode_doc = (repo_root / "docs" / "runtime" / "opencode.md").read_text()

        self.assertIn("python3 tools/install_codex_plugin.py", codex_doc)
        self.assertIn("claude plugin install vgc-coach-claude@vgc-coach", claude_doc)
        self.assertIn("vgc-coach-opencode@git+https://github.com/NoahJenkins/vgc-coach.git", opencode_doc)

    def test_release_notes_match_generated_version_section(self):
        manifest = self.module.load_manifest()
        version = self.module.load_version()
        expected = self.module.render_release_notes(manifest, version)
        actual = (pathlib.Path(__file__).resolve().parents[1] / "RELEASE_NOTES.md").read_text()

        self.assertEqual(actual, expected)

    def test_manifest_rejects_every_path_bearing_field_before_build_reads_sources(self):
        cases = [
            (("skills", 0, "name"), "../escape"),
            (("skills", 0, "codex_metadata"), "../escape"),
            (("skills", 0, "docs", 0), "../escape"),
            (("shared_copy", "files", 0), "../escape"),
            (("shared_copy", "directories", 0), "../escape"),
            (("shared_copy", "tools", 0), "../escape"),
            (("plugins", 0, "name"), "../escape"),
            (("plugins", 0, "manifest_path"), "../escape"),
            (("plugins", 0, "runtime_docs", 0), "../escape"),
        ]
        original = self.module.load_manifest()

        for field_path, bad_value in cases:
            with self.subTest(field_path=field_path):
                manifest = copy.deepcopy(original)
                target = manifest
                for component in field_path[:-1]:
                    target = target[component]
                target[field_path[-1]] = bad_value

                with tempfile.TemporaryDirectory() as tmp:
                    build_root = pathlib.Path(tmp) / "build"
                    with mock.patch.object(
                        self.module, "load_manifest", return_value=manifest
                    ), mock.patch.object(self.module, "load_version") as load_version:
                        with self.assertRaisesRegex(ValueError, "repository-relative POSIX path"):
                            self.module.build_all(build_root)
                        load_version.assert_not_called()
                    self.assertFalse(build_root.exists())

    def test_manifest_rejects_non_normalized_or_unsafe_posix_paths(self):
        invalid_paths = [
            "",
            ".",
            "/absolute",
            "double//component",
            "dot/./component",
            "parent/../component",
            "windows\\component",
            "control/\x01component",
        ]
        original = self.module.load_manifest()

        for bad_path in invalid_paths:
            with self.subTest(path=repr(bad_path)):
                manifest = copy.deepcopy(original)
                manifest["plugins"][0]["name"] = bad_path
                with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
                    self.module, "load_manifest", return_value=manifest
                ), mock.patch.object(self.module, "load_version") as load_version:
                    with self.assertRaisesRegex(ValueError, "repository-relative POSIX path"):
                        self.module.build_all(pathlib.Path(tmp) / "build")
                    load_version.assert_not_called()

    def test_destination_symlink_escape_is_rejected_before_recursive_delete(self):
        manifest = copy.deepcopy(self.module.load_manifest())
        manifest["plugins"] = [manifest["plugins"][2]]

        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            self.module, "load_manifest", return_value=manifest
        ):
            disposable_root = pathlib.Path(tmp)
            build_root = disposable_root / "build"
            outside_root = disposable_root / "outside"
            escaped_plugin = outside_root / "vgc-coach-opencode"
            escaped_plugin.mkdir(parents=True)
            sentinel = escaped_plugin / "sentinel.txt"
            sentinel.write_bytes(b"must survive")
            build_root.mkdir()
            (build_root / "plugins").symlink_to(outside_root, target_is_directory=True)

            with self.assertRaisesRegex(ValueError, "outside intended root"):
                self.module.build_all(build_root)

            self.assertEqual(sentinel.read_bytes(), b"must survive")

    def test_canonical_file_symlink_is_rejected_without_reading_target(self):
        manifest = self.minimal_manifest(
            {"files": ["linked.txt"], "directories": [], "tools": []}
        )
        outside_bytes = b"outside canonical source"

        with tempfile.TemporaryDirectory() as tmp:
            disposable_root = pathlib.Path(tmp)
            source_root = disposable_root / "source"
            source_root.mkdir()
            outside = disposable_root / "outside.txt"
            outside.write_bytes(outside_bytes)
            linked_source = source_root / "linked.txt"
            linked_source.symlink_to(outside)
            with mock.patch.object(self.module, "ROOT", source_root), mock.patch.object(
                self.module, "load_manifest", return_value=manifest
            ), mock.patch.object(
                self.module, "load_version", return_value="test"
            ) as load_version:
                with self.assertRaisesRegex(ValueError, "Source symlink not allowed"):
                    self.module.build_all(disposable_root / "build")
                load_version.assert_not_called()

            self.assertEqual(outside.read_bytes(), outside_bytes)
            self.assertFalse((disposable_root / "build").exists())

    def test_canonical_directory_symlink_is_rejected_without_walking_target(self):
        manifest = self.minimal_manifest(
            {"files": [], "directories": ["linked-dir"], "tools": []}
        )

        with tempfile.TemporaryDirectory() as tmp:
            disposable_root = pathlib.Path(tmp)
            source_root = disposable_root / "source"
            source_root.mkdir()
            outside_dir = disposable_root / "outside"
            outside_dir.mkdir()
            sentinel = outside_dir / "sentinel.txt"
            sentinel.write_bytes(b"must survive")
            (source_root / "linked-dir").symlink_to(outside_dir, target_is_directory=True)
            with mock.patch.object(self.module, "ROOT", source_root), mock.patch.object(
                self.module, "load_manifest", return_value=manifest
            ), mock.patch.object(
                self.module, "load_version", return_value="test"
            ) as load_version:
                with self.assertRaisesRegex(ValueError, "Source symlink not allowed"):
                    self.module.build_all(disposable_root / "build")
                load_version.assert_not_called()

            self.assertEqual(sentinel.read_bytes(), b"must survive")
            self.assertFalse((disposable_root / "build").exists())

    def test_disposable_build_remains_byte_identical_to_checked_in_plugins(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            self.module.build_all(root)

            differences = self.module.compare_directories(
                root / "plugins",
                pathlib.Path(__file__).resolve().parents[1] / "plugins",
            )

            self.assertEqual(differences, [])


if __name__ == "__main__":
    unittest.main()
