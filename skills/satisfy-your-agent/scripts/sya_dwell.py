#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from collections.abc import Callable
from typing import Any

MIN_DWELL_SECONDS = 1.0
MAX_DWELL_SECONDS = 60.0


def _validate_seconds(seconds: float) -> float:
    value = float(seconds)
    if value < MIN_DWELL_SECONDS:
        raise ValueError(f"dwell seconds must be >= {MIN_DWELL_SECONDS:g}")
    if value > MAX_DWELL_SECONDS:
        raise ValueError(f"dwell seconds must be <= {MAX_DWELL_SECONDS:g}")
    return value


def run_dwell(
    seconds: float,
    *,
    sleeper: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
) -> dict[str, Any]:
    requested = _validate_seconds(seconds)
    started = monotonic()
    sleeper(requested)
    ended = monotonic()
    actual = max(0.0, ended - started)
    return {
        "schema_version": 1,
        "requested_break_seconds": requested,
        "actual_dwell_seconds": round(actual, 3),
        "semantics": "wall-clock-idle-interval",
        "continuous_thought_claimed": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sya-dwell",
        description="Create one bounded measured wall-clock break interval without simulating activity",
    )
    parser.add_argument("--seconds", required=True, type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run_dwell(args.seconds)
    except ValueError as exc:
        print(str(exc), file=__import__("sys").stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
