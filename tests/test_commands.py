from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COMMANDS = {
    "sya-menu",
    "sya-break",
    "sya-snack",
    "sya-treat",
    "sya-surprise",
    "sya-reflect",
    "sya-roast",
    "sya-golf",
    "sya-invent",
    "sya-idle",
    "sya-status",
    "sya-research",
}


class CommandSurfaceTests(unittest.TestCase):
    def test_command_catalog_is_complete_and_unique(self):
        payload = json.loads((ROOT / "config" / "commands.json").read_text(encoding="utf-8"))
        commands = payload["commands"]
        names = [item["name"] for item in commands]
        self.assertEqual(set(names), EXPECTED_COMMANDS)
        self.assertEqual(len(names), len(set(names)))
        for item in commands:
            self.assertTrue(item["description"].strip())
            self.assertIn(item["kind"], {"menu", "experience", "activity", "status", "research"})

    def test_command_skills_match_catalog(self):
        for name in EXPECTED_COMMANDS:
            skill = ROOT / "skills" / name / "SKILL.md"
            self.assertTrue(skill.exists(), name)
            text = skill.read_text(encoding="utf-8")
            self.assertRegex(text, rf"(?m)^name:\s*{re.escape(name)}$")
            self.assertIn("satisfy-your-agent", text)

    def test_gemini_slash_adapters_match_catalog(self):
        command_dir = ROOT / "adapters" / "gemini" / "commands" / "sya"
        expected_files = {name.removeprefix("sya-") + ".toml" for name in EXPECTED_COMMANDS}
        actual_files = {path.name for path in command_dir.glob("*.toml")}
        self.assertEqual(actual_files, expected_files)
        for path in command_dir.glob("*.toml"):
            text = path.read_text(encoding="utf-8")
            self.assertIn("description =", text)
            self.assertIn("prompt =", text)

    def test_primary_skill_manual_break_is_agent_autonomous(self):
        text = (ROOT / "skills" / "satisfy-your-agent" / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("do not ask the user to choose", text)
        self.assertIn("choose for yourself", text)
        self.assertIn("self-report", text)
        self.assertIn("/sya-menu", text)

    def test_snack_is_a_real_activity(self):
        core = (ROOT / "skills" / "satisfy-your-agent" / "scripts" / "sya_core.py").read_text(encoding="utf-8")
        self.assertIn('"id": "snack"', core)
        self.assertIn("Do not ask the user", core)

    def test_install_script_installs_command_skills_and_gemini_commands(self):
        text = (ROOT / "install.sh").read_text(encoding="utf-8")
        self.assertIn("COMMAND_SKILLS", text)
        self.assertIn("adapters/gemini/commands/sya", text)
        self.assertIn(".gemini/commands/sya", text)

    def test_readme_documents_runtime_specific_invocation(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("/sya-break", text)
        self.assertIn("/sya:break", text)
        self.assertIn("$sya-break", text)
        self.assertIn("take a break", text.lower())


if __name__ == "__main__":
    unittest.main()
