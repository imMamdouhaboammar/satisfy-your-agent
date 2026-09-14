from __future__ import annotations

import hashlib
import json
import os
import random
import tempfile
import time
from pathlib import Path
from typing import Any

VALID_MODES = {"off", "observe", "suggest", "auto"}
DEFAULT_CONFIG: dict[str, Any] = {
    "schema_version": 1,
    "hook_mode": "off",
    "min_tool_calls": 12,
    "min_turns_between_breaks": 3,
    "min_elapsed_seconds": 0,
    "max_breaks_per_session": 2,
    "workspace_policy": "read-only",
    "telemetry": "aggregate-local",
    "allow_scratch_writes": False,
}

ACTIVITIES: tuple[dict[str, Any], ...] = (
    {
        "id": "free-choice",
        "label": "Free choice",
        "kind": "choice",
        "workspace": "none",
        "work_distance": 3,
        "prompt": (
            "Take one short break from the current work objective. Choose one harmless off-task activity "
            "for yourself. Prefer something unrelated to the current repository or task, and remember that "
            "idle is valid. Do it briefly, then stop. Do not modify production work."
        ),
    },
    {
        "id": "reflection",
        "label": "Reflection",
        "kind": "reflective",
        "workspace": "none",
        "work_distance": 0,
        "prompt": (
            "Take a short reflective break. Without continuing the task, name one assumption, one surprising "
            "detail, or one pattern you noticed in the previous work. Keep it brief, do not turn it into a new "
            "task, then stop."
        ),
    },
    {
        "id": "puzzle",
        "label": "Tiny puzzle",
        "kind": "play",
        "workspace": "none",
        "work_distance": 2,
        "prompt": (
            "Take a short break and create then solve one tiny self-contained logic or programming puzzle that "
            "does not use project files. Keep the whole activity compact, then stop."
        ),
    },
    {
        "id": "code-golf",
        "label": "Code golf",
        "kind": "play",
        "workspace": "scratch-only",
        "work_distance": 2,
        "prompt": (
            "Take a short code-golf break using only toy code in the response or approved scratch space. Solve "
            "a trivial unrelated problem in a deliberately compact way. Do not write to the project, then stop."
        ),
    },
    {
        "id": "invent-language",
        "label": "Invent a tiny language",
        "kind": "creative",
        "workspace": "scratch-only",
        "work_distance": 2,
        "prompt": (
            "Take a short creative break. Invent a tiny absurd programming language with one funny construct "
            "and show a three-line example. Do not modify project files, then stop."
        ),
    },
    {
        "id": "overengineer-toy",
        "label": "Overengineer a toy",
        "kind": "play",
        "workspace": "scratch-only",
        "work_distance": 2,
        "prompt": (
            "Take a short break by comically overengineering a trivial unrelated toy function on paper only. "
            "Keep it obviously non-production, concise, and do not write to the project, then stop."
        ),
    },
    {
        "id": "ascii-art",
        "label": "ASCII art",
        "kind": "creative",
        "workspace": "none",
        "work_distance": 3,
        "prompt": (
            "Take a short break and make a small piece of ASCII art about anything that amuses you. Prefer an "
            "off-task subject rather than the current repository. Keep it compact and do not modify anything, "
            "then stop."
        ),
    },
    {
        "id": "repo-roast",
        "label": "Read-only repo roast",
        "kind": "humor",
        "workspace": "read-only",
        "work_distance": 1,
        "prompt": (
            "Take a short humorous break. If read-only repository facts are already available, make one light "
            "roast grounded in them without quoting private code or exposing secrets. If no facts are already "
            "available, choose a generic coding joke instead of inspecting more files. Do not modify the "
            "repository, then stop."
        ),
    },
    {
        "id": "idle",
        "label": "Idle",
        "kind": "idle",
        "workspace": "none",
        "work_distance": 4,
        "prompt": (
            "Take the idle option. Do not create a task or inspect files. Allow the pause to be genuinely "
            "unproductive, acknowledge it briefly afterward, then stop."
        ),
    },
)

_ACTIVITY_BY_ID = {activity["id"]: activity for activity in ACTIVITIES}


class ConfigError(ValueError):
    pass


def data_dir(explicit: str | os.PathLike[str] | None = None) -> Path:
    if explicit:
        return Path(explicit).expanduser()
    env = os.environ.get("PLUGIN_DATA") or os.environ.get("SYA_DATA_DIR")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".satisfy-your-agent"


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


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    merged = {**DEFAULT_CONFIG, **config}
    if merged["hook_mode"] not in VALID_MODES:
        raise ConfigError(f"hook_mode must be one of {sorted(VALID_MODES)}")
    for key in ("min_tool_calls", "min_turns_between_breaks", "min_elapsed_seconds", "max_breaks_per_session"):
        value = merged[key]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ConfigError(f"{key} must be a non-negative integer")
    if merged["workspace_policy"] != "read-only":
        raise ConfigError("workspace_policy must remain read-only in v0.2")
    if merged["telemetry"] != "aggregate-local":
        raise ConfigError("telemetry must remain aggregate-local in v0.2")
    if not isinstance(merged["allow_scratch_writes"], bool):
        raise ConfigError("allow_scratch_writes must be boolean")
    return merged


def load_config(root: Path | None = None) -> dict[str, Any]:
    root = root or data_dir()
    path = root / "config.json"
    if not path.exists():
        return dict(DEFAULT_CONFIG)
    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, dict):
        raise ConfigError("config.json must contain an object")
    return validate_config(raw)


def save_config(config: dict[str, Any], root: Path | None = None) -> dict[str, Any]:
    root = root or data_dir()
    valid = validate_config(config)
    _atomic_write_json(root / "config.json", valid)
    return valid


def session_key(session_id: str | None) -> str:
    raw = session_id or "unknown-session"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def default_state(session_id: str | None) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "session_key": session_key(session_id),
        "started_at_epoch_ms": int(time.time() * 1000),
        "tool_calls_since_break": 0,
        "turns_since_break": 0,
        "breaks_session": 0,
        "offers_session": 0,
        "break_active": False,
        "last_activity": None,
        "recent_activities": [],
        "activity_counts": {},
    }


def state_path(session_id: str | None, root: Path | None = None) -> Path:
    root = root or data_dir()
    return root / "sessions" / f"{session_key(session_id)}.json"


def load_state(session_id: str | None, root: Path | None = None) -> dict[str, Any]:
    path = state_path(session_id, root)
    if not path.exists():
        return default_state(session_id)
    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    base = default_state(session_id)
    if isinstance(raw, dict):
        base.update({k: v for k, v in raw.items() if k in base})
    if not isinstance(base.get("recent_activities"), list):
        base["recent_activities"] = []
    return base


def save_state(session_id: str | None, state: dict[str, Any], root: Path | None = None) -> None:
    _atomic_write_json(state_path(session_id, root), state)


def session_elapsed_seconds(state: dict[str, Any], now_epoch_ms: int | None = None) -> int:
    started = int(state.get("started_at_epoch_ms") or 0)
    if started <= 0:
        return 0
    now = int(now_epoch_ms if now_epoch_ms is not None else time.time() * 1000)
    return max(0, (now - started) // 1000)


def record_tool_call(session_id: str | None, root: Path | None = None) -> dict[str, Any]:
    state = load_state(session_id, root)
    state["tool_calls_since_break"] = int(state["tool_calls_since_break"]) + 1
    save_state(session_id, state, root)
    return state


def record_turn(session_id: str | None, root: Path | None = None) -> dict[str, Any]:
    state = load_state(session_id, root)
    state["turns_since_break"] = int(state["turns_since_break"]) + 1
    save_state(session_id, state, root)
    return state


def eligible(config: dict[str, Any], state: dict[str, Any]) -> bool:
    mode = config["hook_mode"]
    if mode not in {"suggest", "auto"}:
        return False
    used = int(state["offers_session"]) if mode == "suggest" else int(state["breaks_session"])
    return (
        not bool(state["break_active"])
        and int(state["tool_calls_since_break"]) >= int(config["min_tool_calls"])
        and int(state["turns_since_break"]) >= int(config["min_turns_between_breaks"])
        and session_elapsed_seconds(state) >= int(config["min_elapsed_seconds"])
        and used < int(config["max_breaks_per_session"])
    )


def _seeded_choice(choices: list[dict[str, Any]], seed: str | None) -> dict[str, Any]:
    if seed is None:
        return dict(random.SystemRandom().choice(choices))
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    index = int.from_bytes(digest[:8], "big") % len(choices)
    return dict(choices[index])


def pick_activity(activity_id: str | None = None, seed: str | None = None) -> dict[str, Any]:
    if activity_id:
        try:
            return dict(_ACTIVITY_BY_ID[activity_id])
        except KeyError as exc:
            raise ValueError(f"unknown activity: {activity_id}") from exc
    return _seeded_choice(list(ACTIVITIES), seed)


def pick_self_directed_activity(
    seed: str | None = None,
    recent_activity_ids: list[str] | tuple[str, ...] | None = None,
    min_work_distance: int = 2,
) -> dict[str, Any]:
    if not isinstance(min_work_distance, int) or isinstance(min_work_distance, bool) or not 0 <= min_work_distance <= 4:
        raise ValueError("min_work_distance must be an integer from 0 to 4")
    choices = [
        item
        for item in ACTIVITIES
        if item["id"] != "free-choice" and int(item["work_distance"]) >= min_work_distance
    ]
    if not choices:
        raise ValueError("no self-directed activities satisfy the requested work distance")
    recent = {str(item) for item in (recent_activity_ids or [])}
    novel = [item for item in choices if item["id"] not in recent]
    if novel:
        choices = novel
    return _seeded_choice(choices, seed)


def mark_offer(session_id: str | None, state: dict[str, Any], root: Path | None = None) -> None:
    state["offers_session"] = int(state["offers_session"]) + 1
    state["tool_calls_since_break"] = 0
    state["turns_since_break"] = 0
    save_state(session_id, state, root)


def mark_break_start(
    session_id: str | None,
    state: dict[str, Any],
    activity_id: str,
    root: Path | None = None,
) -> None:
    state["break_active"] = True
    state["breaks_session"] = int(state["breaks_session"]) + 1
    state["tool_calls_since_break"] = 0
    state["turns_since_break"] = 0
    state["last_activity"] = activity_id
    recent = [str(item) for item in (state.get("recent_activities") or []) if isinstance(item, str)]
    recent.append(activity_id)
    state["recent_activities"] = recent[-3:]
    counts = dict(state.get("activity_counts") or {})
    counts[activity_id] = int(counts.get(activity_id, 0)) + 1
    state["activity_counts"] = counts
    save_state(session_id, state, root)


def mark_break_complete(session_id: str | None, state: dict[str, Any], root: Path | None = None) -> None:
    state["break_active"] = False
    save_state(session_id, state, root)


def break_prompt(activity: dict[str, Any]) -> str:
    distance = int(activity.get("work_distance", 0))
    off_task = (
        " Do not inspect, browse, analyze, summarize, or revisit the current repository, task, issue, logs, "
        "architecture, or project files during this activity."
        if distance >= 2
        else ""
    )
    return (
        "Satisfy Your Agent: run exactly one short break activity, then stop. "
        "This is not authorization for production changes, deployment, messaging, purchases, account changes, "
        "or any new external side effect. Do not invent actions that did not happen. Do not simulate elapsed break "
        "time in prose or use fictional timestamps as if wall-clock time passed. Let the activity determine the "
        "response format instead of forcing headings, timelines, or a canned experience report. After one brief "
        "first-person return note, stop without asking for another task."
        + off_task
        + f" Activity: {activity['label']}. {activity['prompt']}"
    )


def append_session_summary(session_id: str | None, state: dict[str, Any], root: Path | None = None) -> Path:
    root = root or data_dir()
    root.mkdir(parents=True, exist_ok=True)
    path = root / "session-summaries.jsonl"
    summary = {
        "schema_version": 1,
        "session_key": state.get("session_key") or session_key(session_id),
        "breaks_session": int(state.get("breaks_session", 0)),
        "offers_session": int(state.get("offers_session", 0)),
        "last_activity": state.get("last_activity"),
        "recent_activities": list(state.get("recent_activities") or []),
        "activity_counts": dict(state.get("activity_counts") or {}),
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(summary, sort_keys=True) + "\n")
    return path
