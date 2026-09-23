import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "abes_bootstrap.py"


class BootstrapTests(unittest.TestCase):
    def test_bootstrap_creates_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-project"
            target.mkdir()
            (target / "package.json").write_text('{"scripts":{"test":"vitest","lint":"eslint ."}}', encoding="utf-8")
            (target / "packages" / "web" / "src").mkdir(parents=True)
            (target / "services" / "api" / "tests").mkdir(parents=True)
            (target / "README.md").write_text("# Sample Project\n\nA reusable app.\n", encoding="utf-8")

            subprocess.run([sys.executable, str(SCRIPT), str(target)], check=True)

            self.assertTrue((target / "AGENTS.md").exists())
            self.assertTrue((target / ".abes" / "project" / "brief.md").exists())
            self.assertTrue((target / ".abes" / "project" / "inventory.md").exists())
            self.assertTrue((target / ".abes" / "memory" / "decisions.md").exists())

            inventory = (target / ".abes" / "project" / "inventory.md").read_text(encoding="utf-8")
            brief = (target / ".abes" / "project" / "brief.md").read_text(encoding="utf-8")
            self.assertIn("JavaScript/TypeScript", inventory)
            self.assertIn("npm run test", inventory)
            self.assertIn("- packages/web/src", inventory)
            self.assertIn("- services/api/tests", inventory)
            self.assertIn('root README describes "Sample Project" as: A reusable app.', brief)

    def test_bootstrap_preserves_existing_agents_with_managed_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-project"
            target.mkdir()
            (target / "AGENTS.md").write_text("# Existing\n\nKeep this.\n", encoding="utf-8")

            subprocess.run([sys.executable, str(SCRIPT), str(target)], check=True)

            agents = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("<!-- ABES:START -->", agents)
            self.assertIn("# Existing", agents)
            self.assertIn("Keep this.", agents)

    def test_bootstrap_is_idempotent_on_fresh_repository(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-project"
            target.mkdir()
            (target / "packages" / "web" / "src").mkdir(parents=True)
            (target / "services" / "api" / "tests").mkdir(parents=True)

            subprocess.run([sys.executable, str(SCRIPT), str(target)], check=True)
            inventory_before = (target / ".abes" / "project" / "inventory.md").read_text(encoding="utf-8")
            subprocess.run([sys.executable, str(SCRIPT), str(target), "--force"], check=True)

            agents = (target / "AGENTS.md").read_text(encoding="utf-8")
            inventory_after = (target / ".abes" / "project" / "inventory.md").read_text(encoding="utf-8")
            self.assertEqual(agents.count("<!-- ABES:START -->"), 1)
            self.assertEqual(agents.count("<!-- ABES:END -->"), 1)
            self.assertIn("- packages/web/src", inventory_after)
            self.assertIn("- services/api/tests", inventory_after)
            self.assertNotIn(".abes/", inventory_after)
            self.assertNotEqual(inventory_before, "")

    def test_bootstrap_preserves_non_ascii_agents_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-project"
            target.mkdir()
            (target / "AGENTS.md").write_text("# Grüezi\n\nÜber context.\n", encoding="utf-8")

            subprocess.run([sys.executable, str(SCRIPT), str(target)], check=True)

            agents = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("# Grüezi", agents)
            self.assertIn("Über context.", agents)

    def test_force_does_not_overwrite_unmanaged_abes_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-project"
            brief = target / ".abes" / "project" / "brief.md"
            brief.parent.mkdir(parents=True)
            brief.write_text("# Custom brief\n\nDo not overwrite.\n", encoding="utf-8")

            subprocess.run([sys.executable, str(SCRIPT), str(target), "--force"], check=True)

            self.assertEqual(brief.read_text(encoding="utf-8"), "# Custom brief\n\nDo not overwrite.\n")

    def test_force_preserves_unmanaged_agents_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-project"
            target.mkdir()
            (target / "AGENTS.md").write_text("# Existing\n\nDo not lose this.\n", encoding="utf-8")

            subprocess.run([sys.executable, str(SCRIPT), str(target), "--force"], check=True)

            agents = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(agents.count("<!-- ABES:START -->"), 1)
            self.assertIn("# Existing", agents)
            self.assertIn("Do not lose this.", agents)

    def test_pyproject_without_declared_tools_uses_generic_command_hint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-project"
            target.mkdir()
            (target / "pyproject.toml").write_text("[project]\nname='pytest-demo'\nversion='0.1.0'\n", encoding="utf-8")

            subprocess.run([sys.executable, str(SCRIPT), str(target)], check=True)

            inventory = (target / ".abes" / "project" / "inventory.md").read_text(encoding="utf-8")
            self.assertIn("inspect Python project test/lint commands before assuming any", inventory)
            self.assertNotIn("python -m pytest", inventory)
            self.assertNotIn("ruff check .", inventory)

    def test_pyproject_declared_tools_are_detected_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-project"
            target.mkdir()
            (target / "pyproject.toml").write_text(
                "[project]\nname='demo'\nversion='0.1.0'\ndependencies=['pytest>=8']\n\n[tool.ruff]\nline-length=100\n",
                encoding="utf-8",
            )

            subprocess.run([sys.executable, str(SCRIPT), str(target)], check=True)

            inventory = (target / ".abes" / "project" / "inventory.md").read_text(encoding="utf-8")
            self.assertIn("python -m pytest", inventory)
            self.assertIn("ruff check .", inventory)

    def test_makefile_only_suggests_declared_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-project"
            target.mkdir()
            (target / "Makefile").write_text("test:\n\t@echo test\nbuild:\n\t@echo build\n", encoding="utf-8")

            subprocess.run([sys.executable, str(SCRIPT), str(target)], check=True)

            inventory = (target / ".abes" / "project" / "inventory.md").read_text(encoding="utf-8")
            self.assertIn("make test", inventory)
            self.assertIn("make build", inventory)
            self.assertNotIn("make lint", inventory)

    def test_go_and_rust_only_suggest_broadly_available_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-project"
            target.mkdir()
            (target / "go.mod").write_text("module example.com/demo\n\ngo 1.22\n", encoding="utf-8")
            (target / "Cargo.toml").write_text("[package]\nname='demo'\nversion='0.1.0'\n", encoding="utf-8")

            subprocess.run([sys.executable, str(SCRIPT), str(target)], check=True)

            inventory = (target / ".abes" / "project" / "inventory.md").read_text(encoding="utf-8")
            self.assertIn("go test ./...", inventory)
            self.assertIn("cargo test", inventory)
            self.assertNotIn("go vet ./...", inventory)
            self.assertNotIn("cargo clippy", inventory)

    def test_nested_manifest_contributes_to_language_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-project"
            target.mkdir()
            nested_package = target / "packages" / "web"
            nested_package.mkdir(parents=True)
            (nested_package / "package.json").write_text('{"name":"web"}', encoding="utf-8")

            subprocess.run([sys.executable, str(SCRIPT), str(target)], check=True)

            inventory = (target / ".abes" / "project" / "inventory.md").read_text(encoding="utf-8")
            self.assertIn("JavaScript/TypeScript", inventory)
            self.assertIn("- packages/web/package.json", inventory)

    def test_generated_and_vendor_trees_are_pruned(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-project"
            target.mkdir()
            (target / "src").mkdir()
            (target / "node_modules" / "left-pad").mkdir(parents=True)
            (target / "dist" / "generated").mkdir(parents=True)
            (target / "node_modules" / "left-pad" / "package.json").write_text('{"name":"left-pad"}', encoding="utf-8")
            (target / "dist" / "generated" / "README.md").write_text("# Built output\n", encoding="utf-8")

            subprocess.run([sys.executable, str(SCRIPT), str(target)], check=True)

            inventory = (target / ".abes" / "project" / "inventory.md").read_text(encoding="utf-8")
            self.assertIn("- src", inventory)
            self.assertNotIn("node_modules/left-pad/package.json", inventory)
            self.assertNotIn("dist/generated/README.md", inventory)

    def test_non_object_package_json_does_not_crash_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-project"
            target.mkdir()
            (target / "package.json").write_text("null", encoding="utf-8")

            subprocess.run([sys.executable, str(SCRIPT), str(target)], check=True)

            inventory = (target / ".abes" / "project" / "inventory.md").read_text(encoding="utf-8")
            self.assertIn("- package.json", inventory)
            self.assertNotIn("npm run test", inventory)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are not supported on this platform")
    def test_symlinked_output_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-project"
            outside = Path(tmp) / "outside.md"
            target.mkdir()
            outside.write_text("outside\n", encoding="utf-8")
            project_dir = target / ".abes" / "project"
            project_dir.mkdir(parents=True)
            os.symlink(outside, project_dir / "brief.md")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(target), "--force"],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("refusing to overwrite symlinked file", result.stderr)
            self.assertEqual(outside.read_text(encoding="utf-8"), "outside\n")

    def test_legacy_managed_files_are_removed_and_unmanaged_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-project"
            legacy_managed = target / ".abes" / "project" / "identity.md"
            legacy_unmanaged = target / ".abes" / "project" / "goals.md"
            legacy_managed.parent.mkdir(parents=True)
            legacy_managed.write_text("<!-- ABES:MANAGED -->\n# Identity\n", encoding="utf-8")
            legacy_unmanaged.write_text("# Goals\n\nKeep this.\n", encoding="utf-8")

            subprocess.run([sys.executable, str(SCRIPT), str(target)], check=True)

            self.assertFalse(legacy_managed.exists())
            self.assertEqual(legacy_unmanaged.read_text(encoding="utf-8"), "# Goals\n\nKeep this.\n")

    def test_target_path_file_is_rejected_with_clean_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target_file = Path(tmp) / "not-a-directory"
            target_file.write_text("content\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(target_file)],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Target path is not a directory", result.stderr)
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
