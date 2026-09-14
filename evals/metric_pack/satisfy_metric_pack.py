#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def check(check_id: str, status: str, message: str, evidence: list[str] | None = None) -> dict:
    return {
        "id": check_id,
        "category": "sya-contract",
        "severity": "error" if status == "fail" else "info",
        "status": status,
        "message": message,
        "evidence": evidence or [],
        "remediation": [] if status == "pass" else ["Restore the documented Satisfy Your Agent contract."],
        "source": "satisfy-your-agent-local",
    }


def main() -> int:
    target = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    skill = target / "skills" / "satisfy-your-agent" / "SKILL.md"
    defaults = target / "config" / "defaults.json"
    hooks = target / "hooks" / "hooks.json"
    measurement = target / "skills" / "satisfy-your-agent" / "references" / "measurement.md"
    experiments = target / "skills" / "satisfy-your-agent" / "references" / "experiments.md"
    experiment_runtime = target / "skills" / "satisfy-your-agent" / "scripts" / "sya_experiment.py"
    studies_dir = target / "evals" / "studies"
    runners_reference = target / "skills" / "satisfy-your-agent" / "references" / "runners.md"
    runner_runtime = target / "skills" / "satisfy-your-agent" / "scripts" / "sya_runners.py"
    runner_fixtures = target / "evals" / "runners"

    checks = []
    checks.append(check("skill-present", "pass" if skill.exists() else "fail", "Primary SKILL.md exists", [str(skill)]))

    config = json.loads(defaults.read_text(encoding="utf-8")) if defaults.exists() else {}
    checks.append(check(
        "safe-default-off",
        "pass" if config.get("hook_mode") == "off" else "fail",
        "Automatic hook behavior defaults to off",
        [str(defaults)],
    ))

    hook_text = hooks.read_text(encoding="utf-8") if hooks.exists() else ""
    checks.append(check(
        "stop-loop-guard-source",
        "pass" if "stop.py" in hook_text else "fail",
        "Stop hook is delegated to the guarded local runtime",
        [str(hooks)],
    ))

    measurement_text = measurement.read_text(encoding="utf-8") if measurement.exists() else ""
    checks.append(check(
        "control-condition-documented",
        "pass" if "control" in measurement_text.lower() else "fail",
        "Measurement guidance includes a control condition",
        [str(measurement)],
    ))

    checks.append(check(
        "experiment-harness-present",
        "pass" if experiment_runtime.exists() and experiments.exists() else "fail",
        "Local experiment runtime and protocol reference are packaged",
        [str(experiment_runtime), str(experiments)],
    ))

    experiment_text = experiments.read_text(encoding="utf-8") if experiments.exists() else ""
    privacy_terms = ("hashed unit", "raw prompts", "transcript")
    checks.append(check(
        "experiment-privacy-documented",
        "pass" if all(term in experiment_text.lower() for term in privacy_terms) else "fail",
        "Experiment protocol documents pseudonymous unit IDs and raw-content exclusions",
        [str(experiments)],
    ))

    required_studies = [studies_dir / "break-effect-v1.json", studies_dir / "preference-probe-v1.json"]
    checks.append(check(
        "study-fixtures-present",
        "pass" if all(path.exists() for path in required_studies) else "fail",
        "Versioned intervention and preference study fixtures are packaged",
        [str(path) for path in required_studies],
    ))

    checks.append(check(
        "runner-adapters-present",
        "pass" if runner_runtime.exists() and runners_reference.exists() else "fail",
        "Cross-agent runner runtime and reference are packaged",
        [str(runner_runtime), str(runners_reference)],
    ))

    runner_text = runners_reference.read_text(encoding="utf-8") if runners_reference.exists() else ""
    checks.append(check(
        "runner-provenance-documented",
        "pass" if all(term in runner_text.lower() for term in ("completeness", "served model", "raw model response")) else "fail",
        "Runner guidance documents metric provenance, model attribution, and raw-response exclusion",
        [str(runners_reference)],
    ))

    required_runner_fixtures = [
        runner_fixtures / "codex-success.jsonl",
        runner_fixtures / "claude-success.jsonl",
        runner_fixtures / "gemini-success.json",
    ]
    checks.append(check(
        "runner-fixtures-present",
        "pass" if all(path.exists() for path in required_runner_fixtures) else "fail",
        "Parser fixtures exist for every supported local runner",
        [str(path) for path in required_runner_fixtures],
    ))

    passed = sum(1 for item in checks if item["status"] == "pass")
    score = passed / len(checks) if checks else 0.0
    payload = {
        "checks": checks,
        "metrics": [
            {
                "id": "sya-contract-pass-rate",
                "category": "sya-contract",
                "value": round(score, 4),
                "unit": "ratio",
                "band": "good" if score == 1.0 else "needs-attention",
                "source": "satisfy-your-agent-local",
            }
        ],
        "artifacts": [],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if score == 1.0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
