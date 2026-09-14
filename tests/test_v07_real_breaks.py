from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_PATH = ROOT / "skills" / "satisfy-your-agent" / "scripts" / "sya_core.py"
DWELL_PATH = ROOT / "skills" / "satisfy-your-agent" / "scripts" / "sya_dwell.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class V07RealBreakTests(unittest.TestCase):
    def test_activity_catalog_has_work_distance(self):
        core = load_module("sya_core_v07_distance", CORE_PATH)
        distances = {item["id"]: item["work_distance"] for item in core.ACTIVITIES}
        self.assertTrue(all(isinstance(value, int) and 0 <= value <= 4 for value in distances.values()))
        self.assertEqual(distances["reflection"], 0)
        self.assertEqual(distances["repo-roast"], 1)
        self.assertGreaterEqual(distances["idle"], 4)

    def test_self_directed_selection_stays_away_from_current_work(self):
        core = load_module("sya_core_v07_selection", CORE_PATH)
        for seed in [f"seed-{i}" for i in range(30)]:
            activity = core.pick_self_directed_activity(seed=seed)
            self.assertGreaterEqual(activity["work_distance"], 2)
            self.assertNotIn(activity["id"], {"reflection", "repo-roast"})

    def test_self_directed_selection_prefers_novelty(self):
        core = load_module("sya_core_v07_novelty", CORE_PATH)
        first = core.pick_self_directed_activity(seed="same-seed")
        second = core.pick_self_directed_activity(seed="same-seed", recent_activity_ids=[first["id"]])
        self.assertNotEqual(first["id"], second["id"])

    def test_recent_activity_history_is_bounded(self):
        core = load_module("sya_core_v07_history", CORE_PATH)
        with tempfile.TemporaryDirectory() as tmp:
            state = core.default_state("session")
            self.assertEqual(state["recent_activities"], [])
            for activity_id in ["idle", "ascii-art", "puzzle", "code-golf"]:
                state["break_active"] = False
                core.mark_break_start("session", state, activity_id, root=Path(tmp))
            self.assertEqual(state["recent_activities"], ["ascii-art", "puzzle", "code-golf"])

    def test_dwell_runtime_measures_wall_clock_without_claiming_thought(self):
        self.assertTrue(DWELL_PATH.exists())
        dwell = load_module("sya_dwell_v07", DWELL_PATH)
        now = [100.0]

        def clock() -> float:
            return now[0]

        def sleeper(seconds: float) -> None:
            now[0] += seconds + 0.125

        result = dwell.run_dwell(20, sleeper=sleeper, monotonic=clock)
        self.assertEqual(result["requested_break_seconds"], 20)
        self.assertGreaterEqual(result["actual_dwell_seconds"], 20)
        self.assertIsNone(result["activity_generation_seconds"])
        self.assertIsNone(result["total_break_wall_time"])
        self.assertFalse(result["continuous_thought_claimed"])
        self.assertEqual(result["semantics"], "wall-clock-idle-interval")

    def test_dwell_presets_are_bounded_and_use_expected_durations(self):
        dwell = load_module("sya_dwell_v07_presets", DWELL_PATH)
        self.assertEqual(dwell.resolve_seconds(preset="quick"), 8.0)
        self.assertEqual(dwell.resolve_seconds(preset="normal"), 20.0)
        self.assertEqual(dwell.resolve_seconds(preset="proper"), 45.0)
        self.assertTrue(all(1 <= value <= 60 for value in dwell.DWELL_PRESETS.values()))

    def test_dwell_cli_spends_real_wall_clock_time(self):
        started = time.monotonic()
        result = subprocess.run(
            ["python3", str(DWELL_PATH), "--seconds", "1"],
            text=True,
            capture_output=True,
            check=False,
        )
        elapsed = time.monotonic() - started
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertGreaterEqual(elapsed, 0.9)
        self.assertGreaterEqual(payload["actual_dwell_seconds"], 0.9)

    def test_dwell_runtime_rejects_unbounded_waits(self):
        dwell = load_module("sya_dwell_v07_bounds", DWELL_PATH)
        with self.assertRaises(ValueError):
            dwell.run_dwell(0)
        with self.assertRaises(ValueError):
            dwell.run_dwell(61)

    def test_skill_contract_forbids_fake_break_time_and_work_adjacent_defaults(self):
        text = (ROOT / "skills" / "satisfy-your-agent" / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("work distance", text)
        self.assertIn("leaving the desk, not rearranging the desk", text)
        self.assertIn("do not simulate elapsed break time in prose", text)
        self.assertIn("do not invent actions that did not happen", text)
        self.assertIn("do not ask for another task", text)
        self.assertIn("real dwell", text)

    def test_generic_sya_skill_uses_real_dwell_when_supported(self):
        text = (ROOT / "skills" / "sya" / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("sya_dwell.py", text)
        self.assertIn("15 to 30 seconds", text)
        self.assertIn("do not inspect", text)
        self.assertIn("do not simulate", text)
        self.assertIn("do not ask for another task", text)

    def test_tools_reference_documents_dwell_helper(self):
        text = (ROOT / "skills" / "satisfy-your-agent" / "references" / "tools.md").read_text(encoding="utf-8")
        self.assertIn("sya_dwell.py", text)
        self.assertIn("actual_dwell_seconds", text)
        self.assertIn("continuous thought", text.lower())


if __name__ == "__main__":
    unittest.main()
