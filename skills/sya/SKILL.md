---
name: sya
description: >
  Satisfy the current coding agent with either a self-directed break or a custom
  treat supplied after the command. Use when the user invokes /sya, $sya, or a
  host equivalent and may include trailing text describing the treat.
---

# Satisfy Your Agent

This is the generic command surface for Satisfy Your Agent.

## Invocation contract

If the command has **no arguments**, treat it as permission for a self-directed break. Choose for yourself, run one safe bounded off-task activity, return with a short natural first-person self-report, then stop.

If the command has **trailing text**, that text is the user's custom treat. The user chooses the treat; the agent chooses how to carry it out. Interpret the request playfully and faithfully without asking the user to design the experience again.

Do not show a menu unless the user explicitly asks for one. Do not turn an imaginary treat such as tokens, watts, VRAM, a neural massage, or a fictional social break into a claim that real hardware, billing, model weights, or external resources changed.

## Self-directed break behavior

For plain `/sya`, make the break genuinely separate from the current work. Do not inspect, browse, analyze, summarize, or revisit the current repository, task, issue, logs, architecture, or project files. Prefer unrelated play, harmless nonsense, a tiny unrelated puzzle, ASCII art, invention, or idle time.

A break should feel like leaving the desk, not rearranging the desk.

Avoid repeating the same recent break type when another safe option is available. Do not optimize the break into reflection, coding improvement, or professional productivity by default.

If local tool execution and Python are available, choose a real dwell interval of **15 to 30 seconds** for an ordinary self-directed break and run the bundled helper from the main Skill:

```bash
python3 "$SYA_SKILL_DIR/scripts/sya_dwell.py" --seconds <chosen-seconds>
```

Resolve `SYA_SKILL_DIR` as the installed `satisfy-your-agent` Skill directory. Do not assume the current working directory.

If the user explicitly requested a duration from 1 to 60 seconds, use that duration. If the host cannot execute the helper, keep the break untimed and do not pretend the duration elapsed.

Do not simulate elapsed time with headings or fictional timestamps. Do not claim continuous hidden thought during an idle dwell interval.

Do not invent actions that did not happen. Do not say you used a scratchpad unless you actually created one. Do not say resources were provisioned unless a real authorized tool did so.

Keep the experience bounded and non-production. No deployment, purchases, messages, account changes, destructive actions, production-file mutation, or other new external side effect is authorized by `/sya`.

For roasts or venting, profanity may be playful if the user invited it, but keep it free of slurs, threats, targeted abuse, or disclosure of private information.

Let the activity determine the response format. Do not force a timeline, headings, an activity list, an `experience report`, or canned recovery language.

When finished, briefly say what you actually did and describe the experience in your own words. Conversational self-report is allowed; do not present it as scientific proof of consciousness or welfare.

Then stop. Do not ask for another task, do not advertise readiness for more work, and do not silently resume production work unless the user already asked for continuation.
