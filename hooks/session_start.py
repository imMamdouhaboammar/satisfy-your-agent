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
        core.save_state(session_id, state)
    except Exception:
        # Hooks must fail open. The skill still works manually if local state is unavailable.
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
