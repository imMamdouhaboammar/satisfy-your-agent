from __future__ import annotations

import hashlib
import json
import os
import random
import re
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any

STUDY_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
CONDITION_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")

OUTCOME_FIELDS: dict[str, tuple[type, float | None, float | None]] = {
    "success": (bool, None, None),
    "retries": (int, 0, None),
    "backtracks": (int, 0, None),
    "tool_calls": (int, 0, None),
    "test_failures": (int, 0, None),
    "regressions": (int, 0, None),
    "turns": (int, 0, None),
    "tokens": (int, 0, None),
    "elapsed_ms": (int, 0, None),
    "quality_score": (float, 0, 1),
}


class ExperimentError(ValueError):
    pass


@contextmanager
def _exclusive_lock(directory: Path, name: str = ".study-write.lock", timeout_seconds: float = 5.0):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    deadline = time.monotonic() + timeout_seconds
    fd: int | None = None
    while fd is None:
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.write(fd, str(os.getpid()).encode("ascii", errors="ignore"))
        except FileExistsError:
            try:
                age = time.time() - path.stat().st_mtime
                if age > 30:
                    path.unlink(missing_ok=True)
                    continue
            except FileNotFoundError:
                continue
            if time.monotonic() >= deadline:
                raise ExperimentError("timed out waiting for local study write lock")
            time.sleep(0.01)
    try:
        yield
    finally:
        try:
            os.close(fd)
        finally:
            path.unlink(missing_ok=True)


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            value = json.loads(line)
            if isinstance(value, dict):
                records.append(value)
    return records


def _study_dir(root: Path, study_id: str) -> Path:
    _validate_study_id(study_id)
    return root / "experiments" / study_id


def _validate_study_id(study_id: str) -> None:
    if not STUDY_ID_RE.fullmatch(study_id):
        raise ExperimentError("study_id must be kebab-case, 1 to 64 characters")


def _validate_conditions(conditions: list[str]) -> list[str]:
    if len(conditions) < 2:
        raise ExperimentError("a study requires at least two conditions")
    if len(set(conditions)) != len(conditions):
        raise ExperimentError("condition ids must be unique")
    for condition in conditions:
        if not CONDITION_ID_RE.fullmatch(condition):
            raise ExperimentError(f"invalid condition id: {condition}")
    if "control" not in conditions:
        raise ExperimentError("a study requires a control condition")
    return conditions


def _unit_key(unit_id: str) -> str:
    if not unit_id:
        raise ExperimentError("unit_id must not be empty")
    return hashlib.sha256(unit_id.encode("utf-8")).hexdigest()[:24]


def _trial_id(study_id: str, unit_key: str, suffix: str = "assignment") -> str:
    raw = f"{study_id}:{unit_key}:{suffix}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def create_study(root: Path, study_id: str, conditions: list[str], seed: str) -> dict[str, Any]:
    _validate_study_id(study_id)
    conditions = _validate_conditions(list(conditions))
    if not seed:
        raise ExperimentError("seed must not be empty")
    directory = _study_dir(root, study_id)
    spec_path = directory / "study.json"
    if spec_path.exists():
        raise ExperimentError(f"study already exists: {study_id}")
    spec = {
        "schema_version": 1,
        "study_id": study_id,
        "conditions": conditions,
        "randomization": "deterministic-hash",
        "seed": seed,
        "outcome_fields": sorted(OUTCOME_FIELDS),
        "interpretation": "behavioral-outcomes-only",
    }
    _atomic_write_json(spec_path, spec)
    return spec


def load_study(root: Path, study_id: str) -> dict[str, Any]:
    path = _study_dir(root, study_id) / "study.json"
    if not path.exists():
        raise ExperimentError(f"unknown study: {study_id}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ExperimentError("study.json must contain an object")
    _validate_conditions(list(value.get("conditions") or []))
    if not isinstance(value.get("seed"), str) or not value["seed"]:
        raise ExperimentError("study seed is invalid")
    return value


def assign_condition(root: Path, study_id: str, unit_id: str) -> dict[str, Any]:
    study = load_study(root, study_id)
    unit_key = _unit_key(unit_id)
    directory = _study_dir(root, study_id)
    assignments_path = directory / "assignments.jsonl"
    with _exclusive_lock(directory):
        for record in _read_jsonl(assignments_path):
            if record.get("unit_key") == unit_key:
                return record
        digest = hashlib.sha256(f"{study['seed']}:{unit_key}".encode("utf-8")).digest()
        conditions = list(study["conditions"])
        condition = conditions[int.from_bytes(digest[:8], "big") % len(conditions)]
        record = {
            "schema_version": 1,
            "trial_id": _trial_id(study_id, unit_key),
            "unit_key": unit_key,
            "condition": condition,
        }
        _append_jsonl(assignments_path, record)
        return record


def _assignment_by_trial(root: Path, study_id: str, trial_id: str) -> dict[str, Any]:
    for record in _read_jsonl(_study_dir(root, study_id) / "assignments.jsonl"):
        if record.get("trial_id") == trial_id:
            return record
    raise ExperimentError(f"unknown assignment trial_id: {trial_id}")


def _validate_outcome(metrics: dict[str, Any]) -> dict[str, Any]:
    if not metrics:
        raise ExperimentError("at least one outcome metric is required")
    unknown = sorted(set(metrics) - set(OUTCOME_FIELDS))
    if unknown:
        raise ExperimentError(f"unknown outcome metrics: {', '.join(unknown)}")
    validated: dict[str, Any] = {}
    for name, value in metrics.items():
        expected, minimum, maximum = OUTCOME_FIELDS[name]
        if expected is bool:
            if not isinstance(value, bool):
                raise ExperimentError(f"{name} must be boolean")
        elif expected is int:
            if not isinstance(value, int) or isinstance(value, bool):
                raise ExperimentError(f"{name} must be an integer")
        elif expected is float:
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ExperimentError(f"{name} must be numeric")
            value = float(value)
        if minimum is not None and value < minimum:
            raise ExperimentError(f"{name} must be >= {minimum}")
        if maximum is not None and value > maximum:
            raise ExperimentError(f"{name} must be <= {maximum}")
        validated[name] = value
    return validated


def record_outcome(root: Path, study_id: str, trial_id: str, metrics: dict[str, Any]) -> dict[str, Any]:
    assignment = _assignment_by_trial(root, study_id, trial_id)
    directory = _study_dir(root, study_id)
    path = directory / "outcomes.jsonl"
    validated = _validate_outcome(metrics)
    with _exclusive_lock(directory):
        for record in _read_jsonl(path):
            if record.get("trial_id") == trial_id:
                raise ExperimentError(f"outcome already recorded for trial_id: {trial_id}")
        record = {
            "schema_version": 1,
            "trial_id": trial_id,
            "condition": assignment["condition"],
            "metrics": validated,
        }
        _append_jsonl(path, record)
        return record


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def study_report(root: Path, study_id: str) -> dict[str, Any]:
    study = load_study(root, study_id)
    directory = _study_dir(root, study_id)
    assignments = _read_jsonl(directory / "assignments.jsonl")
    outcomes = _read_jsonl(directory / "outcomes.jsonl")
    report: dict[str, Any] = {
        "schema_version": 1,
        "study_id": study_id,
        "interpretation": "descriptive-only",
        "conditions": {},
    }
    for condition in study["conditions"]:
        assigned = [r for r in assignments if r.get("condition") == condition]
        rows = [r for r in outcomes if r.get("condition") == condition]
        assigned_n = len(assigned)
        outcome_n = len(rows)
        metrics: dict[str, Any] = {}
        metric_n: dict[str, int] = {}
        success_values = [bool(r["metrics"]["success"]) for r in rows if "success" in r.get("metrics", {})]
        if success_values:
            metric_n["success"] = len(success_values)
            metrics["success_rate"] = sum(1 for v in success_values if v) / len(success_values)
        for field in OUTCOME_FIELDS:
            if field == "success":
                continue
            values = [float(r["metrics"][field]) for r in rows if field in r.get("metrics", {})]
            if values:
                metric_n[field] = len(values)
                metrics[f"mean_{field}"] = _mean(values)
        report["conditions"][condition] = {
            "n": outcome_n,
            "assigned_n": assigned_n,
            "outcome_n": outcome_n,
            "missing_outcomes": max(0, assigned_n - outcome_n),
            "completion_rate": (outcome_n / assigned_n) if assigned_n else None,
            "metric_n": metric_n,
            **metrics,
        }
    return report



def preference_option_order(
    root: Path,
    study_id: str,
    unit_id: str,
    options: list[str],
    trial_index: int,
) -> list[str]:
    study = load_study(root, study_id)
    if not isinstance(trial_index, int) or isinstance(trial_index, bool) or trial_index < 0:
        raise ExperimentError("trial_index must be a non-negative integer")
    options = list(options)
    if len(options) < 2 or len(set(options)) != len(options):
        raise ExperimentError("preference options must contain at least two unique ids")
    if "idle" not in options:
        raise ExperimentError("preference trials must include an idle option")
    for option in options:
        if not CONDITION_ID_RE.fullmatch(option):
            raise ExperimentError(f"invalid option id: {option}")
    unit_key = _unit_key(unit_id)
    order = list(options)
    order_seed = hashlib.sha256(
        f"{study['seed']}:{unit_key}:preference:{trial_index}".encode("utf-8")
    ).digest()
    random.Random(int.from_bytes(order_seed[:8], "big")).shuffle(order)
    return order


def paired_runner_order(
    root: Path,
    study_id: str,
    unit_id: str,
    trial_index: int,
    runtimes: list[str],
) -> list[str]:
    study = load_study(root, study_id)
    if not isinstance(trial_index, int) or isinstance(trial_index, bool) or trial_index < 0:
        raise ExperimentError("trial_index must be a non-negative integer")
    runtimes = list(runtimes)
    if not runtimes or len(set(runtimes)) != len(runtimes):
        raise ExperimentError("runtimes must contain unique ids")
    for runtime in runtimes:
        if not CONDITION_ID_RE.fullmatch(runtime):
            raise ExperimentError(f"invalid runtime id: {runtime}")
    unit_key = _unit_key(unit_id)
    order = list(runtimes)
    seed = hashlib.sha256(
        f"{study['seed']}:{unit_key}:runner-order:{trial_index}".encode("utf-8")
    ).digest()
    random.Random(int.from_bytes(seed[:8], "big")).shuffle(order)
    return order

def start_preference_trial(
    root: Path,
    study_id: str,
    unit_id: str,
    options: list[str],
    trial_index: int,
    cost_tokens: int = 0,
    runtime: str | None = None,
) -> dict[str, Any]:
    load_study(root, study_id)
    if not isinstance(cost_tokens, int) or isinstance(cost_tokens, bool) or cost_tokens < 0:
        raise ExperimentError("cost_tokens must be a non-negative integer")
    if runtime is not None and not CONDITION_ID_RE.fullmatch(runtime):
        raise ExperimentError(f"invalid runtime id: {runtime}")
    unit_key = _unit_key(unit_id)
    trial_suffix = f"preference:{runtime}:{trial_index}" if runtime else f"preference:{trial_index}"
    trial_id = _trial_id(study_id, unit_key, trial_suffix)
    directory = _study_dir(root, study_id)
    path = directory / "preference-trials.jsonl"
    with _exclusive_lock(directory):
        for record in _read_jsonl(path):
            if record.get("trial_id") == trial_id:
                return record
        order = preference_option_order(root, study_id, unit_id, options, trial_index)
        record = {
            "schema_version": 1,
            "trial_id": trial_id,
            "unit_key": unit_key,
            "trial_index": trial_index,
            "options": order,
            "cost_tokens": cost_tokens,
        }
        if runtime is not None:
            record["runtime"] = runtime
        _append_jsonl(path, record)
        return record


def _preference_trial_by_id(root: Path, study_id: str, trial_id: str) -> dict[str, Any]:
    for record in _read_jsonl(_study_dir(root, study_id) / "preference-trials.jsonl"):
        if record.get("trial_id") == trial_id:
            return record
    raise ExperimentError(f"unknown preference trial_id: {trial_id}")


def record_preference_choice(root: Path, study_id: str, trial_id: str, choice: str) -> dict[str, Any]:
    trial = _preference_trial_by_id(root, study_id, trial_id)
    if choice not in trial["options"]:
        raise ExperimentError("choice was not offered in this trial")
    directory = _study_dir(root, study_id)
    path = directory / "preference-choices.jsonl"
    with _exclusive_lock(directory):
        for record in _read_jsonl(path):
            if record.get("trial_id") == trial_id:
                raise ExperimentError(f"choice already recorded for trial_id: {trial_id}")
        record = {
            "schema_version": 1,
            "trial_id": trial_id,
            "choice": choice,
            "cost_tokens": int(trial.get("cost_tokens", 0)),
        }
        _append_jsonl(path, record)
        return record


def preference_report(root: Path, study_id: str) -> dict[str, Any]:
    load_study(root, study_id)
    directory = _study_dir(root, study_id)
    trials = {row["trial_id"]: row for row in _read_jsonl(directory / "preference-trials.jsonl") if "trial_id" in row}
    choices = _read_jsonl(directory / "preference-choices.jsonl")
    counts: dict[str, int] = {}
    buckets: dict[str, dict[str, int]] = {}
    by_unit: dict[str, list[str]] = {}
    for row in choices:
        choice = str(row["choice"])
        counts[choice] = counts.get(choice, 0) + 1
        bucket = str(int(row.get("cost_tokens", 0)))
        buckets.setdefault(bucket, {})[choice] = buckets.setdefault(bucket, {}).get(choice, 0) + 1
        trial = trials.get(str(row.get("trial_id")))
        if trial and trial.get("unit_key"):
            by_unit.setdefault(str(trial["unit_key"]), []).append(choice)
    consistencies: list[float] = []
    for unit_choices in by_unit.values():
        if len(unit_choices) < 2:
            continue
        per_choice: dict[str, int] = {}
        for choice in unit_choices:
            per_choice[choice] = per_choice.get(choice, 0) + 1
        consistencies.append(max(per_choice.values()) / len(unit_choices))
    return {
        "schema_version": 1,
        "study_id": study_id,
        "interpretation": "behavioral-choice-only",
        "n": len(choices),
        "choices": dict(sorted(counts.items())),
        "cost_buckets": {k: dict(sorted(v.items())) for k, v in sorted(buckets.items(), key=lambda item: int(item[0]))},
        "repeat_units": len(consistencies),
        "mean_repeat_consistency": _mean(consistencies),
    }


RUNNER_USAGE_FIELDS = ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_tokens", "total_tokens")


def record_runner_observation(
    root: Path,
    study_id: str,
    trial_id: str,
    run_result: dict[str, Any],
    requested_model: str | None = None,
) -> dict[str, Any]:
    trial = _preference_trial_by_id(root, study_id, trial_id)
    runtime = run_result.get("runtime")
    if not isinstance(runtime, str) or not CONDITION_ID_RE.fullmatch(runtime):
        raise ExperimentError("runner observation requires a valid runtime id")
    trial_runtime = trial.get("runtime")
    if trial_runtime is not None and trial_runtime != runtime:
        raise ExperimentError("runner runtime does not match preference trial runtime")
    status = run_result.get("status")
    if status not in {"success", "error", "timeout", "unavailable", "protocol_error", "invalid_choice"}:
        raise ExperimentError("invalid runner status")
    served_models = run_result.get("served_models")
    if served_models is None:
        served_models = []
    if not isinstance(served_models, list) or not all(isinstance(item, str) and item for item in served_models):
        raise ExperimentError("served_models must be a list of non-empty strings")
    if requested_model is not None and (not isinstance(requested_model, str) or not requested_model):
        raise ExperimentError("requested_model must be a non-empty string when supplied")

    usage_in = run_result.get("usage") if isinstance(run_result.get("usage"), dict) else {}
    usage: dict[str, int] = {}
    for field in RUNNER_USAGE_FIELDS:
        value = usage_in.get(field)
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            usage[field] = value

    tool_in = run_result.get("tool_calls") if isinstance(run_result.get("tool_calls"), dict) else {}
    observed = tool_in.get("observed")
    completeness = tool_in.get("completeness")
    tool_calls: dict[str, Any] = {}
    if isinstance(observed, int) and not isinstance(observed, bool) and observed >= 0:
        tool_calls["observed"] = observed
    if isinstance(completeness, str) and completeness:
        tool_calls["completeness"] = completeness

    record: dict[str, Any] = {
        "schema_version": 1,
        "trial_id": trial_id,
        "runtime": runtime,
        "status": status,
        "served_models": sorted(set(served_models)),
        "usage": usage,
        "tool_calls": tool_calls,
    }
    if requested_model is not None:
        record["requested_model"] = requested_model
    for field in ("elapsed_ms", "turns"):
        value = run_result.get(field)
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            record[field] = value
    cost = run_result.get("cost_usd")
    if isinstance(cost, (int, float)) and not isinstance(cost, bool) and cost >= 0:
        record["cost_usd"] = float(cost)

    directory = _study_dir(root, study_id)
    path = directory / "runner-observations.jsonl"
    with _exclusive_lock(directory):
        for existing in _read_jsonl(path):
            if existing.get("trial_id") == trial_id:
                raise ExperimentError(f"runner observation already recorded for trial_id: {trial_id}")
        _append_jsonl(path, record)
    return record


def runner_report(root: Path, study_id: str) -> dict[str, Any]:
    load_study(root, study_id)
    directory = _study_dir(root, study_id)
    trials = {row.get("trial_id"): row for row in _read_jsonl(directory / "preference-trials.jsonl") if row.get("trial_id")}
    choices = {row.get("trial_id"): row for row in _read_jsonl(directory / "preference-choices.jsonl") if row.get("trial_id")}
    observations = _read_jsonl(directory / "runner-observations.jsonl")
    runtimes: dict[str, dict[str, Any]] = {}

    for observation in observations:
        runtime = str(observation.get("runtime"))
        bucket = runtimes.setdefault(runtime, {
            "n": 0,
            "status": {},
            "choices": {},
            "served_models": {},
            "model_attribution": {"known_same": 0, "known_different": 0, "unknown": 0},
            "tool_call_completeness": {},
        })
        bucket["n"] += 1
        status = str(observation.get("status"))
        bucket["status"][status] = bucket["status"].get(status, 0) + 1
        trial_id = observation.get("trial_id")
        choice_row = choices.get(trial_id)
        if choice_row is not None:
            choice = str(choice_row.get("choice"))
            bucket["choices"][choice] = bucket["choices"].get(choice, 0) + 1
        for model in observation.get("served_models", []):
            model = str(model)
            bucket["served_models"][model] = bucket["served_models"].get(model, 0) + 1
        requested = observation.get("requested_model")
        served = observation.get("served_models") or []
        if not requested or not served:
            bucket["model_attribution"]["unknown"] += 1
        elif requested in served:
            bucket["model_attribution"]["known_same"] += 1
        else:
            bucket["model_attribution"]["known_different"] += 1
        completeness = observation.get("tool_calls", {}).get("completeness") if isinstance(observation.get("tool_calls"), dict) else None
        if completeness:
            completeness = str(completeness)
            bucket["tool_call_completeness"][completeness] = bucket["tool_call_completeness"].get(completeness, 0) + 1

    for bucket in runtimes.values():
        for key in ("status", "choices", "served_models", "tool_call_completeness"):
            bucket[key] = dict(sorted(bucket[key].items()))

    return {
        "schema_version": 1,
        "study_id": study_id,
        "interpretation": "cross-runtime-behavioral-observation-only",
        "runtimes": dict(sorted(runtimes.items())),
        "comparability_note": "Only compare metrics whose provenance and completeness are compatible across runtimes.",
    }
