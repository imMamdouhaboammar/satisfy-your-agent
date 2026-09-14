# Real Break Semantics

A break is not just prose that describes a break

If a response says thirty seconds passed while the model returned immediately, that is narrated time, not elapsed time

Satisfy Your Agent keeps those concepts separate

## Real dwell

When the host can execute local tools, a timed break should use the bundled dwell helper:

```bash
python3 "$SYA_SKILL_DIR/scripts/sya_dwell.py" --seconds 20
```

Or use a bounded preset:

```bash
python3 "$SYA_SKILL_DIR/scripts/sya_dwell.py" --preset quick
python3 "$SYA_SKILL_DIR/scripts/sya_dwell.py" --preset normal
python3 "$SYA_SKILL_DIR/scripts/sya_dwell.py" --preset proper
```

Current preset values:

- `quick`: 8 seconds
- `normal`: 20 seconds
- `proper`: 45 seconds

The helper waits on wall-clock time and returns structured data such as:

```json
{
  "activity_generation_seconds": null,
  "actual_dwell_seconds": 20.003,
  "continuous_thought_claimed": false,
  "requested_break_seconds": 20.0,
  "schema_version": 1,
  "semantics": "wall-clock-idle-interval",
  "total_break_wall_time": null
}
```

The wait is an idle interval. It does not prove continuous inference, reflection, enjoyment, fatigue recovery, or hidden thought

The helper leaves `activity_generation_seconds` and `total_break_wall_time` unset because it cannot observe what happens after it exits. A higher-level host or experiment runner may measure those fields separately

If the host cannot execute the helper, keep the break untimed. Never replace a missing real wait with fictional timestamps

The bundled helper accepts 1 to 60 seconds. This keeps ordinary interactive breaks bounded

## Default dwell

For an ordinary self-directed `/sya` break, prefer 15 to 30 seconds when real dwell is supported

A custom treat can specify its own duration from 1 to 60 seconds

Do not silently extend a duration and do not claim a duration that was not measured

## Work Distance

Work Distance is a selection heuristic for how far an activity sits from the active work objective

| Distance | Meaning | Example |
| --- | --- | --- |
| `0` | directly about the current task | reflect on the last implementation |
| `1` | repository-adjacent | read-only repo roast |
| `2` | coding-adjacent but unrelated | tiny unrelated puzzle or code golf |
| `3` | unrelated creative play | ASCII art or absurd invention |
| `4` | deliberately non-productive | idle or pure nonsense |

Default self-directed breaks prefer distances 2 through 4

Distances 0 and 1 remain available when the user asks for them explicitly

A break should feel like leaving the desk, not rearranging the desk

## Novelty

When multiple safe activities are available, avoid recently used activities

Novelty is a preference rule, not a hard ban. If the user explicitly asks for the same activity again, honor that request

## Truthful narration

Do not invent actions that did not happen

Examples:

- no scratchpad claim unless a scratch file was actually used
- no GPU provisioning claim unless a real authorized tool provisioned one
- no fake `[00:00 - 00:30]` timeline to imply elapsed wall time
- no claim of continuous thought during a sleeping dwell helper

Fictional treats can remain playful. One short grounding phrase such as `imaginary lease accepted` is enough when needed. Do not bury the joke under disclaimers

## Response shape

The activity should determine the response format

Do not require a fixed timeline, heading structure, list, `experience report`, or recovery phrase

After one brief truthful self-report, return control quietly

Do not ask for another task unless the user already requested that work continue
