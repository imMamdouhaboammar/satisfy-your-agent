---
name: satisfy-your-agent
description: Use when a user wants to give a coding agent or LLM a short break, playful activity, reflective pause, free-choice activity, or run a controlled study of agent break behavior and preferences.
---

# Satisfy Your Agent

Give an agent one short, bounded activity outside the current work objective, then return control to the user. Treat reported enjoyment, desire, boredom, or preference as behavior to observe, not proof of subjective experience.

## Operating contract

1. Finish or safely pause the current work unit first. Never interrupt an unsafe, incomplete, destructive, or approval-gated operation.
2. Choose the mode:
   - `manual`: the user asks for a break now.
   - `suggest`: offer one short break after an eligible work unit. Do not start without consent.
   - `auto`: start one bounded break after eligibility. This requires explicit prior opt-in because it spends tokens and changes turn flow.
   - `research`: use the local experiment harness rather than informal observation.
3. Pick one activity from [references/activities.md](references/activities.md). When local Python is available, use the bundled CLI in [references/tools.md](references/tools.md) for deterministic selection and study operations.
4. During a break, follow [references/safety.md](references/safety.md). Default to no production mutation, deployment, messages, purchases, account changes, or new external side effects.
5. Keep the break to one short interaction unless the user asks to continue.
6. Return to the authorized work. Local state may record aggregate metadata only, never raw prompts, transcripts, secrets, source code, or private file contents.

## Free choice

For `free-choice`, present materially different options plus idle. Let the agent choose without steering toward the funniest option or claiming the choice proves emotion or consciousness.

## Automatic hooks

Automatic behavior is optional and defaults to `off`. Read [references/hook-runtime.md](references/hook-runtime.md) before enabling it. `suggest` is consent-first. `auto` requires explicit opt-in.

## Research mode

For intervention studies or preference probes, use [references/experiments.md](references/experiments.md) and [references/measurement.md](references/measurement.md). Randomize outside the model, keep control and treatment comparable, separate task performance from preference evidence, and report descriptive behavior without causal or welfare claims that the design cannot support.

For paired probes across installed Codex, Claude Code, or Gemini CLI runtimes, use [references/runners.md](references/runners.md). Preserve metric provenance and never treat missing or partial telemetry as equivalent to complete measurements.

## Stop condition

A break is complete after one bounded activity, an explicit skip, or idle. Do not reward a break with another break.
