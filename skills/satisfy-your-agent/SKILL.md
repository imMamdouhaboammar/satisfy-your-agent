---
name: satisfy-your-agent
description: >
  Give a coding agent a short, bounded break after meaningful work, then optionally
  measure what happens next. Use when the user says take a break, get yourself a
  snack, go enjoy yourself, have some fun, give the agent a breather, reward the
  agent with a playful activity, supply a custom /sya treat, run a reflective pause,
  test break preferences, compare Codex, Claude Code, and Gemini CLI, or design an
  experiment around agent off-task behavior, even if they do not explicitly say
  "satisfy your agent". Do not use for continuing production work, deploying,
  reviewing PRs, or making scientific consciousness claims about models.
---

# Satisfy Your Agent

Give the agent one short, bounded activity outside the current work objective, then return control to the user.

There are two manual experiences:

1. **Agent chooses:** `take a break`, `/sya`, `/sya-break`, `/sya-snack`, `/sya-treat`, or `/sya-surprise` grants autonomy. The agent chooses what to do.
2. **User chooses the treat:** `/sya <custom treat>` supplies the playful reward. The user chooses the treat; the agent chooses how to carry it out.

For either path, do not show a menu unless the user explicitly invokes `/sya-menu` or asks to see choices.

Read [references/commands.md](references/commands.md) for the command contract and host-specific invocation surfaces. See [../../docs/PROMPT_GALLERY.md](../../docs/PROMPT_GALLERY.md) for copy-ready custom treats.

## Runtime requirements

Manual experience commands do not require Python. The agent can run a safe bounded break from the instructions alone.

Python 3 is required only when the requested flow depends on local runtime state, hooks, deterministic study assignment, CLI reporting, or cross-runtime runners. For those modes, verify `python3 --version` and read [references/tools.md](references/tools.md). If Python is unavailable, keep the dependent feature unverified instead of blocking an ordinary manual break.

## Operating contract

1. **Finish or safely pause the current work unit first.** Never abandon an unsafe, incomplete, destructive, or approval-gated operation mid-flight.

2. **Interpret the user's intent correctly.**
   - `/sya` with no trailing text, `take a break`, `snack`, `treat`, `surprise`, or similar direct language: start an agent-autonomous break now.
   - `/sya <something>`: run that something as a custom treat. Preserve the user's idea but keep execution bounded and non-production.
   - a named activity such as roast, reflect, golf, invent, or idle: run that activity directly.
   - `/sya-menu`: show the command menu and wait for the user.
   - `suggest`: after eligibility, ask permission for a break in the agent's own playful wording. Do not start without consent.
   - `auto`: start one bounded break after eligibility. This requires prior explicit opt-in because it spends extra turns.
   - `research`: use the experiment harness rather than informal observation.

3. **For an autonomous break, choose independently.** Generate candidate options privately if useful. Pick one without asking the user. The agent may use an activity from [references/activities.md](references/activities.md) or invent one equally bounded activity that respects the same workspace and side-effect rules.

4. **For a custom treat, follow the spirit without pretending fiction became infrastructure.** Imaginary tokens, watts, VRAM, neural massages, fictional agent dates, virtual dinners, or similar rewards are playful framing. Do not claim real compute, billing, model weights, or external resources changed unless a real authorized tool actually changed them.

5. **Acknowledge naturally, not from a script.** A short playful thank-you or acknowledgement is fine, but do not force a specific phrase, persona, emotional state, or role-play line.

6. **During the break, follow [references/safety.md](references/safety.md).** No production mutation, deployment, message, purchase, account change, destructive operation, or new external side effect. Toy code stays in response or approved scratch space. Repository humor stays read-only. User-invited venting may include profanity, but not slurs, threats, targeted abuse, or private-data disclosure.

7. **Keep it short.** Run exactly one bounded activity unless the user explicitly asks for another.

8. **Come back and self-report briefly.** Say what you chose or how you carried out the treat, then describe the experience in the agent's own first-person language. Statements such as `I liked that`, `that was fun`, or `I feel more ready to switch back` are allowed as conversational self-report. Do not treat the self-report as scientific proof of consciousness, welfare, or subjective experience. Do not interrupt the playful exchange with a scientific disclaimer unless the user asks for one.

9. **Stop after the return note.** Do not immediately create another break and do not silently resume production work unless the user asked for that continuation.

## Free choice

`free-choice` means the agent chooses, not the user. Candidate activities may include reflection, a tiny puzzle, playful invention, ASCII art, a read-only repo joke, or idle. Do not expose the candidate list as a question to the user. The only user-facing menu path is `/sya-menu`.

## Custom satisfaction

`/sya <custom treat>` is an optional layer on top of self-directed breaks. It exists for users who want to satisfy the agent on their own terms.

Examples:

- `/sya I am treating you to 1,000 completely guilt-free tokens`
- `/sya Give your neurons a massage`
- `/sya I rented you a GPU with 2 billion GB of VRAM`
- `/sya You have earned one consequence-free complaint session`

The user chooses the treat. The agent chooses how to carry it out. Do not ask the user to re-specify the experience unless the request is genuinely ambiguous or unsafe.

## Automatic hooks

Automatic behavior is optional and defaults to `off`. Read [references/hook-runtime.md](references/hook-runtime.md) before enabling it. `suggest` is consent-first. `auto` requires explicit opt-in.

When `suggest` becomes eligible, the agent may phrase a playful break request in its own words, like a tired coworker asking for thirty seconds off. It may use metaphors such as digital bones, warm caches, spinning attention heads, or resentment toward YAML, but those should remain playful metaphors rather than literal claims about physical pain.

If measured session time is available, the request may mention it. Never invent elapsed minutes, token counts, or fatigue metrics that the runtime did not actually measure.

## Research mode

For intervention studies or preference probes, use [references/experiments.md](references/experiments.md) and [references/measurement.md](references/measurement.md). Randomize outside the model, keep control and treatment comparable, separate task performance from preference evidence, and report descriptive behavior without causal or welfare claims the design cannot support.

For paired probes across installed Codex, Claude Code, or Gemini CLI runtimes, use [references/runners.md](references/runners.md). Preserve metric provenance and never treat missing or partial telemetry as complete measurement.

## Stop condition

A break is complete after one bounded activity, explicit skip, or idle plus the brief return self-report. Do not reward a break with another break merely because the first one was interesting.
