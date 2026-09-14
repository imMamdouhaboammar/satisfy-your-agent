#!/usr/bin/env python3
from __future__ import annotations

import json
import sys

from _bootstrap import load_core


def main() -> int:
    core = load_core()
    try:
        event = json.load(sys.stdin)
        session_id = event.get("session_id") or event.get("sessionId")
        config = core.load_config()
        if config["hook_mode"] != "off":
            core.record_tool_call(session_id)
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
