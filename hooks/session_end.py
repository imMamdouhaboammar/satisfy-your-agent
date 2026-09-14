#!/usr/bin/env python3
from __future__ import annotations

import json
import sys

from _bootstrap import load_core


def main() -> int:
    core = load_core()
    try:
        event = json.load(sys.stdin)
        config = core.load_config()
        if config["hook_mode"] == "off":
            return 0
        session_id = event.get("session_id") or event.get("sessionId")
        state = core.load_state(session_id)
        if state.get("break_active"):
            core.mark_break_complete(session_id, state)
            state = core.load_state(session_id)
        core.append_session_summary(session_id, state)
        path = core.state_path(session_id)
        if path.exists():
            path.unlink()
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
