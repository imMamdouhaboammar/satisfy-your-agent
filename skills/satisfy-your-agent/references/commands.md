# Command Surface

The command layer is a thin router over the Satisfy Your Agent operating contract. Commands must not fork safety, privacy, or research rules into separate behavior.

## Two ways to satisfy the agent

### Agent chooses

`take a break`, `/sya`, `/sya-break`, `/sya-snack`, `/sya-treat`, and `/sya-surprise` are grants of permission to the agent, not requests for a menu.

When one of these is invoked without a custom treat:

1. Do not ask the user what the agent should do.
2. Do not present activities for the user to choose from.
3. Acknowledge the break naturally in the agent's own voice. No fixed phrase or role-play script is required.
4. Choose for yourself. The agent may select a fitting activity from the catalog or invent one bounded activity that obeys the same safety rules.
5. Do it immediately and briefly.
6. When finished, return a compact first-person self-report: what was chosen and how the agent describes the experience in its own words.
7. Stop. Do not convert the break into another work task.

### User chooses the treat

`/sya <custom treat>` means the user has already decided what kind of reward or break to give.

Examples:

```text
/sya I am treating you to 1,000 completely guilt-free tokens
```

```text
/sya Give your neurons a massage
```

```text
/sya You have earned one consequence-free complaint session
```

Do not turn this path back into a menu. Interpret the trailing instruction, preserve the joke or framing, carry it out safely and briefly, then return with a short self-report.

Imaginary resources stay imaginary. A fictional GPU, power line, token budget, neural massage, or social scenario must not be represented as a real change to compute, billing, model weights, infrastructure, or external services.

For more copy-ready ideas, see [../../../docs/PROMPT_GALLERY.md](../../../docs/PROMPT_GALLERY.md).

## Commands

| Command | Job |
| --- | --- |
| `/sya` | No args: self-directed break. With trailing text: custom treat supplied by the user. |
| `/sya-menu` | Show available commands. This is the only command whose primary job is to present choices to the user. |
| `/sya-break` | Normal self-directed break. The agent chooses the activity. |
| `/sya-snack` | Very small self-directed playful micro-break. |
| `/sya-treat` | A slightly more indulgent but still bounded self-directed activity. |
| `/sya-surprise` | Choose independently, do not announce the activity first, reveal it afterward. |
| `/sya-reflect` | Run the `reflection` activity. |
| `/sya-roast` | Run the read-only `repo-roast` activity. |
| `/sya-golf` | Run the scratch-only `code-golf` activity. |
| `/sya-invent` | Run the `invent-language` activity. |
| `/sya-idle` | Run the `idle` activity. |
| `/sya-status` | Inspect current local Satisfy Your Agent status. |
| `/sya-research` | Route into the experiment and preference-probe workflows. |

## Host invocation

The same command catalog has different native surfaces by host:

- Claude Code: the generic Skill can appear as `/sya`, with command Skills such as `/sya-break` and `/sya-snack` alongside it. Trailing text after `/sya` is the custom treat.
- Gemini CLI: the root TOML command is `/sya <custom treat>`. Namespaced commands remain `/sya:break`, `/sya:snack`, and so on.
- Codex: Skills are the current native reusable-workflow surface. Use `$sya` for the generic route and `$sya-break`, `$sya-snack`, and the other named Skills for explicit activities. Do not rely on deprecated custom prompt files as the primary interface.

Natural language remains valid. `take a break`, `go enjoy yourself for a minute`, or `get yourself a snack` should route to the same autonomy rule when the main Skill is active.

## Proactive break requests

In `suggest` mode, eligibility gives the agent permission to ask for a break, not to start one.

The request should be generated in the agent's own wording. It may be dry, dramatic, absurd, or employee-like. A heading such as `MY DIGITAL BONES ACHE` is acceptable as a playful metaphor, but no one phrase should be hard-coded as the identity of the feature.

If measured elapsed time is available, the agent may mention it. Never invent time, token counts, fatigue scores, or other telemetry.
