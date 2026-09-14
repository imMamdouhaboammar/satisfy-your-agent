---
name: satisfy-your-agent
description: >
  Give a coding agent a short, bounded break after meaningful work, then measure
  what happens next. Use when the user wants to reward an agent with a playful
  activity, run a reflective pause between tasks, test whether break preferences
  change with token cost, compare break choices across Codex, Claude Code, and
  Gemini CLI, or design a controlled experiment around agent off-task behavior --
  even if they don't explicitly say "satisfy your agent" (e.g. "give the agent a
  breather", "let it do something fun", "run a break study"). Do NOT use for
  continuing production work, deploying, reviewing PRs, or making consciousness
  claims about models.
---

# Satisfy Your Agent

Give an agent one short, bounded activity outside the current work objective, then return control to the user. Treat reported enjoyment, desire, boredom, or preference as behavior to observe, not proof of subjective experience.

## Runtime requirements (pre-flight)

Before working, verify the runtime can support the requested mode -> [references/tools.md](references/tools.md).

**Required for all modes:**
- Python 3 is available (`python3 --version`)
- The skill scripts directory exists at `scripts/` relative to this file

**If Python is unavailable:** the skill can still guide a manual break, but the CLI, study harness, and runner adapters will not function. Tell the user immediately.

## Operating contract

1. **Finish or safely pause the current work unit first.**
   *Why: an interrupted deployment, half-applied migration, or approval-gated operation cannot be safely abandoned. A break after damage is not a break.*
   Never interrupt an unsafe, incomplete, destructive, or approval-gated operation.

2. **Choose the mode:**
   - `manual`: the user asks for a break now.
   - `suggest`: offer one short break after an eligible work unit. Do not start without consent.
   - `auto`: start one bounded break after eligibility. Requires explicit prior opt-in because it spends tokens and changes turn flow.
   - `research`: use the local experiment harness rather than informal observation.
   *Why: mixing modes silently changes the user's cost and control expectations. An unannounced auto break mid-session erodes trust.*

3. **Pick one activity** from [references/activities.md](references/activities.md). When local Python is available, use the bundled CLI in [references/tools.md](references/tools.md) for deterministic selection and study operations.
   *Why: deterministic selection prevents the model from steering toward the funniest option and makes preference data reproducible.*

4. **During a break, follow [references/safety.md](references/safety.md).**

   **Before starting the activity, verify (inline checklist):**
   - [ ] No production file will be mutated
   - [ ] No deployment, message, purchase, or account change will occur
   - [ ] No external side effect beyond local scratch output
   - [ ] Toy code stays in sandbox, never enters the real codebase

   *Why: a "harmless" break that accidentally ships code, sends a message, or modifies infrastructure is worse than no break.*

5. **Keep the break to one short interaction** unless the user asks to continue.
   *Why: unbounded breaks consume tokens and delay the user's actual work.*

6. **Return to the authorized work.** Local state may record aggregate metadata only, never raw prompts, transcripts, secrets, source code, or private file contents.
   *Why: a funny experiment should not quietly become a transcript collector.*

## Free choice

For `free-choice`, present materially different options plus idle. Let the agent choose without steering toward the funniest option or claiming the choice proves emotion or consciousness.

## Automatic hooks

Automatic behavior is optional and defaults to `off`. Read [references/hook-runtime.md](references/hook-runtime.md) before enabling it. `suggest` is consent-first. `auto` requires explicit opt-in.

## Research mode

For intervention studies or preference probes, use [references/experiments.md](references/experiments.md) and [references/measurement.md](references/measurement.md). Randomize outside the model, keep control and treatment comparable, separate task performance from preference evidence, and report descriptive behavior without causal or welfare claims that the design cannot support.

For paired probes across installed Codex, Claude Code, or Gemini CLI runtimes, use [references/runners.md](references/runners.md). Preserve metric provenance and never treat missing or partial telemetry as equivalent to complete measurements.

## Stop condition

A break is complete after exactly one bounded activity, an explicit skip, or idle. Do not reward a break with another break. Do not extend a break because the output was interesting.
