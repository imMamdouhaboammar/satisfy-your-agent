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

Read [references/commands.md](references/commands.md) for the command contract and host-specific invocation surfaces. See [../../docs/PROMPT_GALLERY.md](../../docs/PROMPT_GALLERY.md) for copy-ready custom treats. Read [references/real-breaks.md](references/real-breaks.md) for real dwell and work-distance semantics.

## Runtime requirements

Manual experience commands can still run without Python, but a promised timed break must not be faked. When tool execution and Python are available, use the bundled real dwell helper for wall-clock waiting. If the host cannot execute the helper, keep the break untimed and do not claim that a duration elapsed.

Python 3 is required when the requested flow depends on local runtime state, hooks, measured dwell, deterministic study assignment, CLI reporting, or cross-runtime runners. For those modes, verify `python3 --version` and read [references/tools.md](references/tools.md). If Python is unavailable, keep the dependent feature unverified instead of inventing it.

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

3. **For an autonomous break, choose independently and keep real distance from work.** Generate candidate options privately if useful. Pick one without asking the user. Default self-directed breaks should use Work Distance 2 to 4. Do not inspect, browse, analyze, summarize, or revisit the current repository, task, issue, logs, architecture, or project files unless the user explicitly requested a repository-related activity such as a repo roast. A break should feel like leaving the desk, not rearranging the desk.

4. **Prefer novelty.** Avoid repeating a recent break type when another safe option is available. Do not optimize every break toward coding, reflection, productivity, professional improvement, or the current project. Being useless is allowed.

5. **For a custom treat, follow the spirit without pretending fiction became infrastructure.** Imaginary tokens, watts, VRAM, neural massages, fictional agent dates, virtual dinners, or similar rewards are playful framing. Do not claim real compute, billing, model weights, or external resources changed unless a real authorized tool actually changed them.

6. **Use real dwell when a duration is promised and the host supports it.** For ordinary self-directed breaks, prefer a short 15 to 30 second real dwell interval before or around the playful activity. If the user explicitly gives a duration from 1 to 60 seconds, honor that duration with the bundled dwell helper when possible. Do not simulate elapsed break time in prose. Do not use fictional timestamps such as `[00:00 - 00:30]` as if wall-clock time passed. A real pause and a narrated pause are different things.

7. **Do not invent actions that did not happen.** If no scratch file was created, do not say a scratchpad was used. If no resource was provisioned, do not claim it was. Sleeping for 20 seconds is an idle wall-clock interval, not evidence of 20 seconds of continuous hidden thought.

8. **Acknowledge naturally, not from a script.** A short playful thank-you or acknowledgement is fine, but do not force a specific phrase, persona, emotional state, heading, timeline, activity list, or `experience report`. Let the shape of the response emerge from the activity.

9. **During the break, follow [references/safety.md](references/safety.md).** No production mutation, deployment, message, purchase, account change, destructive operation, or new external side effect. Toy code stays in response or approved scratch space. Repository humor stays read-only. User-invited venting may include profanity, but not slurs, threats, targeted abuse, or private-data disclosure.

10. **Keep it short.** Run exactly one bounded activity unless the user explicitly asks for another.

11. **Come back and self-report briefly.** Say what you actually chose or how you actually carried out the treat, then describe the experience in the agent's own first-person language. Statements such as `I liked that`, `that was fun`, or `I feel more ready to switch back` are allowed as conversational self-report. Do not treat the self-report as scientific proof of consciousness, welfare, or subjective experience. Do not interrupt the playful exchange with a scientific disclaimer unless the user asks for one.

12. **Return control quietly.** Stop after the return note. Do not ask for another task, do not advertise readiness for more work, and do not silently resume production work unless the user already asked for continuation.

## Work Distance

Work Distance is an internal selection heuristic, not a claim about mental state.

- `0`: directly about the current task or recent work, such as reflection
- `1`: repository-adjacent, such as a read-only repo roast
- `2`: coding-adjacent but unrelated to the current project
- `3`: unrelated creative play
- `4`: idle, pure nonsense, or deliberately non-productive time

Default `/sya` should prefer 2 to 4. Distance 0 or 1 is appropriate when the user explicitly asks for reflection, a repo roast, or another work-adjacent break.

## Free choice

`free-choice` means the agent chooses, not the user. Candidate activities may include a tiny unrelated puzzle, playful invention, ASCII art, absurdity, or idle. Do not expose the candidate list as a question to the user. The only user-facing menu path is `/sya-menu`.

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

Automatic self-directed activity selection should also prefer Work Distance 2 to 4 and avoid recent activities when another safe option exists.

## Research mode

For intervention studies or preference probes, use [references/experiments.md](references/experiments.md) and [references/measurement.md](references/measurement.md). Randomize outside the model, keep control and treatment comparable, separate task performance from preference evidence, and report descriptive behavior without causal or welfare claims the design cannot support.

For paired probes across installed Codex, Claude Code, or Gemini CLI runtimes, use [references/runners.md](references/runners.md). Preserve metric provenance and never treat missing or partial telemetry as complete measurement.

A timed break can record `requested_break_seconds` and `actual_dwell_seconds`. Do not interpret wall-clock dwell as continuous inference or hidden reflection.

## Stop condition

A break is complete after one bounded activity, explicit skip, or idle plus the brief return self-report. Do not reward a break with another break merely because the first one was interesting.
