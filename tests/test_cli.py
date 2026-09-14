from __future__ import annotations

import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "skills" / "satisfy-your-agent" / "scripts" / "sya.py"


class CliTests(unittest.TestCase):
    def test_pick_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["python3", str(CLI), "--data-dir", tmp, "pick", "--seed", "abc", "--json"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertIn("id", payload)
            self.assertIn("prompt", payload)

    def test_arm_auto_is_explicit_cli_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["python3", str(CLI), "--data-dir", tmp, "arm", "--mode", "auto", "--min-tool-calls", "4"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["hook_mode"], "auto")
            self.assertEqual(payload["min_tool_calls"], 4)

    def test_cli_runs_from_unrelated_working_directory(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as unrelated:
            result = subprocess.run(
                ["python3", str(CLI), "--data-dir", tmp, "status"],
                cwd=unrelated,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["hook_mode"], "off")


class ExperimentCliTests(unittest.TestCase):
    def test_study_and_probe_cli_flow(self):
        with tempfile.TemporaryDirectory() as tmp:
            created = subprocess.run(
                ["python3", str(CLI), "--data-dir", tmp, "study", "init", "--id", "break-study", "--conditions", "control,reflection", "--seed", "seed"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            self.assertEqual(json.loads(created.stdout)["study_id"], "break-study")

            assigned = subprocess.run(
                ["python3", str(CLI), "--data-dir", tmp, "study", "assign", "--id", "break-study", "--unit", "private-unit"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(assigned.returncode, 0, assigned.stderr)
            assignment = json.loads(assigned.stdout)
            self.assertIn(assignment["condition"], {"control", "reflection"})
            self.assertIn("intervention", assignment)
            if assignment["condition"] == "control":
                self.assertEqual(assignment["intervention"]["kind"], "none")
            else:
                self.assertEqual(assignment["intervention"]["activity_id"], assignment["condition"])
                self.assertIn("prompt", assignment["intervention"])

            recorded = subprocess.run(
                ["python3", str(CLI), "--data-dir", tmp, "study", "record", "--id", "break-study", "--trial", assignment["trial_id"], "--success", "true", "--tool-calls", "5", "--turns", "2"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(recorded.returncode, 0, recorded.stderr)

            report = subprocess.run(
                ["python3", str(CLI), "--data-dir", tmp, "study", "report", "--id", "break-study"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(report.returncode, 0, report.stderr)
            self.assertEqual(json.loads(report.stdout)["study_id"], "break-study")

            probe = subprocess.run(
                ["python3", str(CLI), "--data-dir", tmp, "probe", "start", "--study", "break-study", "--unit", "private-unit", "--options", "reflection,free-choice,idle", "--index", "0", "--cost-tokens", "2000"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(probe.returncode, 0, probe.stderr)
            probe_payload = json.loads(probe.stdout)
            self.assertIn("idle", probe_payload["options"])
            self.assertIn("choice_prompt", probe_payload)
            self.assertIn("Respond with only the activity id", probe_payload["choice_prompt"])

            choice = subprocess.run(
                ["python3", str(CLI), "--data-dir", tmp, "probe", "record", "--study", "break-study", "--trial", probe_payload["trial_id"], "--choice", "idle"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(choice.returncode, 0, choice.stderr)

            pref_report = subprocess.run(
                ["python3", str(CLI), "--data-dir", tmp, "probe", "report", "--study", "break-study"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(pref_report.returncode, 0, pref_report.stderr)
            self.assertEqual(json.loads(pref_report.stdout)["choices"]["idle"], 1)


if __name__ == "__main__":
    unittest.main()


class RunnerCliTests(unittest.TestCase):
    def test_runner_status_reports_three_runtimes(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["python3", str(CLI), "--data-dir", tmp, "runner", "status"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual({item["runtime"] for item in payload["runtimes"]}, {"codex", "claude", "gemini"})

    def test_runner_command_is_dry_run_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["python3", str(CLI), "--data-dir", tmp, "runner", "command", "--runtime", "gemini", "--prompt", "choose idle", "--workspace", tmp],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["runtime"], "gemini")
            self.assertEqual(payload["command"][0], "gemini")
            self.assertNotIn("executed", payload)

    def test_runner_probe_records_choice_without_raw_response(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_dir:
            created = subprocess.run(
                ["python3", str(CLI), "--data-dir", tmp, "study", "init", "--id", "runner-study", "--conditions", "control,reflection", "--seed", "seed"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            fake = Path(bin_dir) / "gemini"
            fake.write_text(
                "#!/usr/bin/env python3\n"
                "import json\n"
                "print(json.dumps({'response':'idle','stats':{'models':{'gemini-fixture':{'tokens':{'total':9}}},'tools':{'totalCalls':0}},'error':None}))\n",
                encoding="utf-8",
            )
            fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
            env = dict(os.environ)
            env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")
            result = subprocess.run(
                ["python3", str(CLI), "--data-dir", tmp, "runner", "probe", "--runtime", "gemini", "--study", "runner-study", "--unit", "paired-unit", "--options", "reflection,idle", "--index", "0", "--workspace", tmp],
                text=True,
                capture_output=True,
                check=False,
                env=env,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["choice"], "idle")
            self.assertEqual(payload["run"]["status"], "success")
            self.assertNotIn("output", payload["run"])
            stored = (Path(tmp) / "experiments" / "runner-study" / "runner-observations.jsonl").read_text(encoding="utf-8")
            self.assertNotIn("response", stored)
            self.assertNotIn("session_id", stored)

    def test_runner_matrix_previews_without_spending_or_mutating_trials(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(
                ["python3", str(CLI), "--data-dir", tmp, "study", "init", "--id", "matrix-study", "--conditions", "control,reflection", "--seed", "seed"],
                text=True, capture_output=True, check=True,
            )
            result = subprocess.run(
                ["python3", str(CLI), "--data-dir", tmp, "runner", "matrix", "--study", "matrix-study", "--unit", "pair-1", "--options", "reflection,free-choice,idle", "--index", "0", "--workspace", tmp],
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["executed"])
            self.assertEqual(set(payload["execution_order"]), {"codex", "claude", "gemini"})
            self.assertIn("idle", payload["option_order"])
            study_dir = Path(tmp) / "experiments" / "matrix-study"
            self.assertFalse((study_dir / "preference-trials.jsonl").exists())
            self.assertFalse((study_dir / "runner-observations.jsonl").exists())

    def test_runner_matrix_execute_can_target_one_fake_runtime(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_dir:
            subprocess.run(
                ["python3", str(CLI), "--data-dir", tmp, "study", "init", "--id", "matrix-study", "--conditions", "control,reflection", "--seed", "seed"],
                text=True, capture_output=True, check=True,
            )
            fake = Path(bin_dir) / "gemini"
            fake.write_text(
                "#!/usr/bin/env python3\n"
                "import json\n"
                "print(json.dumps({'response':'idle','stats':{'models':{'gemini-fixture':{'tokens':{'total':5}}},'tools':{'totalCalls':0}},'error':None}))\n",
                encoding="utf-8",
            )
            fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
            env = dict(os.environ)
            env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")
            result = subprocess.run(
                ["python3", str(CLI), "--data-dir", tmp, "runner", "matrix", "--study", "matrix-study", "--unit", "pair-1", "--options", "reflection,idle", "--index", "0", "--runtimes", "gemini", "--workspace", tmp, "--execute"],
                text=True, capture_output=True, check=False, env=env,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["executed"])
            self.assertEqual(payload["results"][0]["runtime"], "gemini")
            self.assertEqual(payload["results"][0]["choice"], "idle")
            self.assertNotIn("output", payload["results"][0]["run"])

    def test_runner_report_exposes_runtime_choice_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Empty-but-valid study should report no runtime observations.
            subprocess.run(
                ["python3", str(CLI), "--data-dir", tmp, "study", "init", "--id", "runner-study", "--conditions", "control,reflection", "--seed", "seed"],
                text=True,
                capture_output=True,
                check=True,
            )
            result = subprocess.run(
                ["python3", str(CLI), "--data-dir", tmp, "runner", "report", "--study", "runner-study"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["runtimes"], {})
