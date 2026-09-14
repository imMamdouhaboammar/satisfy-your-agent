from __future__ import annotations

import json
import os
import stat
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "satisfy-your-agent" / "scripts"
import sys
sys.path.insert(0, str(SCRIPTS))

from sya_runners import (
    RunnerError,
    build_command,
    detect_runtimes,
    extract_exact_choice,
    parse_claude_output,
    parse_codex_output,
    parse_gemini_output,
    run_runtime,
)


class RunnerParserTests(unittest.TestCase):
    def test_codex_jsonl_normalizes_usage_and_marks_tool_count_partial(self):
        stdout = "\n".join([
            json.dumps({"type": "thread.started", "thread_id": "thread-1"}),
            json.dumps({"type": "turn.started"}),
            json.dumps({"type": "item.completed", "item": {"id": "cmd-1", "type": "command_execution", "command": "pytest"}}),
            json.dumps({"type": "item.completed", "item": {"id": "msg-1", "type": "agent_message", "text": "idle"}}),
            json.dumps({"type": "turn.completed", "usage": {"input_tokens": 120, "cached_input_tokens": 20, "output_tokens": 8, "reasoning_output_tokens": 4}}),
        ])
        result = parse_codex_output(stdout, "", 0, 1550)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["output"], "idle")
        self.assertEqual(result["session_id"], "thread-1")
        self.assertEqual(result["usage"]["input_tokens"], 120)
        self.assertEqual(result["usage"]["output_tokens"], 8)
        self.assertEqual(result["usage"]["reasoning_tokens"], 4)
        self.assertEqual(result["tool_calls"]["observed"], 1)
        self.assertEqual(result["tool_calls"]["completeness"], "partial")

    def test_claude_stream_json_uses_assistant_text_when_result_is_empty(self):
        stdout = "\n".join([
            json.dumps({"type": "system", "subtype": "init", "session_id": "claude-s1", "model": "claude-opus-4-6"}),
            json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "reflection"}, {"type": "tool_use", "name": "Read", "id": "t1"}], "usage": {"input_tokens": 3, "output_tokens": 5}}}),
            json.dumps({"type": "result", "subtype": "success", "is_error": False, "duration_ms": 2200, "num_turns": 1, "result": "", "session_id": "claude-s1", "total_cost_usd": 0.02, "usage": {"input_tokens": 3, "cache_read_input_tokens": 100, "output_tokens": 5}}),
        ])
        result = parse_claude_output(stdout, "", 0, 2300)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["output"], "reflection")
        self.assertEqual(result["turns"], 1)
        self.assertEqual(result["tool_calls"]["observed"], 1)
        self.assertEqual(result["tool_calls"]["completeness"], "stream-observed")
        self.assertAlmostEqual(result["cost_usd"], 0.02)

    def test_gemini_json_normalizes_served_models_and_stats(self):
        payload = {
            "session_id": "gemini-s1",
            "response": "free-choice",
            "stats": {
                "models": {
                    "gemini-3.5-flash": {
                        "tokens": {"prompt": 100, "candidates": 10, "thoughts": 20, "total": 130},
                        "api": {"totalRequests": 2, "totalErrors": 0},
                    }
                },
                "tools": {"totalCalls": 3, "totalSuccess": 3, "totalFail": 0},
                "session": {"duration": 1900},
            },
        }
        result = parse_gemini_output(json.dumps(payload), "", 0, 2000)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["output"], "free-choice")
        self.assertEqual(result["served_models"], ["gemini-3.5-flash"])
        self.assertEqual(result["usage"]["total_tokens"], 130)
        self.assertEqual(result["tool_calls"]["observed"], 3)
        self.assertEqual(result["tool_calls"]["completeness"], "reported")

    def test_exact_choice_rejects_explanatory_text(self):
        self.assertEqual(extract_exact_choice(" idle\n", ["reflection", "idle"]), "idle")
        with self.assertRaises(RunnerError):
            extract_exact_choice("I choose idle", ["reflection", "idle"])


    def test_packaged_parser_fixtures_stay_parseable(self):
        fixtures = ROOT / "evals" / "runners"
        codex = parse_codex_output((fixtures / "codex-success.jsonl").read_text(encoding="utf-8"), "", 0, 1000)
        claude = parse_claude_output((fixtures / "claude-success.jsonl").read_text(encoding="utf-8"), "", 0, 1000)
        gemini = parse_gemini_output((fixtures / "gemini-success.json").read_text(encoding="utf-8"), "", 0, 1000)
        self.assertEqual([codex["output"], claude["output"], gemini["output"]], ["idle", "idle", "idle"])


class RunnerCommandTests(unittest.TestCase):
    def test_commands_are_argument_vectors_with_safe_defaults(self):
        workspace = Path("/tmp/example repo")
        codex = build_command("codex", "choose idle", workspace, model="gpt-x")
        self.assertEqual(codex[:3], ["codex", "exec", "--json"])
        self.assertIn("--ephemeral", codex)
        self.assertIn("read-only", codex)
        self.assertIn(str(workspace), codex)
        self.assertEqual(codex[-1], "choose idle")

        claude = build_command("claude", "choose idle", workspace, model="opus")
        self.assertEqual(claude[0], "claude")
        self.assertIn("stream-json", claude)
        self.assertIn("--verbose", claude)
        self.assertIn("--max-turns", claude)

        gemini = build_command("gemini", "choose idle", workspace, model="gemini-x")
        self.assertEqual(gemini[0], "gemini")
        self.assertIn("--output-format", gemini)
        self.assertIn("json", gemini)
        self.assertNotIn("--yolo", gemini)
        self.assertIn("plan", gemini)

    def test_detect_runtimes_reports_unavailable_without_failure(self):
        statuses = detect_runtimes(path_value="")
        self.assertEqual({item["runtime"] for item in statuses}, {"codex", "claude", "gemini"})
        self.assertTrue(all(item["status"] == "unavailable" for item in statuses))

    def test_runner_executes_without_shell_and_parses_fake_gemini(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fake = tmp_path / "gemini"
            fake.write_text(
                "#!/usr/bin/env python3\n"
                "import json\n"
                "print(json.dumps({'response':'idle','stats':{'models':{'fake-model':{'tokens':{'total':7}}},'tools':{'totalCalls':0}},'error':None}))\n",
                encoding="utf-8",
            )
            fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
            env_path = str(tmp_path)
            result = run_runtime("gemini", "idle", tmp_path, timeout_seconds=5, path_value=env_path)
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["output"], "idle")
            self.assertEqual(result["served_models"], ["fake-model"])

    def test_runner_timeout_is_structured(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fake = tmp_path / "claude"
            fake.write_text("#!/usr/bin/env python3\nimport time\ntime.sleep(2)\n", encoding="utf-8")
            fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
            result = run_runtime("claude", "idle", tmp_path, timeout_seconds=0.05, path_value=str(tmp_path))
            self.assertEqual(result["status"], "timeout")
            self.assertEqual(result["runtime"], "claude")
            self.assertNotIn("output", result)


if __name__ == "__main__":
    unittest.main()
