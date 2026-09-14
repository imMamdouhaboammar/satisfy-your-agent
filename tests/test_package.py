from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def test_manifest_shape(self):
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "satisfy-your-agent")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual(manifest["hooks"], "./hooks/hooks.json")

    def test_only_manifest_inside_codex_plugin_directory(self):
        names = sorted(p.name for p in (ROOT / ".codex-plugin").iterdir())
        self.assertEqual(names, ["plugin.json"])

    def test_skill_frontmatter_name_matches_slug(self):
        text = (ROOT / "skills" / "satisfy-your-agent" / "SKILL.md").read_text(encoding="utf-8")
        match = re.search(r"^name:\s*([^\n]+)$", text, re.MULTILINE)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1).strip(), "satisfy-your-agent")

    def test_no_em_dash_character_in_package_text(self):
        bad = []
        for path in ROOT.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".py", ".json", ".yaml", ".yml"}:
                if chr(0x2014) in path.read_text(encoding="utf-8"):
                    bad.append(str(path.relative_to(ROOT)))
        self.assertEqual(bad, [])

    def test_packaged_defaults_match_runtime_defaults(self):
        defaults = json.loads((ROOT / "config" / "defaults.json").read_text(encoding="utf-8"))
        core_path = ROOT / "skills" / "satisfy-your-agent" / "scripts" / "sya_core.py"
        namespace = {}
        exec(compile(core_path.read_text(encoding="utf-8"), str(core_path), "exec"), namespace)
        self.assertEqual(defaults, namespace["DEFAULT_CONFIG"])

    def test_metric_pack_manifest_uses_current_contract_shape(self):
        manifest = json.loads((ROOT / "evals" / "metric_pack" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(set(manifest), {"name", "version", "supportedTargetKinds", "command"})
        self.assertIn("plugin", manifest["supportedTargetKinds"])
        self.assertNotIn("{target}", manifest["command"])


class V02PackageTests(unittest.TestCase):
    def test_manifest_keeps_v02_contract_or_later(self):
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        version = tuple(int(part) for part in manifest["version"].split("."))
        self.assertGreaterEqual(version, (0, 2, 0))

    def test_experiment_runtime_and_reference_are_packaged(self):
        self.assertTrue((ROOT / "skills" / "satisfy-your-agent" / "scripts" / "sya_experiment.py").exists())
        self.assertTrue((ROOT / "skills" / "satisfy-your-agent" / "references" / "experiments.md").exists())

    def test_study_fixtures_exist_and_are_valid_json(self):
        for name in ("break-effect-v1.json", "preference-probe-v1.json"):
            path = ROOT / "evals" / "studies" / name
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], 1)
    def test_metric_pack_covers_v02_experiment_contract(self):
        script = (ROOT / "evals" / "metric_pack" / "satisfy_metric_pack.py").read_text(encoding="utf-8")
        self.assertIn("experiment-harness-present", script)
        self.assertIn("experiment-privacy-documented", script)
        self.assertIn("study-fixtures-present", script)

    def test_research_discovery_and_behavior_evals_are_present(self):
        discovery = json.loads((ROOT / "evals" / "discovery_prompts.json").read_text(encoding="utf-8"))
        joined = " ".join(discovery["direct"] + discovery["indirect"]).lower()
        self.assertIn("preference", joined)
        self.assertIn("control", joined)
        behavior = json.loads((ROOT / "evals" / "behavior_scenarios.json").read_text(encoding="utf-8"))
        ids = {item["id"] for item in behavior["scenarios"]}
        self.assertIn("local-experiment-harness", ids)
        self.assertIn("preference-probe-neutrality", ids)



if __name__ == "__main__":
    unittest.main()

class V03PackageTests(unittest.TestCase):
    def test_manifest_version_is_0_3_0(self):
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "0.3.0")

    def test_runner_runtime_and_reference_are_packaged(self):
        self.assertTrue((ROOT / "skills" / "satisfy-your-agent" / "scripts" / "sya_runners.py").exists())
        self.assertTrue((ROOT / "skills" / "satisfy-your-agent" / "references" / "runners.md").exists())

    def test_runner_fixtures_cover_all_supported_runtimes(self):
        fixture_dir = ROOT / "evals" / "runners"
        names = {p.name for p in fixture_dir.glob("*.json*")}
        self.assertIn("codex-success.jsonl", names)
        self.assertIn("claude-success.jsonl", names)
        self.assertIn("gemini-success.json", names)

    def test_metric_pack_covers_v03_runner_contract(self):
        script = (ROOT / "evals" / "metric_pack" / "satisfy_metric_pack.py").read_text(encoding="utf-8")
        self.assertIn("runner-adapters-present", script)
        self.assertIn("runner-provenance-documented", script)
        self.assertIn("runner-fixtures-present", script)

    def test_cross_runtime_behavior_eval_is_present(self):
        behavior = json.loads((ROOT / "evals" / "behavior_scenarios.json").read_text(encoding="utf-8"))
        ids = {item["id"] for item in behavior["scenarios"]}
        self.assertIn("cross-runtime-provenance", ids)
