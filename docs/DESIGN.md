# Satisfy Your Agent Design

## Product outcome

A user can give an LLM or coding agent one short, safe, opt-in activity outside the current work objective, or run a local behavioral experiment around that intervention, then regain control without silently changing production state.

## Why this can be useful without assuming feelings

A break-like intervention can alter context, objective framing, reflection, or choice behavior. The project measures observable effects without claiming they prove subjective experience.

## Version 0.3 milestone

Version 0.3 supports:

- explicit manual invocation through one Skill
- nine bounded activity types
- optional lifecycle hooks with `off`, `observe`, `suggest`, and `auto`
- aggregate local counters only
- deterministic local study assignment
- structured downstream outcome metrics
- randomized preference probes
- descriptive reports by condition and declared cost bucket
- optional Codex, Claude Code, and Gemini CLI runner adapters
- paired cross-runtime preference probes
- normalized runner observations with explicit provenance and completeness
- package, runtime, privacy, and experiment tests

## Non-goals

Version 0.3 does not:

- diagnose consciousness or sentience
- claim model welfare outcomes
- mutate production repositories during a break
- require an MCP server or external service
- upload telemetry
- persist raw transcripts or task prompts
- run statistical significance tests automatically
- auto-enable token-consuming continuations after installation

## Components

### Skill

`skills/satisfy-your-agent/SKILL.md` owns the workflow and safety contract. Progressive details live under `references/`.

### Local runtime

`sya_core.py` stores break configuration and aggregate session counters. `sya_experiment.py` owns study randomization, structured outcome records, preference trials, runner observations, and descriptive summaries. `sya_runners.py` owns local CLI adapters and output normalization. `sya.py` provides the CLI surface.

### Hooks

Codex lifecycle hooks observe local tool calls and Stop events. They are behaviorally inert while `hook_mode=off`. The experiment harness is explicit CLI state and does not silently activate hooks.

### Evals

Static package tests protect defaults and privacy boundaries. Study fixtures document repeatable starting designs. Discovery prompts and behavior scenarios support live evaluation when a compatible runner is available.

## Data flow

```text
manual or hook break
  -> bounded activity
  -> return control

research study
  -> create study
  -> hash unit id
  -> deterministic condition assignment
  -> caller applies control or intervention
  -> comparable next task
  -> record structured outcomes
  -> descriptive report
```

cross-runtime preference study
  -> create one paired unit
  -> runtime-specific trial id
  -> invoke read-only or plan-mode runner
  -> extract exact offered choice
  -> discard raw response from persisted state
  -> persist allowlisted runner observation
  -> compare only provenance-compatible metrics

Raw transcript text is not required by any path.
