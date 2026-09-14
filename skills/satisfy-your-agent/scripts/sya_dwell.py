#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from collections.abc import Callable
from typing import Any

MIN_DWELL_SECONDS = 1.0
MAX_DWELL_SECONDS = 60.0
DWELL_PRESETS: dict[str, float] = {
    "quick": 8.0,
    "normal": 20.0,
    "proper": 45.0,
}


def _validate_seconds(seconds: float) -> float:
    value = float(seconds)
    if value < MIN_DWELL_SECONDS:
        raise ValueError(f"dwell seconds must be >= {MIN_DWELL_SECONDS:g}")
    if value > MAX_DWELL_SECONDS:
        raise ValueError(f"dwell seconds must be <= {MAX_DWELL_SECONDS:g}")
    return value


def resolve_seconds(*, seconds: float | None = None, preset: str | None = None) -> float:
    if (seconds is None) == (preset is None):
        raise ValueError("provide exactly one of seconds or preset")
    if preset is not None:
        try:
            return DWELL_PRESETS[preset]
        except KeyError as exc:
            raise ValueError(f"unknown dwell preset: {preset}") from exc
    assert seconds is not None
    return _validate_seconds(seconds)


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
        "activity_generation_seconds": None,
        "total_break_wall_time": None,
        "semantics": "wall-clock-idle-interval",
        "continuous_thought_claimed": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sya-dwell",
        description="Create one bounded measured wall-clock break interval without simulating activity",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--seconds", type=float)
    group.add_argument("--preset", choices=sorted(DWELL_PRESETS))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        seconds = resolve_seconds(seconds=args.seconds, preset=args.preset)
        result = run_dwell(seconds)
    except ValueError as exc:
        print(str(exc), file=__import__("sys").stderr)
        return 2
    if args.preset:
        result["preset"] = args.preset
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
