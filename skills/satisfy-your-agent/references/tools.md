# Local Tool Contract

The Skill ships one dependency-free local CLI. It is a bundled helper, not an external service or MCP dependency.

Resolve the directory containing this Skill's `SKILL.md` as `SYA_SKILL_DIR`. Do not assume the current working directory is the Skill directory.

## Break runtime

```bash
python3 "$SYA_SKILL_DIR/scripts/sya.py" status
python3 "$SYA_SKILL_DIR/scripts/sya.py" catalog --json
python3 "$SYA_SKILL_DIR/scripts/sya.py" pick --json
python3 "$SYA_SKILL_DIR/scripts/sya.py" pick --activity idle --json
python3 "$SYA_SKILL_DIR/scripts/sya.py" arm --mode suggest
```

`arm` supports `off`, `observe`, `suggest`, and `auto`. `auto` is an explicit behavior change because it may create additional model turns. `reset` restores safe defaults.

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

If the host cannot execute Python or shell commands, do not claim the CLI or experiment harness ran. Use the activity catalog manually and keep runtime or study state unverified.

## Runner adapters

```bash
python3 "$SYA_SKILL_DIR/scripts/sya.py" runner status
python3 "$SYA_SKILL_DIR/scripts/sya.py" runner command --runtime codex --prompt "Respond with exactly OK" --workspace .
python3 "$SYA_SKILL_DIR/scripts/sya.py" runner run --runtime gemini --prompt "Respond with exactly OK" --workspace . --timeout 60
python3 "$SYA_SKILL_DIR/scripts/sya.py" runner probe --runtime claude --study break-effect-v1 --unit paired-001 --options reflection,free-choice,idle --index 0 --workspace .
python3 "$SYA_SKILL_DIR/scripts/sya.py" runner report --study break-effect-v1
```

Runner execution is optional and only works when the selected CLI is installed and authenticated. See [runners.md](runners.md) for safety defaults, parser limitations, and metric comparability rules.
