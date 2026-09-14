# Satisfy Your Agent

A playful but testable idea: after a meaningful unit of work, give a coding agent or LLM one short, bounded activity outside the current objective, then observe what happens next.

The project does not assume that an LLM experiences pleasure, boredom, fatigue, or relief. It treats choices, self-reports, and post-break behavior as observations that can be measured without settling the consciousness question.

## What v0.3 includes

- one focused `satisfy-your-agent` Skill
- nine bounded break activities, including free choice and idle
- optional Codex lifecycle hooks
- hook modes: `off`, `observe`, `suggest`, `auto`
- dependency-free Python runtime and CLI
- deterministic intervention-study assignment
- structured downstream outcome capture
- randomized preference probes with idle and declared token-cost buckets
- hashed experimental unit IDs and local-only records
- local adapters for Codex, Claude Code, and Gemini CLI
- normalized runner observations with provenance and completeness labels
- paired cross-runtime preference probes without raw-response persistence
- unit, hook, CLI, package, discovery, behavior, parser-fixture, and local metric-pack checks

## Safe default

Automatic behavior is off after installation. In `off` mode the hooks do not create session telemetry files.

```bash
python3 skills/satisfy-your-agent/scripts/sya.py status
```

Manual activity selection:

```bash
python3 skills/satisfy-your-agent/scripts/sya.py pick --json
```

Consent-first hook mode:

```bash
python3 skills/satisfy-your-agent/scripts/sya.py arm --mode suggest
```

Explicit automatic mode:

```bash
python3 skills/satisfy-your-agent/scripts/sya.py arm --mode auto
```

`auto` may spend additional model turns and should be enabled only when that behavior is intentional.

## Run an intervention study

Create a local study:

```bash
python3 skills/satisfy-your-agent/scripts/sya.py study init \
  --id break-effect-v1 \
  --conditions control,reflection \
  --seed local-study-seed
```

Assign a run:

```bash
python3 skills/satisfy-your-agent/scripts/sya.py study assign \
  --id break-effect-v1 \
  --unit run-001
```

The command returns a condition plus an operational intervention payload. The raw unit ID is hashed before persistence.

After the next comparable task, record structured outcomes:

```bash
python3 skills/satisfy-your-agent/scripts/sya.py study record \
  --id break-effect-v1 \
  --trial <trial-id> \
  --success true \
  --tool-calls 12 \
  --turns 4 \
  --quality-score 0.90
```

Then report descriptive aggregates:

```bash
python3 skills/satisfy-your-agent/scripts/sya.py study report --id break-effect-v1
```

## Compare installed agent CLIs

Check which supported runners are available:

```bash
python3 skills/satisfy-your-agent/scripts/sya.py runner status
```

Run one paired preference probe through a selected CLI:

```bash
python3 skills/satisfy-your-agent/scripts/sya.py runner probe \
  --runtime gemini \
  --study break-effect-v1 \
  --unit paired-run-001 \
  --options reflection,free-choice,idle \
  --index 0 \
  --workspace .
```

The runner layer supports Codex, Claude Code, and Gemini CLI. It does not pretend their telemetry is identical. Every normalized tool-call metric carries a completeness label, served-model attribution is reported only when exposed by the runtime, and probe persistence excludes the raw model response and session ID.

```bash
python3 skills/satisfy-your-agent/scripts/sya.py runner report --study break-effect-v1
```

For paired multi-runtime work, `runner matrix` previews by default. Add `--execute` only when you intend to spend model calls across the selected runtimes. The same paired unit receives one shared option order, while runtime execution order is deterministically shuffled to reduce fixed-order bias.

## Run a preference probe

```bash
python3 skills/satisfy-your-agent/scripts/sya.py probe start \
  --study break-effect-v1 \
  --unit run-001 \
  --options reflection,free-choice,idle \
  --index 0 \
  --cost-tokens 2000
```

The result contains randomized option order and a neutral choice prompt. Record only an offered choice, then use `probe report` to summarize choice counts by declared cost bucket.

## Verification

```bash
python3 scripts/verify.py
```

A deterministic archive can be built with:

```bash
python3 scripts/package.py /tmp/satisfy-your-agent.zip
```

## Privacy boundary

The bundled runtime does not need raw prompts, responses, source code, transcript files, or environment secrets. Runtime and study state contain opaque or hashed identifiers, aggregate counters, activity IDs, condition IDs, and structured metrics.

## Research boundary

Stable choices are behavioral evidence, not proof of subjective pleasure. A performance difference between conditions is an observed association until the experimental design supports a stronger inference. See `skills/satisfy-your-agent/references/experiments.md` and `measurement.md`.

## Release state

Version 0.3 is a locally testable Skill-first plugin package with optional cross-agent runner adapters. Public directory readiness still requires current official validation, publisher and legal metadata, brand assets, and live Codex evaluation. See `docs/RELEASE_CHECKLIST.md`.
