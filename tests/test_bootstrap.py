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
            (target / "package.json").write_text('{"scripts":{"test":"vitest","lint":"eslint ."}}')
            (target / "packages" / "web" / "src").mkdir(parents=True)
            (target / "services" / "api" / "tests").mkdir(parents=True)
            subprocess.run([sys.executable, str(SCRIPT), str(target)], check=True)

            self.assertTrue((target / "AGENTS.md").exists())
            self.assertTrue((target / ".abes" / "project" / "identity.md").exists())
            self.assertTrue((target / ".abes" / "memory" / "opportunities.md").exists())

            identity = (target / ".abes" / "project" / "identity.md").read_text()
            self.assertIn("JavaScript/TypeScript", identity)
            self.assertIn("npm run test", identity)
            self.assertIn("- packages/web/src", identity)
            self.assertIn("- services/api/tests", identity)

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

            subprocess.run([sys.executable, str(SCRIPT), str(target)], check=True)
            identity_before = (target / ".abes" / "project" / "identity.md").read_text(encoding="utf-8")
            subprocess.run([sys.executable, str(SCRIPT), str(target)], check=True)

            agents = (target / "AGENTS.md").read_text(encoding="utf-8")
            identity_after = (target / ".abes" / "project" / "identity.md").read_text(encoding="utf-8")
            self.assertEqual(agents.count("<!-- ABES:START -->"), 1)
            self.assertEqual(agents.count("<!-- ABES:END -->"), 1)
            self.assertEqual(identity_before, identity_after)

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
            goals = target / ".abes" / "project" / "goals.md"
            goals.parent.mkdir(parents=True)
            goals.write_text("# Custom goals\n\nDo not overwrite.\n", encoding="utf-8")

            subprocess.run([sys.executable, str(SCRIPT), str(target), "--force"], check=True)

            self.assertEqual(goals.read_text(encoding="utf-8"), "# Custom goals\n\nDo not overwrite.\n")

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


if __name__ == "__main__":
    unittest.main()
