import importlib.util
import pathlib
import sys
import tempfile
import unittest


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


if __name__ == "__main__":
    unittest.main()
