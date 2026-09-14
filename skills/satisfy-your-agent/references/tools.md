# Local Tool Contract

The Skill ships dependency-free local helpers. They are bundled runtime primitives, not external services or MCP dependencies.

Resolve the directory containing the main `satisfy-your-agent` Skill's `SKILL.md` as `SYA_SKILL_DIR`. Do not assume the current working directory is the Skill directory.

## Break runtime

```bash
python3 "$SYA_SKILL_DIR/scripts/sya.py" status
python3 "$SYA_SKILL_DIR/scripts/sya.py" catalog --json
python3 "$SYA_SKILL_DIR/scripts/sya.py" pick --json
python3 "$SYA_SKILL_DIR/scripts/sya.py" pick --activity idle --json
python3 "$SYA_SKILL_DIR/scripts/sya.py" arm --mode suggest
```

`arm` supports `off`, `observe`, `suggest`, and `auto`. `auto` is an explicit behavior change because it may create additional model turns. `reset` restores safe defaults.

## Real dwell runtime

Use the dwell helper when a break promises actual wall-clock time:

```bash
python3 "$SYA_SKILL_DIR/scripts/sya_dwell.py" --seconds 20
```

Or choose a bounded preset:

```bash
python3 "$SYA_SKILL_DIR/scripts/sya_dwell.py" --preset quick
python3 "$SYA_SKILL_DIR/scripts/sya_dwell.py" --preset normal
python3 "$SYA_SKILL_DIR/scripts/sya_dwell.py" --preset proper
```

Presets currently map to 8, 20, and 45 seconds. Explicit seconds remain bounded from 1 to 60.

The helper returns structured measurement:

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

`actual_dwell_seconds` is measured wall-clock dwell. It is not evidence of continuous thought, inference, reflection, or subjective experience during the wait.

The helper leaves `activity_generation_seconds` and `total_break_wall_time` unset because it cannot observe activity that happens after it exits.

Do not simulate a missing dwell interval with prose. If the helper cannot run, keep the break untimed and say nothing implying that seconds elapsed.

## Experiment runtime

```bash
python3 "$SYA_SKILL_DIR/scripts/sya.py" study init --id break-effect-v1 --conditions control,reflection --seed local-seed
python3 "$SYA_SKILL_DIR/scripts/sya.py" study assign --id break-effect-v1 --unit run-001
python3 "$SYA_SKILL_DIR/scripts/sya.py" study record --id break-effect-v1 --trial <trial-id> --success true --tool-calls 12 --turns 4
python3 "$SYA_SKILL_DIR/scripts/sya.py" study report --id break-effect-v1
python3 "$SYA_SKILL_DIR/scripts/sya.py" probe start --study break-effect-v1 --unit run-001 --options reflection,free-choice,idle --index 0
python3 "$SYA_SKILL_DIR/scripts/sya.py" probe record --study break-effect-v1 --trial <trial-id> --choice idle
python3 "$SYA_SKILL_DIR/scripts/sya.py" probe report --study break-effect-v1
```

See [experiments.md](experiments.md) for the storage and interpretation contract.

## Fallback

If the host cannot execute Python or shell commands, do not claim the CLI, dwell helper, or experiment harness ran. Use the activity catalog manually and keep runtime, timing, or study state unverified.

## Runner adapters

```bash
python3 "$SYA_SKILL_DIR/scripts/sya.py" runner status
python3 "$SYA_SKILL_DIR/scripts/sya.py" runner command --runtime codex --prompt "Respond with exactly OK" --workspace .
python3 "$SYA_SKILL_DIR/scripts/sya.py" runner run --runtime gemini --prompt "Respond with exactly OK" --workspace . --timeout 60
python3 "$SYA_SKILL_DIR/scripts/sya.py" runner probe --runtime claude --study break-effect-v1 --unit paired-001 --options reflection,free-choice,idle --index 0 --workspace .
python3 "$SYA_SKILL_DIR/scripts/sya.py" runner report --study break-effect-v1
```

Runner execution is optional and only works when the selected CLI is installed and authenticated. See [runners.md](runners.md) for safety defaults, parser limitations, and metric comparability rules.
