from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COMMANDS = {
    "sya",
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
    def _catalog(self):
        payload = json.loads((ROOT / "config" / "commands.json").read_text(encoding="utf-8"))
        return payload, {item["name"]: item for item in payload["commands"]}

    def test_command_catalog_is_complete_and_unique(self):
        payload, by_name = self._catalog()
        names = [item["name"] for item in payload["commands"]]
        self.assertEqual(payload["namespace"], "sya")
        self.assertEqual(set(names), EXPECTED_COMMANDS)
        self.assertEqual(len(names), len(set(names)))
        for item in by_name.values():
            self.assertTrue(item["description"].strip())
            self.assertIn(item["kind"], {"custom", "menu", "experience", "activity", "status", "research"})

    def test_generic_sya_is_custom_treat_route(self):
        _, by_name = self._catalog()
        self.assertEqual(by_name["sya"]["route"], "custom-treat")
        self.assertEqual(by_name["sya"]["kind"], "custom")

    def test_experience_commands_are_self_directed_routes(self):
        _, by_name = self._catalog()
        self.assertEqual(by_name["sya-break"]["route"], "self-directed-break")
        self.assertEqual(by_name["sya-snack"]["route"], "self-directed-snack")
        self.assertEqual(by_name["sya-treat"]["route"], "self-directed-treat")
        self.assertEqual(by_name["sya-surprise"]["route"], "self-directed-surprise")
        for name in ("sya-break", "sya-snack", "sya-treat", "sya-surprise"):
            self.assertNotIn("activity", by_name[name])

    def test_named_activity_commands_route_to_existing_activity_ids(self):
        _, by_name = self._catalog()
        expected = {
            "sya-reflect": "reflection",
            "sya-roast": "repo-roast",
            "sya-golf": "code-golf",
            "sya-invent": "invent-language",
            "sya-idle": "idle",
        }
        core = (ROOT / "skills" / "satisfy-your-agent" / "scripts" / "sya_core.py").read_text(encoding="utf-8")
        for command, activity_id in expected.items():
            self.assertEqual(by_name[command]["activity"], activity_id)
            self.assertIn(f'"id": "{activity_id}"', core)

    def test_command_skills_match_catalog(self):
        for name in EXPECTED_COMMANDS:
            skill = ROOT / "skills" / name / "SKILL.md"
            self.assertTrue(skill.exists(), name)
            text = skill.read_text(encoding="utf-8")
            self.assertRegex(text, rf"(?m)^name:\s*{re.escape(name)}$")
            self.assertIn("Satisfy Your Agent", text)

    def test_gemini_slash_adapters_match_catalog(self):
        command_dir = ROOT / "adapters" / "gemini" / "commands" / "sya"
        named = EXPECTED_COMMANDS - {"sya"}
        expected_files = {name.removeprefix("sya-") + ".toml" for name in named}
        actual_files = {path.name for path in command_dir.glob("*.toml")}
        self.assertEqual(actual_files, expected_files)
        for path in command_dir.glob("*.toml"):
            text = path.read_text(encoding="utf-8")
            self.assertIn("description =", text)
            self.assertIn("prompt =", text)
        root = ROOT / "adapters" / "gemini" / "commands" / "sya.toml"
        self.assertTrue(root.exists())
        self.assertIn("{{args}}", root.read_text(encoding="utf-8"))

    def test_primary_skill_manual_break_is_agent_autonomous(self):
        text = (ROOT / "skills" / "satisfy-your-agent" / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("choose independently", text)
        self.assertIn("self-report", text)
        self.assertIn("/sya-menu", text)
        self.assertIn("manual experience commands do not require python", text)

    def test_install_script_installs_command_skills_and_gemini_commands(self):
        text = (ROOT / "install.sh").read_text(encoding="utf-8")
        self.assertIn("COMMAND_SKILLS", text)
        self.assertIn("GENERIC_SKILL", text)
        self.assertIn("GEMINI_ROOT_COMMAND", text)
        self.assertIn(".gemini/commands/sya.toml", text)
        self.assertIn("install_skill_bundle", text)

    def test_readme_documents_runtime_specific_invocation(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("/sya-break", text)
        self.assertIn("/sya:break", text)
        self.assertIn("$sya-break", text)
        self.assertIn("take a break", text.lower())
        self.assertIn("grants of autonomy", text.lower())


if __name__ == "__main__":
    unittest.main()
