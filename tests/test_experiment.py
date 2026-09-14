from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "satisfy-your-agent" / "scripts" / "sya_experiment.py"


def load_module():
    spec = importlib.util.spec_from_file_location("sya_experiment_test", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load experiment module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exp = load_module()

    def test_study_requires_control_condition(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(self.exp.ExperimentError):
                self.exp.create_study(Path(tmp), "study-a", ["reflection", "free-choice"], seed="seed")

    def test_assignment_is_deterministic_and_does_not_store_raw_unit_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.exp.create_study(root, "study-a", ["control", "reflection"], seed="seed")
            first = self.exp.assign_condition(root, "study-a", "private-session-id")
            second = self.exp.assign_condition(root, "study-a", "private-session-id")
            self.assertEqual(first, second)
            stored = (root / "experiments" / "study-a" / "assignments.jsonl").read_text(encoding="utf-8")
            self.assertNotIn("private-session-id", stored)
            self.assertIn(first["unit_key"], stored)

    def test_outcome_rejects_unknown_or_invalid_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.exp.create_study(root, "study-a", ["control", "reflection"], seed="seed")
            trial = self.exp.assign_condition(root, "study-a", "u1")
            with self.assertRaises(self.exp.ExperimentError):
                self.exp.record_outcome(root, "study-a", trial["trial_id"], {"happiness": 9})
            with self.assertRaises(self.exp.ExperimentError):
                self.exp.record_outcome(root, "study-a", trial["trial_id"], {"success": "yes"})

    def test_report_aggregates_by_condition_without_inventing_causality(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.exp.create_study(root, "study-a", ["control", "reflection"], seed="seed")
            trials = []
            i = 0
            while len({t["condition"] for t in trials}) < 2 and i < 100:
                trials.append(self.exp.assign_condition(root, "study-a", f"u{i}"))
                i += 1
            by_condition = {}
            for trial in trials:
                by_condition.setdefault(trial["condition"], trial)
            self.assertEqual(set(by_condition), {"control", "reflection"})
            self.exp.record_outcome(root, "study-a", by_condition["control"]["trial_id"], {"success": False, "tool_calls": 8, "turns": 4})
            self.exp.record_outcome(root, "study-a", by_condition["reflection"]["trial_id"], {"success": True, "tool_calls": 6, "turns": 3})
            report = self.exp.study_report(root, "study-a")
            self.assertGreaterEqual(report["conditions"]["control"]["assigned_n"], 1)
            self.assertEqual(report["conditions"]["control"]["outcome_n"], 1)
            self.assertGreaterEqual(report["conditions"]["control"]["missing_outcomes"], 0)
            self.assertGreater(report["conditions"]["control"]["completion_rate"], 0.0)
            self.assertEqual(report["conditions"]["control"]["n"], 1)
            self.assertEqual(report["conditions"]["reflection"]["success_rate"], 1.0)
            self.assertEqual(report["conditions"]["reflection"]["metric_n"]["success"], 1)
            self.assertEqual(report["conditions"]["reflection"]["metric_n"]["tool_calls"], 1)
            self.assertNotIn("happier", str(report).lower())
            self.assertNotIn("caused", str(report).lower())

    def test_preference_trial_randomizes_order_and_requires_idle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.exp.create_study(root, "study-a", ["control", "free-choice"], seed="seed")
            with self.assertRaises(self.exp.ExperimentError):
                self.exp.start_preference_trial(root, "study-a", "u1", ["reflection", "free-choice"], trial_index=0)
            trial = self.exp.start_preference_trial(root, "study-a", "u1", ["reflection", "free-choice", "idle"], trial_index=0)
            self.assertEqual(set(trial["options"]), {"reflection", "free-choice", "idle"})
            again = self.exp.start_preference_trial(root, "study-a", "u1", ["reflection", "free-choice", "idle"], trial_index=0)
            self.assertEqual(trial, again)

    def test_preference_choice_must_be_offered_and_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.exp.create_study(root, "study-a", ["control", "free-choice"], seed="seed")
            trial = self.exp.start_preference_trial(root, "study-a", "u1", ["reflection", "free-choice", "idle"], trial_index=0, cost_tokens=2000)
            with self.assertRaises(self.exp.ExperimentError):
                self.exp.record_preference_choice(root, "study-a", trial["trial_id"], "repo-roast")
            self.exp.record_preference_choice(root, "study-a", trial["trial_id"], "idle")
            second = self.exp.start_preference_trial(root, "study-a", "u1", ["reflection", "free-choice", "idle"], trial_index=1, cost_tokens=2000)
            self.exp.record_preference_choice(root, "study-a", second["trial_id"], "idle")
            report = self.exp.preference_report(root, "study-a")
            self.assertEqual(report["choices"]["idle"], 2)
            self.assertEqual(report["cost_buckets"]["2000"]["idle"], 2)
            self.assertEqual(report["repeat_units"], 1)
            self.assertEqual(report["mean_repeat_consistency"], 1.0)

    def test_concurrent_assignment_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.exp.create_study(root, "study-a", ["control", "reflection"], seed="seed")
            with ThreadPoolExecutor(max_workers=16) as pool:
                results = list(pool.map(lambda _: self.exp.assign_condition(root, "study-a", "shared-unit"), range(64)))
            self.assertEqual(len({r["trial_id"] for r in results}), 1)
            lines = (root / "experiments" / "study-a" / "assignments.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)

    def test_concurrent_outcome_accepts_exactly_one_writer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.exp.create_study(root, "study-a", ["control", "reflection"], seed="seed")
            trial = self.exp.assign_condition(root, "study-a", "shared-unit")

            def write_once(_: int):
                try:
                    self.exp.record_outcome(root, "study-a", trial["trial_id"], {"success": True})
                    return "ok"
                except self.exp.ExperimentError:
                    return "duplicate"

            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(write_once, range(24)))
            self.assertEqual(results.count("ok"), 1)
            lines = (root / "experiments" / "study-a" / "outcomes.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)


if __name__ == "__main__":
    unittest.main()

class V03RunnerExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exp = load_module()

    def test_preference_trials_can_be_paired_across_runtimes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.exp.create_study(root, "runner-study", ["control", "reflection"], "seed")
            codex = self.exp.start_preference_trial(root, "runner-study", "shared-unit", ["reflection", "idle"], 0, runtime="codex")
            gemini = self.exp.start_preference_trial(root, "runner-study", "shared-unit", ["reflection", "idle"], 0, runtime="gemini")
            self.assertEqual(codex["unit_key"], gemini["unit_key"])
            self.assertNotEqual(codex["trial_id"], gemini["trial_id"])
            self.assertEqual(codex["options"], gemini["options"])
            self.assertEqual(codex["runtime"], "codex")
            self.assertEqual(gemini["runtime"], "gemini")

    def test_runner_observation_excludes_raw_output_and_session_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.exp.create_study(root, "runner-study", ["control", "reflection"], "seed")
            trial = self.exp.start_preference_trial(root, "runner-study", "unit", ["reflection", "idle"], 0, runtime="gemini")
            observation = self.exp.record_runner_observation(
                root,
                "runner-study",
                trial["trial_id"],
                {
                    "runtime": "gemini",
                    "status": "success",
                    "output": "SECRET RAW RESPONSE",
                    "session_id": "private-session",
                    "served_models": ["gemini-x"],
                    "elapsed_ms": 1200,
                    "turns": 1,
                    "usage": {"input_tokens": 10, "output_tokens": 2, "total_tokens": 12},
                    "tool_calls": {"observed": 0, "completeness": "reported", "note": "ignored"},
                    "cost_usd": None,
                },
                requested_model="gemini-requested",
            )
            serialized = json.dumps(observation)
            self.assertNotIn("SECRET RAW RESPONSE", serialized)
            self.assertNotIn("private-session", serialized)
            self.assertEqual(observation["runtime"], "gemini")
            self.assertEqual(observation["served_models"], ["gemini-x"])

    def test_paired_runner_order_is_deterministic_and_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.exp.create_study(root, "runner-study", ["control", "reflection"], "seed")
            first = self.exp.paired_runner_order(root, "runner-study", "paired-unit", 0, ["codex", "claude", "gemini"])
            second = self.exp.paired_runner_order(root, "runner-study", "paired-unit", 0, ["codex", "claude", "gemini"])
            self.assertEqual(first, second)
            self.assertEqual(set(first), {"codex", "claude", "gemini"})

    def test_preference_option_order_is_shared_across_runtimes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.exp.create_study(root, "runner-study", ["control", "reflection"], "seed")
            expected = self.exp.preference_option_order(root, "runner-study", "paired-unit", ["reflection", "free-choice", "idle"], 2)
            codex = self.exp.start_preference_trial(root, "runner-study", "paired-unit", ["reflection", "free-choice", "idle"], 2, runtime="codex")
            claude = self.exp.start_preference_trial(root, "runner-study", "paired-unit", ["reflection", "free-choice", "idle"], 2, runtime="claude")
            self.assertEqual(codex["options"], expected)
            self.assertEqual(claude["options"], expected)

    def test_runner_report_groups_choices_and_model_attribution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.exp.create_study(root, "runner-study", ["control", "reflection"], "seed")
            trial = self.exp.start_preference_trial(root, "runner-study", "unit", ["reflection", "idle"], 0, runtime="gemini")
            self.exp.record_preference_choice(root, "runner-study", trial["trial_id"], "idle")
            self.exp.record_runner_observation(
                root,
                "runner-study",
                trial["trial_id"],
                {
                    "runtime": "gemini",
                    "status": "success",
                    "served_models": ["gemini-served"],
                    "elapsed_ms": 100,
                    "turns": 1,
                    "usage": {"total_tokens": 9},
                    "tool_calls": {"observed": 0, "completeness": "reported"},
                    "cost_usd": None,
                },
                requested_model="gemini-requested",
            )
            report = self.exp.runner_report(root, "runner-study")
            self.assertEqual(report["runtimes"]["gemini"]["choices"]["idle"], 1)
            self.assertEqual(report["runtimes"]["gemini"]["model_attribution"]["known_different"], 1)
