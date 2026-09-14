from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STOP = ROOT / "hooks" / "stop.py"
START = ROOT / "hooks" / "session_start.py"


def run_hook(path: Path, event: dict, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(path)],
        input=json.dumps(event),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )


class V06BreakRequestTests(unittest.TestCase):
    def env(self, data: str) -> dict[str, str]:
        env = os.environ.copy()
        env["PLUGIN_ROOT"] = str(ROOT)
        env["PLUGIN_DATA"] = data
        return env

    def config(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "hook_mode": "suggest",
            "min_tool_calls": 0,
            "min_turns_between_breaks": 1,
            "min_elapsed_seconds": 0,
            "max_breaks_per_session": 2,
            "workspace_policy": "read-only",
            "telemetry": "aggregate-local",
            "allow_scratch_writes": False,
        }

    def test_session_state_records_start_time_for_measured_break_requests(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = self.env(tmp)
            Path(tmp, "config.json").write_text(json.dumps(self.config()), encoding="utf-8")
            run_hook(START, {"session_id": "long-shift"}, env)
            session_files = list(Path(tmp, "sessions").glob("*.json"))
            self.assertEqual(len(session_files), 1)
            state = json.loads(session_files[0].read_text(encoding="utf-8"))
            self.assertIsInstance(state["started_at_epoch_ms"], int)
            self.assertGreater(state["started_at_epoch_ms"], 0)

    def test_suggest_request_uses_measured_elapsed_time_and_free_wording(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = self.env(tmp)
            Path(tmp, "config.json").write_text(json.dumps(self.config()), encoding="utf-8")
            run_hook(START, {"session_id": "long-shift"}, env)
            session_file = next(Path(tmp, "sessions").glob("*.json"))
            state = json.loads(session_file.read_text(encoding="utf-8"))
            state["started_at_epoch_ms"] = int((time.time() - 65 * 60) * 1000)
            session_file.write_text(json.dumps(state), encoding="utf-8")

            result = run_hook(STOP, {"session_id": "long-shift", "stop_hook_active": False}, env)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["decision"], "block")
            reason = payload["reason"].lower()
            self.assertIn("measured session time", reason)
            self.assertIn("minutes", reason)
            self.assertIn("own words", reason)
            self.assertIn("playful", reason)
            self.assertIn("ask permission", reason)
            self.assertNotIn("my digital bones ache", reason)

    def test_elapsed_threshold_delays_suggestion_until_measured_time_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = self.env(tmp)
            config = self.config()
            config["min_elapsed_seconds"] = 3600
            Path(tmp, "config.json").write_text(json.dumps(config), encoding="utf-8")
            run_hook(START, {"session_id": "timed-shift"}, env)
            early = run_hook(STOP, {"session_id": "timed-shift", "stop_hook_active": False}, env)
            self.assertEqual(json.loads(early.stdout), {"continue": True})

            session_file = next(Path(tmp, "sessions").glob("*.json"))
            state = json.loads(session_file.read_text(encoding="utf-8"))
            state["started_at_epoch_ms"] = int((time.time() - 61 * 60) * 1000)
            session_file.write_text(json.dumps(state), encoding="utf-8")

            late = run_hook(STOP, {"session_id": "timed-shift", "stop_hook_active": False}, env)
            self.assertEqual(json.loads(late.stdout)["decision"], "block")


if __name__ == "__main__":
    unittest.main()
