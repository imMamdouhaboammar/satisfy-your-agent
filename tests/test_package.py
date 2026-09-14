from __future__ import annotations

import json
import re
import unittest
import xml.etree.ElementTree as ET
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
            if path.is_file() and path.suffix in {".md", ".py", ".json", ".yaml", ".yml", ".toml"}:
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


class V03PackageTests(unittest.TestCase):
    def test_manifest_keeps_v03_contract_or_later(self):
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        version = tuple(int(part) for part in manifest["version"].split("."))
        self.assertGreaterEqual(version, (0, 3, 0))

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


class BrandingAndDistributionTests(unittest.TestCase):
    def test_logo_is_valid_svg_and_manifest_points_to_it(self):
        logo = ROOT / "assets" / "logo.svg"
        self.assertTrue(logo.exists())
        ET.parse(logo)
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        interface = manifest["interface"]
        self.assertEqual(interface["logo"], "./assets/logo.svg")
        self.assertEqual(interface["composerIcon"], "./assets/logo.svg")

    def test_repo_marketplace_points_at_plugin_root(self):
        marketplace = json.loads((ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(marketplace["name"], "satisfy-your-agent")
        plugin = marketplace["plugins"][0]
        self.assertEqual(plugin["name"], "satisfy-your-agent")
        self.assertEqual(plugin["source"], {"source": "local", "path": "./"})
        self.assertEqual(plugin["policy"]["installation"], "AVAILABLE")

    def test_readme_documents_marketplace_install_and_logo(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("./assets/logo.svg", readme)
        self.assertIn("codex plugin marketplace add imMamdouhaboammar/satisfy-your-agent --ref main", readme)


class V04DistributionTests(unittest.TestCase):
    def test_manifest_keeps_v04_contract_or_later(self):
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        version = tuple(int(part) for part in manifest["version"].split("."))
        self.assertGreaterEqual(version, (0, 4, 0))
        self.assertIn("homepage", manifest)

    def test_package_json_has_bin_entry(self):
        pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(pkg["name"], "satisfy-your-agent")
        self.assertIn("satisfy-your-agent", pkg["bin"])
        self.assertIn("sya", pkg["bin"])
        self.assertEqual(pkg["license"], "MIT")

    def test_skills_json_is_valid(self):
        skills = json.loads((ROOT / ".skills.json").read_text(encoding="utf-8"))
        self.assertEqual(skills["name"], "satisfy-your-agent")
        self.assertIn("skills/satisfy-your-agent/SKILL.md", skills["skill"])
        self.assertIsInstance(skills["tags"], list)

    def test_root_marketplace_json_has_required_fields(self):
        mkt = json.loads((ROOT / "marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(mkt["name"], "satisfy-your-agent")
        self.assertIn("compatibility", mkt)
        self.assertIn("claudeCode", mkt["compatibility"])
        self.assertIn("codex", mkt["compatibility"])
        self.assertIn("antigravity", mkt["compatibility"])
        self.assertEqual(mkt["entrypoint"], "skills/satisfy-your-agent/SKILL.md")

    def test_install_sh_is_executable_and_targets_all_agents(self):
        install = ROOT / "install.sh"
        self.assertTrue(install.exists())
        content = install.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("#!/usr/bin/env bash"))
        self.assertIn(".claude/skills", content)
        self.assertIn(".gemini/config/skills", content)
        self.assertIn(".codex/skills", content)
        self.assertIn(".cursor/skills", content)
        self.assertIn(".agents/skills", content)

    def test_bin_cli_js_exists(self):
        cli = ROOT / "bin" / "cli.js"
        self.assertTrue(cli.exists())
        content = cli.read_text(encoding="utf-8")
        self.assertIn("sya.py", content)

    def test_skill_description_has_discovery_clause_and_negatives(self):
        text = (ROOT / "skills" / "satisfy-your-agent" / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("even if they do not explicitly say", text)
        self.assertIn("do not use for", text)

    def test_runtime_requirements_keep_manual_break_lightweight(self):
        text = (ROOT / "skills" / "satisfy-your-agent" / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("runtime requirements", text)
        self.assertIn("manual experience commands do not require python", text)
        self.assertIn("python3", text)

    def test_contributing_and_security_exist(self):
        self.assertTrue((ROOT / "CONTRIBUTING.md").exists())
        self.assertTrue((ROOT / "SECURITY.md").exists())
        contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        self.assertIn("verify.py", contributing)
        security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
        self.assertIn("install.sh", security)


class V05CommandSurfaceTests(unittest.TestCase):
    def test_release_version_is_0_5_0_everywhere(self):
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        skills = json.loads((ROOT / ".skills.json").read_text(encoding="utf-8"))
        marketplace = json.loads((ROOT / "marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual({manifest["version"], pkg["version"], skills["version"], marketplace["version"]}, {"0.5.0"})

    def test_npm_package_includes_command_adapters(self):
        pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        self.assertIn("adapters", pkg["files"])
        self.assertIn("slash-commands", pkg["keywords"])

    def test_commands_reference_is_packaged(self):
        self.assertTrue((ROOT / "skills" / "satisfy-your-agent" / "references" / "commands.md").exists())
        self.assertTrue((ROOT / "config" / "commands.json").exists())

    def test_gemini_command_adapter_directory_is_packaged(self):
        command_dir = ROOT / "adapters" / "gemini" / "commands" / "sya"
        self.assertTrue(command_dir.is_dir())
        self.assertGreaterEqual(len(list(command_dir.glob("*.toml"))), 12)


if __name__ == "__main__":
    unittest.main()
