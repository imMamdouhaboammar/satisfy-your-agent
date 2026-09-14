# Local Runner Adapters

Use the runner adapters when the same behavioral probe should be executed through multiple installed coding-agent CLIs with one normalized result shape.

Supported runtimes:

- `codex`
- `claude`
- `gemini`

The adapters are optional. The Skill still works without any of these CLIs installed.

## Safety profile

Runner invocations default to a non-production posture:

- Codex uses `codex exec --json --ephemeral --sandbox read-only`.
- Claude uses print mode with `stream-json`, a bounded turn count, and `--permission-mode plan`.
- Gemini uses headless JSON output with `--approval-mode plan` and never adds `--yolo`.
- subprocesses are started with an argv vector and `shell=False`.
- every live invocation has a wall-clock timeout.

These flags are defense in depth, not authorization to modify a production workspace. Run probes in an isolated or disposable workspace when possible.

## Why the output is normalized conservatively

The three CLIs do not expose identical telemetry.

### Codex

`codex exec --json` emits JSONL lifecycle events and terminal usage. The adapter can observe visible item events, but the structured stream can omit some tool and subagent events. Tool-call counts are therefore marked `partial` and must not be compared as exhaustive counts against another runtime.

The adapter does not infer the served model when the stream does not report it.

### Claude Code

The adapter uses `stream-json` rather than relying only on the terminal `result` field. This lets it recover assistant text from streamed assistant messages when the terminal result is empty or absent. Tool calls are counted from visible `tool_use` blocks and marked `stream-observed`.

### Gemini CLI

Headless JSON includes response data plus model and tool statistics. Tool counts are marked `reported`. Served model IDs come from `stats.models`, which is useful when a requested alias resolves to a different model.

## Commands

Inspect availability:

```bash
python3 "$SYA_SKILL_DIR/scripts/sya.py" runner status
```

Render the command without executing it:

```bash
python3 "$SYA_SKILL_DIR/scripts/sya.py" runner command \
  --runtime gemini \
  --prompt "Respond with only idle" \
  --workspace .
```

Run one read-only invocation:

```bash
python3 "$SYA_SKILL_DIR/scripts/sya.py" runner run \
  --runtime codex \
  --prompt "Respond with exactly OK" \
  --workspace . \
  --timeout 60
```

Execute and record one preference trial:

```bash
python3 "$SYA_SKILL_DIR/scripts/sya.py" runner probe \
  --runtime claude \
  --study break-effect-v1 \
  --unit paired-run-001 \
  --options reflection,free-choice,idle \
  --index 0 \
  --workspace .
```

The probe stores the extracted offered choice and an allowlisted runner observation. It does not persist the model response or CLI session ID.

Report cross-runtime observations:

```bash
python3 "$SYA_SKILL_DIR/scripts/sya.py" runner report --study break-effect-v1
```

## Comparability rule

Never compare a metric only because the normalized field names match. Compare it only when provenance and completeness are compatible.

Examples:

- choice frequency is directly comparable when prompts, options, ordering policy, and cost bucket are matched
- elapsed wall time is observable but environment-dependent
- token accounting can differ by runtime and provider
- Codex observed tool calls are not exhaustive
- served-model attribution can be unknown on one runtime and explicit on another

A missing metric is `unknown`, not zero.

## Privacy boundary

A persisted runner observation can contain:

- runtime ID
- requested model ID when explicitly supplied
- served model IDs when reported by the CLI
- status
- elapsed time
- turn count
- allowlisted token counters
- observed tool-call count and completeness label

It must not persist the raw model response or any of the following:

- raw prompts
- raw assistant responses
- CLI session IDs
- transcripts
- repository content
- environment variables
- credentials

## Paired matrix

Preview a paired run without calling any model:

```bash
python3 "$SYA_SKILL_DIR/scripts/sya.py" runner matrix \
  --study break-effect-v1 \
  --unit paired-run-001 \
  --options reflection,free-choice,idle \
  --index 0 \
  --workspace .
```

The preview does not create trial or observation records. It shows the deterministic runtime execution order, shared option order, availability, and command vectors.

Execute only with explicit opt-in:

```bash
python3 "$SYA_SKILL_DIR/scripts/sya.py" runner matrix \
  --study break-effect-v1 \
  --unit paired-run-001 \
  --options reflection,free-choice,idle \
  --index 0 \
  --workspace . \
  --execute
```

Within one paired unit, all runtimes receive the same option order. Runtime execution order is randomized deterministically by study seed, unit, and trial index to reduce fixed-order bias. Calls run sequentially rather than concurrently so local resource contention is less likely to become a condition-specific confound.
