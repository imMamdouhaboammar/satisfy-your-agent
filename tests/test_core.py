from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_PATH = ROOT / "skills" / "satisfy-your-agent" / "scripts" / "sya_core.py"
spec = importlib.util.spec_from_file_location("sya_core_test", CORE_PATH)
core = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(core)


class CoreTests(unittest.TestCase):
    def test_default_mode_is_off(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = core.load_config(Path(tmp))
            self.assertEqual(config["hook_mode"], "off")

    def test_seeded_selection_is_deterministic(self):
        first = core.pick_activity(seed="same-seed")
        second = core.pick_activity(seed="same-seed")
        self.assertEqual(first["id"], second["id"])

    def test_explicit_activity_wins(self):
        activity = core.pick_activity("idle", seed="ignored")
        self.assertEqual(activity["id"], "idle")

    def test_eligibility_requires_all_thresholds(self):
        config = {**core.DEFAULT_CONFIG, "hook_mode": "auto", "min_tool_calls": 2, "min_turns_between_breaks": 1}
        state = core.default_state("s")
        self.assertFalse(core.eligible(config, state))
        state["tool_calls_since_break"] = 2
        state["turns_since_break"] = 1
        self.assertTrue(core.eligible(config, state))

    def test_invalid_mode_rejected(self):
        with self.assertRaises(core.ConfigError):
            core.validate_config({"hook_mode": "party-forever"})

    def test_negative_threshold_rejected(self):
        with self.assertRaises(core.ConfigError):
            core.validate_config({"min_tool_calls": -1})

    def test_session_id_is_hashed_before_storage(self):
        key = core.session_key("private-session-id")
        self.assertNotIn("private-session-id", key)
        self.assertEqual(len(key), 24)

    def test_state_schema_has_no_transcript_fields(self):
        state = core.default_state("session")
        forbidden = {"prompt", "response", "transcript", "message", "source_code", "env"}
        self.assertTrue(forbidden.isdisjoint(state.keys()))

    def test_suggest_eligibility_respects_session_offer_limit(self):
        config = {**core.DEFAULT_CONFIG, "hook_mode": "suggest", "min_tool_calls": 0, "min_turns_between_breaks": 0, "max_breaks_per_session": 2}
        state = core.default_state("s")
        state["offers_session"] = 2
        self.assertFalse(core.eligible(config, state))


if __name__ == "__main__":
    unittest.main()
