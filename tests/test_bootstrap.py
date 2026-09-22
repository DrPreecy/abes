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
            (target / "src").mkdir()
            (target / "tests").mkdir()
            subprocess.run([sys.executable, str(SCRIPT), str(target)], check=True)

            self.assertTrue((target / "AGENTS.md").exists())
            self.assertTrue((target / ".abes" / "project" / "identity.md").exists())
            self.assertTrue((target / ".abes" / "memory" / "opportunities.md").exists())

            identity = (target / ".abes" / "project" / "identity.md").read_text()
            self.assertIn("JavaScript/TypeScript", identity)
            self.assertIn("npm run test", identity)
            self.assertIn("- src", identity)
            self.assertIn("- tests", identity)

    def test_bootstrap_preserves_existing_agents_with_managed_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-project"
            target.mkdir()
            (target / "AGENTS.md").write_text("# Existing\n\nKeep this.\n")

            subprocess.run([sys.executable, str(SCRIPT), str(target)], check=True)

            agents = (target / "AGENTS.md").read_text()
            self.assertIn("<!-- ABES:START -->", agents)
            self.assertIn("# Existing", agents)
            self.assertIn("Keep this.", agents)

    def test_bootstrap_is_idempotent_on_fresh_repository(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-project"
            target.mkdir()

            subprocess.run([sys.executable, str(SCRIPT), str(target)], check=True)
            subprocess.run([sys.executable, str(SCRIPT), str(target)], check=True)

            agents = (target / "AGENTS.md").read_text()
            self.assertEqual(agents.count("<!-- ABES:START -->"), 1)
            self.assertEqual(agents.count("<!-- ABES:END -->"), 1)


if __name__ == "__main__":
    unittest.main()
