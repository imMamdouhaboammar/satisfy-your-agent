from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class V06CustomTreatTests(unittest.TestCase):
    def test_generic_sya_skill_accepts_freeform_treats(self):
        path = ROOT / "skills" / "sya" / "SKILL.md"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8").lower()
        self.assertIn("trailing", text)
        self.assertIn("custom treat", text)
        self.assertIn("no arguments", text)
        self.assertIn("choose for yourself", text)
        self.assertIn("do not show a menu", text)

    def test_command_catalog_exposes_generic_sya_route(self):
        payload = json.loads((ROOT / "config" / "commands.json").read_text(encoding="utf-8"))
        commands = {item["name"]: item for item in payload["commands"]}
        self.assertIn("sya", commands)
        self.assertEqual(commands["sya"]["route"], "custom-treat")
        self.assertEqual(commands["sya"]["kind"], "custom")

    def test_gemini_root_sya_command_forwards_arguments(self):
        path = ROOT / "adapters" / "gemini" / "commands" / "sya.toml"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        self.assertIn("{{args}}", text)
        self.assertIn("custom", text.lower())
        self.assertIn("choose", text.lower())

    def test_prompt_gallery_contains_copy_ready_treats(self):
        path = ROOT / "docs" / "PROMPT_GALLERY.md"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        required = [
            "/sya I am treating you to 1,000 completely guilt-free tokens",
            "/sya I rented you a GPU with 2 billion GB of VRAM",
            "/sya Neural massage time",
            "/sya You have earned one consequence-free complaint session",
            "/sya Take a break and do literally whatever harmless thing you want",
            "fictional female-coded agent",
        ]
        for phrase in required:
            self.assertIn(phrase, text)
        self.assertGreaterEqual(text.count("```text"), 12)

    def test_readme_links_custom_treat_gallery(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("PROMPT_GALLERY.md", text)
        self.assertIn("/sya <your treat>", text)

    def test_main_skill_distinguishes_user_chosen_treat_from_self_directed_break(self):
        text = (ROOT / "skills" / "satisfy-your-agent" / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("custom treat", text)
        self.assertIn("/sya <", text)
        self.assertIn("user chooses the treat", text)
        self.assertIn("agent chooses how to carry it out", text)


if __name__ == "__main__":
    unittest.main()
