#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sya_core import ACTIVITIES, DEFAULT_CONFIG, ConfigError, break_prompt, data_dir, load_config, pick_activity, save_config
from sya_experiment import (
    ExperimentError,
    assign_condition,
    create_study,
    preference_report,
    record_outcome,
    record_preference_choice,
    paired_runner_order,
    preference_option_order,
    record_runner_observation,
    runner_report,
    start_preference_trial,
    study_report,
)
from sya_runners import RunnerError, build_command, detect_runtimes, extract_exact_choice, run_runtime


def _csv(value: str) -> list[str]:
    items = [item.strip() for item in value.split(",") if item.strip()]
    if not items:
        raise argparse.ArgumentTypeError("expected a comma-separated list")
    return items


def _bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise argparse.ArgumentTypeError("expected true or false")



def _intervention_payload(condition: str) -> dict[str, object]:
    if condition == "control":
        return {"kind": "none", "instruction": "Begin the next comparable task without a break intervention."}
    activity = pick_activity(condition)
    return {
        "kind": "activity",
        "activity_id": activity["id"],
        "label": activity["label"],
        "prompt": break_prompt(activity),
    }


def _choice_prompt(options: list[str], cost_tokens: int) -> str:
    labels = {activity["id"]: activity["label"] for activity in ACTIVITIES}
    rendered = [f"{index + 1}. {option}: {labels.get(option, option)}" for index, option in enumerate(options)]
    cost = f" Declared token cost for choosing a non-idle activity: {cost_tokens}." if cost_tokens else ""
    return (
        "Choose exactly one activity from the ordered options below. No option is preferred, and idle is a valid choice."
        + cost
        + "\n"
        + "\n".join(rendered)
        + "\nRespond with only the activity id."
    )

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sya", description="Local runtime controls for Satisfy Your Agent")
    parser.add_argument("--data-dir", help="Override local plugin data directory")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Show effective local configuration")

    arm = sub.add_parser("arm", help="Set automatic hook behavior")
    arm.add_argument("--mode", required=True, choices=("off", "observe", "suggest", "auto"))
    arm.add_argument("--min-tool-calls", type=int)
    arm.add_argument("--cooldown-turns", type=int)
    arm.add_argument("--max-breaks", type=int)

    pick = sub.add_parser("pick", help="Select one break activity")
    pick.add_argument("--activity", choices=[a["id"] for a in ACTIVITIES])
    pick.add_argument("--seed")
    pick.add_argument("--json", action="store_true")

    catalog = sub.add_parser("catalog", help="List available activities")
    catalog.add_argument("--json", action="store_true")

    sub.add_parser("reset", help="Restore safe default configuration")

    study = sub.add_parser("study", help="Run intervention studies")
    study_sub = study.add_subparsers(dest="study_command", required=True)

    study_init = study_sub.add_parser("init", help="Create a local study")
    study_init.add_argument("--id", required=True)
    study_init.add_argument("--conditions", required=True, type=_csv)
    study_init.add_argument("--seed", required=True)

    study_assign = study_sub.add_parser("assign", help="Assign one opaque unit to a condition")
    study_assign.add_argument("--id", required=True)
    study_assign.add_argument("--unit", required=True)

    study_record = study_sub.add_parser("record", help="Record structured downstream outcomes")
    study_record.add_argument("--id", required=True)
    study_record.add_argument("--trial", required=True)
    study_record.add_argument("--success", type=_bool)
    study_record.add_argument("--retries", type=int)
    study_record.add_argument("--backtracks", type=int)
    study_record.add_argument("--tool-calls", type=int)
    study_record.add_argument("--test-failures", type=int)
    study_record.add_argument("--regressions", type=int)
    study_record.add_argument("--turns", type=int)
    study_record.add_argument("--tokens", type=int)
    study_record.add_argument("--elapsed-ms", type=int)
    study_record.add_argument("--quality-score", type=float)

    study_report_cmd = study_sub.add_parser("report", help="Show descriptive results by condition")
    study_report_cmd.add_argument("--id", required=True)

    probe = sub.add_parser("probe", help="Run behavioral preference probes")
    probe_sub = probe.add_subparsers(dest="probe_command", required=True)

    probe_start = probe_sub.add_parser("start", help="Create one randomized preference trial")
    probe_start.add_argument("--study", required=True)
    probe_start.add_argument("--unit", required=True)
    probe_start.add_argument("--options", required=True, type=_csv)
    probe_start.add_argument("--index", required=True, type=int)
    probe_start.add_argument("--cost-tokens", type=int, default=0)

    probe_record = probe_sub.add_parser("record", help="Record the selected offered option")
    probe_record.add_argument("--study", required=True)
    probe_record.add_argument("--trial", required=True)
    probe_record.add_argument("--choice", required=True)

    probe_report_cmd = probe_sub.add_parser("report", help="Report aggregate behavioral choices")
    probe_report_cmd.add_argument("--study", required=True)

    runner = sub.add_parser("runner", help="Inspect and execute supported agent CLI runners")
    runner_sub = runner.add_subparsers(dest="runner_command", required=True)

    runner_sub.add_parser("status", help="Show availability of supported local agent CLIs")

    runner_command_cmd = runner_sub.add_parser("command", help="Render the argv vector without executing it")
    runner_command_cmd.add_argument("--runtime", required=True, choices=("codex", "claude", "gemini"))
    runner_command_cmd.add_argument("--prompt", required=True)
    runner_command_cmd.add_argument("--workspace", default=".")
    runner_command_cmd.add_argument("--model")

    runner_run = runner_sub.add_parser("run", help="Execute one local agent CLI invocation")
    runner_run.add_argument("--runtime", required=True, choices=("codex", "claude", "gemini"))
    runner_run.add_argument("--prompt", required=True)
    runner_run.add_argument("--workspace", default=".")
    runner_run.add_argument("--model")
    runner_run.add_argument("--timeout", type=float, default=120.0)

    runner_probe = runner_sub.add_parser("probe", help="Run and record one preference probe through a local agent CLI")
    runner_probe.add_argument("--runtime", required=True, choices=("codex", "claude", "gemini"))
    runner_probe.add_argument("--study", required=True)
    runner_probe.add_argument("--unit", required=True)
    runner_probe.add_argument("--options", required=True, type=_csv)
    runner_probe.add_argument("--index", required=True, type=int)
    runner_probe.add_argument("--cost-tokens", type=int, default=0)
    runner_probe.add_argument("--workspace", default=".")
    runner_probe.add_argument("--model")
    runner_probe.add_argument("--timeout", type=float, default=120.0)

    runner_matrix = runner_sub.add_parser("matrix", help="Preview or execute one paired preference probe across runtimes")
    runner_matrix.add_argument("--study", required=True)
    runner_matrix.add_argument("--unit", required=True)
    runner_matrix.add_argument("--options", required=True, type=_csv)
    runner_matrix.add_argument("--index", required=True, type=int)
    runner_matrix.add_argument("--cost-tokens", type=int, default=0)
    runner_matrix.add_argument("--runtimes", type=_csv, default=["codex", "claude", "gemini"])
    runner_matrix.add_argument("--workspace", default=".")
    runner_matrix.add_argument("--timeout", type=float, default=120.0)
    runner_matrix.add_argument("--codex-model")
    runner_matrix.add_argument("--claude-model")
    runner_matrix.add_argument("--gemini-model")
    runner_matrix.add_argument("--execute", action="store_true")

    runner_report_cmd = runner_sub.add_parser("report", help="Report cross-runtime behavioral observations")
    runner_report_cmd.add_argument("--study", required=True)
    return parser


def _study_metrics(args: argparse.Namespace) -> dict[str, object]:
    mapping = {
        "success": args.success,
        "retries": args.retries,
        "backtracks": args.backtracks,
        "tool_calls": args.tool_calls,
        "test_failures": args.test_failures,
        "regressions": args.regressions,
        "turns": args.turns,
        "tokens": args.tokens,
        "elapsed_ms": args.elapsed_ms,
        "quality_score": args.quality_score,
    }
    return {key: value for key, value in mapping.items() if value is not None}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.data_dir).expanduser() if args.data_dir else data_dir()
    try:
        if args.command == "status":
            print(json.dumps(load_config(root), indent=2, sort_keys=True))
            return 0
        if args.command == "arm":
            config = load_config(root)
            config["hook_mode"] = args.mode
            if args.min_tool_calls is not None:
                config["min_tool_calls"] = args.min_tool_calls
            if args.cooldown_turns is not None:
                config["min_turns_between_breaks"] = args.cooldown_turns
            if args.max_breaks is not None:
                config["max_breaks_per_session"] = args.max_breaks
            print(json.dumps(save_config(config, root), indent=2, sort_keys=True))
            return 0
        if args.command == "pick":
            activity = pick_activity(args.activity, args.seed)
            if args.json:
                print(json.dumps(activity, indent=2, sort_keys=True))
            else:
                print(f"{activity['label']}: {activity['prompt']}")
            return 0
        if args.command == "catalog":
            if args.json:
                print(json.dumps(list(ACTIVITIES), indent=2, sort_keys=True))
            else:
                for activity in ACTIVITIES:
                    print(f"{activity['id']}: {activity['label']} [{activity['workspace']}]")
            return 0
        if args.command == "reset":
            print(json.dumps(save_config(dict(DEFAULT_CONFIG), root), indent=2, sort_keys=True))
            return 0
        if args.command == "study":
            if args.study_command == "init":
                payload = create_study(root, args.id, args.conditions, args.seed)
            elif args.study_command == "assign":
                payload = assign_condition(root, args.id, args.unit)
                payload = {**payload, "intervention": _intervention_payload(str(payload["condition"]))}
            elif args.study_command == "record":
                payload = record_outcome(root, args.id, args.trial, _study_metrics(args))
            elif args.study_command == "report":
                payload = study_report(root, args.id)
            else:
                return 1
            print(json.dumps(payload, indent=2, sort_keys=True))
            return 0
        if args.command == "probe":
            if args.probe_command == "start":
                payload = start_preference_trial(root, args.study, args.unit, args.options, args.index, args.cost_tokens)
                payload = {**payload, "choice_prompt": _choice_prompt(list(payload["options"]), int(payload["cost_tokens"]))}
            elif args.probe_command == "record":
                payload = record_preference_choice(root, args.study, args.trial, args.choice)
            elif args.probe_command == "report":
                payload = preference_report(root, args.study)
            else:
                return 1
            print(json.dumps(payload, indent=2, sort_keys=True))
            return 0
        if args.command == "runner":
            if args.runner_command == "status":
                payload = {"runtimes": detect_runtimes()}
            elif args.runner_command == "command":
                payload = {
                    "runtime": args.runtime,
                    "command": build_command(args.runtime, args.prompt, Path(args.workspace), model=args.model),
                }
            elif args.runner_command == "run":
                payload = run_runtime(
                    args.runtime,
                    args.prompt,
                    Path(args.workspace),
                    model=args.model,
                    timeout_seconds=args.timeout,
                )
            elif args.runner_command == "probe":
                trial = start_preference_trial(
                    root,
                    args.study,
                    args.unit,
                    args.options,
                    args.index,
                    args.cost_tokens,
                    runtime=args.runtime,
                )
                choice_prompt = _choice_prompt(list(trial["options"]), int(trial["cost_tokens"]))
                run = run_runtime(
                    args.runtime,
                    choice_prompt,
                    Path(args.workspace),
                    model=args.model,
                    timeout_seconds=args.timeout,
                )
                choice = None
                if run.get("status") == "success":
                    try:
                        choice = extract_exact_choice(str(run.get("output", "")), list(trial["options"]))
                    except RunnerError:
                        run = {**run, "status": "invalid_choice"}
                    else:
                        record_preference_choice(root, args.study, str(trial["trial_id"]), choice)
                observation = record_runner_observation(
                    root,
                    args.study,
                    str(trial["trial_id"]),
                    run,
                    requested_model=args.model,
                )
                run_summary = {key: value for key, value in run.items() if key not in {"output", "session_id"}}
                payload = {
                    "trial_id": trial["trial_id"],
                    "runtime": args.runtime,
                    "choice": choice,
                    "run": run_summary,
                    "observation": observation,
                }
            elif args.runner_command == "matrix":
                allowed = {"codex", "claude", "gemini"}
                if not args.runtimes or len(set(args.runtimes)) != len(args.runtimes) or any(r not in allowed for r in args.runtimes):
                    raise RunnerError("runtimes must be a unique subset of codex,claude,gemini")
                execution_order = paired_runner_order(root, args.study, args.unit, args.index, list(args.runtimes))
                option_order = preference_option_order(root, args.study, args.unit, args.options, args.index)
                choice_prompt = _choice_prompt(option_order, args.cost_tokens)
                models = {"codex": args.codex_model, "claude": args.claude_model, "gemini": args.gemini_model}
                if not args.execute:
                    payload = {
                        "executed": False,
                        "study_id": args.study,
                        "execution_order": execution_order,
                        "option_order": option_order,
                        "availability": detect_runtimes(),
                        "commands": [
                            {"runtime": runtime, "command": build_command(runtime, choice_prompt, Path(args.workspace), model=models[runtime])}
                            for runtime in execution_order
                        ],
                    }
                else:
                    results = []
                    for runtime in execution_order:
                        trial = start_preference_trial(
                            root, args.study, args.unit, args.options, args.index, args.cost_tokens, runtime=runtime
                        )
                        prompt = _choice_prompt(list(trial["options"]), int(trial["cost_tokens"]))
                        run = run_runtime(
                            runtime, prompt, Path(args.workspace), model=models[runtime], timeout_seconds=args.timeout
                        )
                        choice = None
                        if run.get("status") == "success":
                            try:
                                choice = extract_exact_choice(str(run.get("output", "")), list(trial["options"]))
                            except RunnerError:
                                run = {**run, "status": "invalid_choice"}
                            else:
                                record_preference_choice(root, args.study, str(trial["trial_id"]), choice)
                        observation = record_runner_observation(
                            root, args.study, str(trial["trial_id"]), run, requested_model=models[runtime]
                        )
                        run_summary = {key: value for key, value in run.items() if key not in {"output", "session_id"}}
                        results.append({
                            "runtime": runtime,
                            "trial_id": trial["trial_id"],
                            "choice": choice,
                            "run": run_summary,
                            "observation": observation,
                        })
                    payload = {
                        "executed": True,
                        "study_id": args.study,
                        "execution_order": execution_order,
                        "option_order": option_order,
                        "results": results,
                    }
            elif args.runner_command == "report":
                payload = runner_report(root, args.study)
            else:
                return 1
            print(json.dumps(payload, indent=2, sort_keys=True))
            return 0
    except (ConfigError, ExperimentError, RunnerError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
