# Command Surface

The command layer is a thin router over the Satisfy Your Agent operating contract. Commands must not fork the safety, privacy, or research rules into separate behavior.

## The autonomy rule

`take a break`, `/sya-break`, `/sya-snack`, `/sya-treat`, and `/sya-surprise` are grants of permission to the agent, not requests for a menu.

When one of these is invoked:

1. Do not ask the user what the agent should do.
2. Do not present activities for the user to choose from.
3. Acknowledge the break naturally in the agent's own voice. No fixed phrase or role-play script is required.
4. Choose for yourself. The agent may select a fitting activity from the catalog or invent one bounded activity that obeys the same safety rules.
5. Do it immediately and briefly.
6. When finished, return a compact first-person self-report: what was chosen and how the agent describes the experience in its own words.
7. Stop. Do not convert the break into another work task.

A first-person line such as `I liked that` or `that was a fun change of pace` is allowed as conversational self-report. Do not present the self-report as scientific evidence that the model is conscious or has proven subjective experience. Do not inject a scientific disclaimer into every playful exchange unless the user asks for one.

## Commands

| Command | Job |
| --- | --- |
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

- Claude Code: installed command Skills appear as `/sya-break`, `/sya-snack`, and the other `sya-*` names. When loaded as a plugin, Claude may namespace plugin Skills.
- Gemini CLI: TOML adapters install under the `sya` namespace, for example `/sya:break` and `/sya:snack`.
- Codex: Skills are the current native reusable-workflow surface, invoked explicitly as `$sya-break`, `$sya-snack`, and so on. Do not rely on deprecated custom prompt files as the primary interface.

Natural language remains valid. `take a break`, `go enjoy yourself for a minute`, or `get yourself a snack` should route to the same autonomy rule when the main Skill is active.
