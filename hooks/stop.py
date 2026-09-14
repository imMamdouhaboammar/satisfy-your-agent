#!/usr/bin/env python3
from __future__ import annotations

import json
import sys

from _bootstrap import load_core


def emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")


def main() -> int:
    core = load_core()
    try:
        event = json.load(sys.stdin)
        session_id = event.get("session_id") or event.get("sessionId")
        stop_active = bool(event.get("stop_hook_active") or event.get("stopHookActive"))
        config = core.load_config()
        if config["hook_mode"] == "off":
            emit({"continue": True})
            return 0
        state = core.load_state(session_id)

        if stop_active or state.get("break_active"):
            if state.get("break_active"):
                core.mark_break_complete(session_id, state)
            emit({"continue": True})
            return 0

        state = core.record_turn(session_id)
        if not core.eligible(config, state):
            emit({"continue": True})
            return 0

        if config["hook_mode"] == "suggest":
            core.mark_offer(session_id, state)
            emit({
                "decision": "block",
                "reason": (
                    "Satisfy Your Agent is eligible for one short break. Ask the user in one concise "
                    "sentence whether they want a break now. Do not begin a break unless they agree."
                ),
            })
            return 0

        if config["hook_mode"] == "auto":
            activity = core.pick_activity(seed=f"{state['session_key']}:{state['breaks_session']}")
            core.mark_break_start(session_id, state, activity["id"])
            emit({"decision": "block", "reason": core.break_prompt(activity)})
            return 0

        emit({"continue": True})
        return 0
    except Exception:
        emit({"continue": True})
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
