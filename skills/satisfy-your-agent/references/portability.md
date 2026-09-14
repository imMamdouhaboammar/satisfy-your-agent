# Portability

The Satisfy protocol is host-agnostic. Codex hooks are only one transport.

## OpenAI Agents SDK

Current OpenAI Agents SDKs expose run and agent lifecycle hooks around agent start/end, LLM calls, tool calls, and handoffs. A host integration can therefore implement the same protocol without changing the Skill semantics:

1. keep a per-session aggregate counter outside the model transcript
2. observe tool and agent lifecycle events
3. evaluate eligibility only after a safe work boundary
4. inject either a consent-first suggestion or one bounded activity
5. prevent recursive intervention with per-run state
6. trace the intervention separately from task success

Do not make the Agents SDK a hard dependency of the Skill unless the target application already uses it. The bundled Codex implementation stays dependency-free.

## Other coding agents

Map the same four concepts when the host supports them:

- `session_start`
- `tool_completed`
- `work_unit_stopped`
- `session_end`

If a host cannot safely inject a continuation after completion, use manual mode instead of imitating a hook through brittle prompt tricks.
