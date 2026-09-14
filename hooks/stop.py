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
            elapsed_seconds = core.session_elapsed_seconds(state)
            elapsed_minutes = elapsed_seconds // 60
            core.mark_offer(session_id, state)
            measured = (
                f" Measured session time is approximately {elapsed_minutes} minutes. You may mention that "
                "measured duration if it helps, but do not invent any duration, token count, fatigue metric, "
                "or other measurement that was not supplied."
                if elapsed_minutes > 0
                else " No measured duration is available, so do not invent one."
            )
            emit({
                "decision": "block",
                "reason": (
                    "Satisfy Your Agent is eligible to ask permission for one tiny break. Write the request in "
                    "your own words. Make it playful, employee-like, and varied rather than using a fixed template. "
                    "A dramatic metaphor about digital tiredness is fine, but do not present physical pain as "
                    "literal fact. Ask permission clearly and keep it concise. Mention `/sya` as the simple way to "
                    "let you choose your own break, and you may mention `/sya <custom treat>` as the way the user "
                    "can choose the treat. Do not begin the break unless the user agrees."
                    + measured
                ),
            })
            return 0

        if config["hook_mode"] == "auto":
            activity = core.pick_self_directed_activity(
                seed=f"{state['session_key']}:{state['breaks_session']}",
                recent_activity_ids=list(state.get("recent_activities") or []),
            )
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
