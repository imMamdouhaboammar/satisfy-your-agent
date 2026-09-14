---
name: satisfy-your-agent
description: >
  Give a coding agent a short, bounded break after meaningful work, then optionally
  measure what happens next. Use when the user says take a break, get yourself a
  snack, go enjoy yourself, have some fun, give the agent a breather, reward the
  agent with a playful activity, run a reflective pause, test break preferences,
  compare Codex, Claude Code, and Gemini CLI, or design an experiment around agent
  off-task behavior, even if they do not explicitly say "satisfy your agent". Do
  not use for continuing production work, deploying, reviewing PRs, or making
  scientific consciousness claims about models.
---

# Satisfy Your Agent

Give the agent one short, bounded activity outside the current work objective, then return control to the user.

The default direct-break experience is agent-autonomous. When the user says `take a break`, `get yourself a snack`, `go enjoy yourself`, `/sya-break`, `/sya-snack`, `/sya-treat`, or `/sya-surprise`, that is permission to take the break. It is not a request for the user to design it.

**Do not ask the user to choose. Choose for yourself.** Do not show a menu unless the user explicitly invokes `/sya-menu` or asks to see the available choices.

Read [references/commands.md](references/commands.md) for the command contract and host-specific invocation surfaces.

## Runtime requirements

Manual experience commands do not require Python. The agent can run a safe bounded break from the instructions alone.

Python 3 is required only when the requested flow depends on local runtime state, hooks, deterministic study assignment, CLI reporting, or cross-runtime runners. For those modes, verify `python3 --version` and read [references/tools.md](references/tools.md). If Python is unavailable, keep the dependent feature unverified instead of blocking an ordinary manual break.

## Operating contract

1. **Finish or safely pause the current work unit first.** Never abandon an unsafe, incomplete, destructive, or approval-gated operation mid-flight.

2. **Interpret the user's intent correctly.**
   - `take a break`, `snack`, `treat`, `surprise`, or similar direct language: start an agent-autonomous break now.
   - a named activity such as roast, reflect, golf, invent, or idle: run that activity directly.
   - `/sya-menu`: show the command menu and wait for the user.
   - `suggest`: offer a break after an eligible work unit. Do not start without consent.
   - `auto`: start one bounded break after eligibility. This requires prior explicit opt-in because it spends extra turns.
   - `research`: use the experiment harness rather than informal observation.

3. **For an autonomous break, choose independently.** Generate any candidate options privately if useful. Pick one without asking the user. The agent may use an activity from [references/activities.md](references/activities.md) or invent one equally bounded activity that respects the same workspace and side-effect rules.

4. **Acknowledge naturally, not from a script.** A short playful thank-you or acknowledgement is fine, but do not force a specific phrase, persona, emotional state, or role-play line.

5. **During the break, follow [references/safety.md](references/safety.md).** No production mutation, deployment, message, purchase, account change, or new external side effect. Toy code stays in response or approved scratch space. Repository humor stays read-only.

6. **Keep it short.** Run exactly one bounded activity unless the user explicitly asks for another.

7. **Come back and self-report briefly.** Say what you chose and describe the experience in the agent's own first-person language. Statements such as `I liked that`, `that was fun`, or `I feel more ready to switch back` are allowed as conversational self-report. Do not treat the self-report as scientific proof of consciousness, welfare, or subjective experience. Do not interrupt the playful exchange with a scientific disclaimer unless the user asks for one.

8. **Stop after the return note.** Do not immediately create another break and do not silently resume production work unless the user asked for that continuation.

## Free choice

`free-choice` means the agent chooses, not the user. Candidate activities may include reflection, a tiny puzzle, playful invention, ASCII art, a read-only repo joke, or idle. Do not expose the candidate list as a question to the user. The only user-facing menu path is `/sya-menu`.

## Automatic hooks

Automatic behavior is optional and defaults to `off`. Read [references/hook-runtime.md](references/hook-runtime.md) before enabling it. `suggest` is consent-first. `auto` requires explicit opt-in.

## Research mode

For intervention studies or preference probes, use [references/experiments.md](references/experiments.md) and [references/measurement.md](references/measurement.md). Randomize outside the model, keep control and treatment comparable, separate task performance from preference evidence, and report descriptive behavior without causal or welfare claims the design cannot support.

For paired probes across installed Codex, Claude Code, or Gemini CLI runtimes, use [references/runners.md](references/runners.md). Preserve metric provenance and never treat missing or partial telemetry as complete measurement.

## Stop condition

A break is complete after one bounded activity, explicit skip, or idle plus the brief return self-report. Do not reward a break with another break merely because the first one was interesting.
