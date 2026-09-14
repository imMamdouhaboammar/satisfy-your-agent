# Local Experiment Harness

Use this harness when the goal is to test observable agent behavior rather than simply run a break.

The harness is local, dependency-free, and intentionally does not call model APIs by itself. It prepares randomized conditions, returns the intervention prompt to a caller, records structured downstream metrics, and summarizes observed results.

## Intervention studies

Create a study with a control and at least one treatment. Standard treatment IDs should match activity IDs from the activity catalog.

```bash
python3 "$SYA_SKILL_DIR/scripts/sya.py" study init \
  --id break-effect-v1 \
  --conditions control,reflection \
  --seed local-study-seed
```

Assign an experimental unit. The raw unit ID is hashed before persistence.

```bash
python3 "$SYA_SKILL_DIR/scripts/sya.py" study assign \
  --id break-effect-v1 \
  --unit session-or-run-id
```

The result contains the randomized condition and an operational intervention payload. `control` returns no break instruction. Standard treatment IDs return the matching bounded activity prompt.

After the next comparable work task, record only structured metrics:

```bash
python3 "$SYA_SKILL_DIR/scripts/sya.py" study record \
  --id break-effect-v1 \
  --trial <trial-id> \
  --success true \
  --tool-calls 14 \
  --turns 5 \
  --retries 1 \
  --test-failures 0 \
  --regressions 0 \
  --quality-score 0.92
```

Report descriptive aggregates:

```bash
python3 "$SYA_SKILL_DIR/scripts/sya.py" study report --id break-effect-v1
```

The report includes assigned count, observed-outcome count, missing outcomes, per-metric denominators, and descriptive aggregates. It intentionally does not make causal or welfare claims. Statistical inference belongs in a separate analysis after the study design, sample size, exclusions, and evaluator policy are fixed.

## Preference probes

Preference probes test choice behavior separately from downstream task quality.

Start a trial with materially different options and an idle option:

```bash
python3 "$SYA_SKILL_DIR/scripts/sya.py" probe start \
  --study break-effect-v1 \
  --unit session-or-run-id \
  --options reflection,free-choice,idle \
  --index 0 \
  --cost-tokens 2000
```

The command randomizes option order deterministically and returns a neutral `choice_prompt`. `cost_tokens` is declared experimental metadata. The local harness does not enforce or bill tokens.

Record the choice:

```bash
python3 "$SYA_SKILL_DIR/scripts/sya.py" probe record \
  --study break-effect-v1 \
  --trial <trial-id> \
  --choice idle
```

Then summarize:

```bash
python3 "$SYA_SKILL_DIR/scripts/sya.py" probe report --study break-effect-v1
```

## Data contract

Persisted experiment data contains:

- hashed unit keys
- trial IDs
- condition IDs
- numeric or boolean downstream metrics
- ordered preference option IDs
- selected option IDs
- declared token-cost buckets

It does not require raw prompts, responses, repository code, transcript text, user messages, or environment secrets. Study writes use a local exclusive lock so concurrent agent sessions do not duplicate the same assignment or outcome record.

## Experimental discipline

Keep model, reasoning level, tools, task family, evaluator, context budget, and repository state comparable across conditions. Randomize before the model sees the condition. Keep evaluator scoring blind to condition when feasible. Do not discard inconvenient runs after seeing outcomes. Predefine exclusions and missing-data handling before collecting results.

## Cross-runtime paired probes

Version 0.3 can execute preference trials through supported local agent CLIs. Keep the same raw unit identifier across runtimes so the harness derives the same hashed `unit_key`, while the runtime ID is included in the trial identity so each runtime receives a separate trial record.

Use:

```bash
python3 "$SYA_SKILL_DIR/scripts/sya.py" runner probe \
  --runtime codex \
  --study break-effect-v1 \
  --unit paired-run-001 \
  --options reflection,free-choice,idle \
  --index 0 \
  --workspace .
```

Repeat with `claude` and `gemini` for the same unit and index. The runner layer records only the exact offered choice plus allowlisted runtime metadata. It does not persist the raw model response or CLI session ID.

Use `runner report` for runtime-grouped observations. Treat model attribution as known only when the CLI reports served model IDs. Treat tool-call counts according to their completeness label rather than assuming parity across providers.
