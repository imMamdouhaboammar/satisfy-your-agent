from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STOP = ROOT / "hooks" / "stop.py"
POST = ROOT / "hooks" / "post_tool_use.py"
START = ROOT / "hooks" / "session_start.py"
END = ROOT / "hooks" / "session_end.py"


def run_hook(path: Path, event: dict, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(path)],
        input=json.dumps(event),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )


class HookTests(unittest.TestCase):
    def env(self, data: str) -> dict[str, str]:
        env = os.environ.copy()
        env["PLUGIN_ROOT"] = str(ROOT)
        env["PLUGIN_DATA"] = data
        return env

    def test_off_mode_never_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = self.env(tmp)
            run_hook(START, {"session_id": "a"}, env)
            result = run_hook(STOP, {"session_id": "a", "stop_hook_active": False}, env)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout), {"continue": True})

    def test_auto_mode_blocks_once_then_break_continuation_finishes(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = self.env(tmp)
            config = {
                "schema_version": 1,
                "hook_mode": "auto",
                "min_tool_calls": 1,
                "min_turns_between_breaks": 1,
                "max_breaks_per_session": 2,
                "workspace_policy": "read-only",
                "telemetry": "aggregate-local",
                "allow_scratch_writes": False,
            }
            Path(tmp, "config.json").write_text(json.dumps(config), encoding="utf-8")
            run_hook(START, {"session_id": "a"}, env)
            run_hook(POST, {"session_id": "a", "tool_name": "apply_patch"}, env)
            first = run_hook(STOP, {"session_id": "a", "stop_hook_active": False}, env)
            payload = json.loads(first.stdout)
            self.assertEqual(payload["decision"], "block")
            self.assertIn("Satisfy Your Agent", payload["reason"])
            second = run_hook(STOP, {"session_id": "a", "stop_hook_active": True}, env)
            self.assertEqual(json.loads(second.stdout), {"continue": True})

    def test_suggest_mode_asks_before_break(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = self.env(tmp)
            config = {
                "schema_version": 1,
                "hook_mode": "suggest",
                "min_tool_calls": 0,
                "min_turns_between_breaks": 1,
                "max_breaks_per_session": 2,
                "workspace_policy": "read-only",
                "telemetry": "aggregate-local",
                "allow_scratch_writes": False,
            }
            Path(tmp, "config.json").write_text(json.dumps(config), encoding="utf-8")
            run_hook(START, {"session_id": "a"}, env)
            result = run_hook(STOP, {"session_id": "a", "stop_hook_active": False}, env)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["decision"], "block")
            reason = payload["reason"].lower()
            self.assertIn("ask permission", reason)
            self.assertIn("do not begin the break unless the user agrees", reason)

    def test_hook_ignores_transcript_path_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = self.env(tmp)
            secret_file = Path(tmp, "secret-transcript.txt")
            secret_file.write_text("SHOULD_NOT_BE_READ_OR_PERSISTED", encoding="utf-8")
            run_hook(START, {"session_id": "a", "transcript_path": str(secret_file)}, env)
            persisted = "".join(p.read_text(encoding="utf-8") for p in Path(tmp).rglob("*.json"))
            self.assertNotIn("SHOULD_NOT_BE_READ_OR_PERSISTED", persisted)
            self.assertNotIn(str(secret_file), persisted)

    def test_off_mode_is_storage_inert(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = self.env(tmp)
            run_hook(START, {"session_id": "a"}, env)
            run_hook(POST, {"session_id": "a", "tool_name": "Bash"}, env)
            run_hook(STOP, {"session_id": "a", "stop_hook_active": False}, env)
            run_hook(END, {"session_id": "a", "reason": "other"}, env)
            self.assertEqual(list(Path(tmp).rglob("*")), [])


if __name__ == "__main__":
    unittest.main()
