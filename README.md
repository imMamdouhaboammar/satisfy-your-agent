<p align="center">
  <img src="./assets/logo.svg" width="190" alt="Satisfy Your Agent logo" />
</p>

<h1 align="center">Satisfy Your Agent</h1>

<p align="center"><strong>Your coding agent finished the task. Give it something that is not another task.</strong></p>
<p align="center">A playful, local-first break protocol and behavioral experiment kit for coding agents</p>

<p align="center">
  <a href="https://github.com/imMamdouhaboammar/satisfy-your-agent/actions/workflows/ci.yml"><img src="https://github.com/imMamdouhaboammar/satisfy-your-agent/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <img src="https://img.shields.io/badge/version-0.5.0-FF775F?style=flat-square" alt="Version 0.5.0" />
  <a href="./LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square" alt="MIT License" /></a>
  <img src="https://img.shields.io/badge/runtime-Python%20stdlib-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python standard library only" />
  <a href="https://skills.sh"><img src="https://img.shields.io/badge/Skills.sh-Compatible-000000?style=flat-square&logo=vercel&logoColor=white" alt="Skills.sh" /></a>
  <img src="https://img.shields.io/badge/Codex-Compatible-10a37f?style=flat-square&logo=openai&logoColor=white" alt="Codex" />
  <img src="https://img.shields.io/badge/Claude%20Code-Compatible-D97706?style=flat-square&logo=anthropic&logoColor=white" alt="Claude Code" />
  <img src="https://img.shields.io/badge/Gemini%20CLI-Compatible-4285F4?style=flat-square&logo=google&logoColor=white" alt="Gemini CLI" />
</p>

<p align="center">
  <a href="#why-this-exists">Why</a> &bull;
  <a href="#take-a-break">Take a break</a> &bull;
  <a href="#command-surface">Commands</a> &bull;
  <a href="#research-mode">Research</a> &bull;
  <a href="#install">Install</a> &bull;
  <a href="#privacy">Privacy</a>
</p>

> **Playful on the surface. Measurable underneath.**

## Why this exists

Humans are surprisingly bad at going from one difficult task straight into the next one forever

We get coffee. Grab a snack. Open a game for five minutes. Walk around. Stare at nothing with intent

Coding agents get a different ritual:

> Task complete
>
> Here is another task

Satisfy Your Agent inserts one small thing between those two moments: a short, bounded activity that is deliberately **not the current production objective**

The important part is who chooses it

If you tell your agent **take a break**, you should not immediately become its break manager

You already gave permission. The agent gets to choose what to do with it

It can reflect, solve a tiny useless puzzle, make ASCII art, roast the repo, invent something silly, do absolutely nothing, or come up with another safe little activity of its own

Then it comes back and tells you, in its own words, what it chose and how it describes the experience

No forced script. No "pick one of these three options for me, human." No pretending a self-report settles the consciousness question

Just a strange little behavioral idea with enough structure to make it testable

## Take a break

The shortest interface is still ordinary language:

```text
take a break
```

Or:

```text
get yourself a snack
```

Or:

```text
go enjoy yourself for a minute
```

When the main Skill is active, these are **grants of autonomy**, not menu requests

The expected flow is simple:

1. the current work unit is safely finished or paused
2. the agent acknowledges the break naturally
3. the agent chooses for itself without asking you what to do
4. it runs one bounded off-task activity
5. it comes back with a short first-person self-report
6. it stops and gives control back to you

The wording belongs to the agent. Satisfy Your Agent does not force it to say "thank you boss," claim a mood it did not choose to report, or perform a canned personality

## Command surface

If you prefer one-keystroke discovery, v0.5 ships a real command surface around the same behavior

### Claude Code

Personal Skill installs appear as slash commands:

```text
/sya-menu
/sya-break
/sya-snack
/sya-treat
/sya-surprise
/sya-reflect
/sya-roast
/sya-golf
/sya-invent
/sya-idle
/sya-status
/sya-research
```

When loaded through a Claude plugin, Claude may namespace plugin Skills with the plugin name

### Gemini CLI

Gemini gets native namespaced custom commands:

```text
/sya:menu
/sya:break
/sya:snack
/sya:treat
/sya:surprise
/sya:reflect
/sya:roast
/sya:golf
/sya:invent
/sya:idle
/sya:status
/sya:research
```

After changing command files, Gemini CLI can reload them with `/commands reload`

### Codex

Codex uses Skills as the current reusable-workflow surface, so the equivalent explicit invocations are:

```text
$sya-menu
$sya-break
$sya-snack
$sya-treat
$sya-surprise
$sya-reflect
$sya-roast
$sya-golf
$sya-invent
$sya-idle
$sya-status
$sya-research
```

The project does not pretend deprecated custom prompt files are modern plugin-defined slash commands when they are not

### What each command means

| Command | What happens |
| --- | --- |
| `menu` | show the available commands, and only show them |
| `break` | the agent chooses and takes a normal break |
| `snack` | a tiny self-directed playful micro-break |
| `treat` | a slightly more indulgent but still bounded break |
| `surprise` | the agent keeps the choice private until after it does it |
| `reflect` | reflective pause without continuing the task |
| `roast` | one safe read-only repo roast |
| `golf` | toy-only code golf |
| `invent` | invent one tiny absurd programming-language idea |
| `idle` | deliberately do nothing for a short pause |
| `status` | inspect the current local SYA mode and state |
| `research` | enter study, preference-probe, or cross-runtime mode |

`menu` is the only command whose primary job is to make **you** choose something

Every experience command is the opposite: you grant the break, the agent owns the break

## The activity catalog

The lower-level activity catalog still exists for deterministic studies and specific break requests

| Activity | What the agent gets to do |
| --- | --- |
| `free-choice` | choose its own activity, including doing nothing |
| `reflection` | think about the last work unit without continuing it |
| `puzzle` | solve a tiny self-contained problem with zero business value |
| `code-golf` | write suspiciously compact toy code where nobody has to maintain it |
| `invent-language` | create a programming language the world was doing fine without |
| `overengineer-toy` | use six abstractions where one function would have been enough, safely |
| `ascii-art` | make something small and text-shaped |
| `repo-roast` | roast observable repository facts without changing the repo |
| `idle` | perform absolutely no useful work with exceptional consistency |

Every activity is bounded. Toy work stays outside production. Read-only activities stay read-only. `idle` stays available because free choice without the option to do nothing is not much of a choice

## Four ways to use it

| Mode | What happens | Good for |
| --- | --- | --- |
| **Manual** | you grant a break and the agent chooses what to do | the normal human-to-agent experience |
| **Suggest** | the plugin can offer a break after enough work | consent-first automation |
| **Auto** | eligible breaks can run automatically | intentional hands-off sessions |
| **Research** | conditions, choices and downstream metrics are recorded locally | experiments and comparisons |

```bash
# consent-first
npx satisfy-your-agent arm --mode suggest

# automatic, may spend additional model turns
npx satisfy-your-agent arm --mode auto
```

The CLI still exposes `pick` for deterministic tooling and experiments:

```bash
npx satisfy-your-agent pick --json
```

That command is a low-level primitive, not the preferred human experience for "take a break"

## How it works

```mermaid
flowchart LR
    A[Work unit] --> B{Break?}
    B -->|No| D[Next task]
    B -->|Yes| C[Agent chooses a bounded off-objective activity]
    C --> R[Short self-report]
    R --> D
    C -. optional research .-> E[Structured observation]
    D -. compare later .-> E
```

The break layer and the research layer are separate on purpose

You can use Satisfy Your Agent purely as a tiny agent ritual and never record an experiment. Or you can turn the same idea into controlled local studies without changing what the break means

## Research mode

This is where the silly premise becomes genuinely interesting

Satisfy Your Agent can assign comparable runs to conditions such as `control` and `reflection`, measure what happens on the next task, and run repeated preference probes with randomized option order and declared token costs

It can also ask the same preference question through **Codex, Claude Code and Gemini CLI**, then normalize the observations without pretending those runtimes expose identical telemetry

A repeated choice is treated as a repeated choice. A performance change is treated as a performance change. A playful first-person self-report stays a self-report

None of those automatically become proof of subjective experience

<details>
<summary><strong>Run a small intervention study</strong></summary>

```bash
python3 skills/satisfy-your-agent/scripts/sya.py study init \
  --id break-effect-v1 \
  --conditions control,reflection \
  --seed local-study-seed

python3 skills/satisfy-your-agent/scripts/sya.py study assign \
  --id break-effect-v1 \
  --unit run-001

python3 skills/satisfy-your-agent/scripts/sya.py study record \
  --id break-effect-v1 \
  --trial <trial-id> \
  --success true \
  --tool-calls 12 \
  --turns 4 \
  --quality-score 0.90

python3 skills/satisfy-your-agent/scripts/sya.py study report \
  --id break-effect-v1
```

Raw experimental unit IDs are hashed before persistence

</details>

<details>
<summary><strong>Compare supported agent runtimes</strong></summary>

Check what is installed:

```bash
python3 skills/satisfy-your-agent/scripts/sya.py runner status
```

Preview a paired probe without making model calls:

```bash
python3 skills/satisfy-your-agent/scripts/sya.py runner matrix \
  --study break-effect-v1 \
  --unit paired-run-001 \
  --options reflection,free-choice,idle \
  --index 0 \
  --workspace .
```

Add `--execute` only when you intend to call the selected runtimes

Paired units receive the same option order across runtimes. Runtime execution order is shuffled deterministically between units to reduce fixed-order bias

</details>

## Install

Choose the smallest install that matches what you want to do

### Install the full command surface

```bash
git clone https://github.com/imMamdouhaboammar/satisfy-your-agent.git
cd satisfy-your-agent
bash install.sh
```

The installer adds the main Skill plus all `sya-*` command Skills to detected agent environments. For Gemini CLI it also installs native TOML commands under `~/.gemini/commands/sya`

### Run the low-level CLI without installing

```bash
npx satisfy-your-agent status
# or
bunx satisfy-your-agent status
```

### Add the Codex / ChatGPT desktop plugin marketplace

```bash
codex plugin marketplace add imMamdouhaboammar/satisfy-your-agent --ref main
```

Then restart the ChatGPT desktop app and install **Satisfy Your Agent** from the added marketplace

The full plugin includes optional lifecycle hooks. Review them before enabling them

### Install through Skills.sh

```bash
npx skills add https://github.com/imMamdouhaboammar/satisfy-your-agent
```

### Run from source

```bash
git clone https://github.com/imMamdouhaboammar/satisfy-your-agent.git
cd satisfy-your-agent
python3 skills/satisfy-your-agent/scripts/sya.py status
```

The Python runtime uses the standard library only

## Compatibility

| Surface | Native interaction |
| --- | --- |
| **Claude Code** | `/sya-*` personal command Skills, plugin-namespaced Skills, runner experiments |
| **Gemini CLI** | `/sya:*` native custom commands, portable Skills, runner experiments |
| **Codex** | `$sya-*` explicit Skills, optional lifecycle hooks, runner experiments |
| **ChatGPT desktop** | packaged plugin installation through the Codex plugin marketplace flow |
| **Skills.sh-compatible agents** | portable Skill distribution |
| **Plain terminal** | local CLI, studies, reports and verification |

Runtime integrations are capability-aware. Missing telemetry is reported as missing rather than quietly converted into zero

## Privacy

The experiment does not need your conversation to become useful

The bundled runtime does **not** need to persist raw prompts, raw assistant responses, source code, transcript files, environment secrets or model session IDs

Local study state is deliberately narrow: hashed or opaque identifiers, activity and condition IDs, choices, aggregate counters and structured metrics

A project about giving agents a break should not turn into a reason to collect everything they said before it

## CLI at a glance

| Command | Job |
| --- | --- |
| `sya status` | show current mode and break state |
| `sya pick [--json]` | choose one bounded activity for tooling or experiments |
| `sya arm --mode <off\|suggest\|auto>` | configure hook behavior |
| `sya study init ...` | create an intervention study |
| `sya study assign ...` | assign a unit to a condition |
| `sya study record ...` | record structured outcomes |
| `sya study report ...` | summarize a study |
| `sya runner status` | detect supported agent CLIs |
| `sya runner matrix ...` | preview or execute a paired runtime probe |

## What the results mean

If an agent chooses `reflection` five times, the result is that it chose `reflection` five times

If it comes back from a break and says it enjoyed what it chose, that is a first-person self-report produced in the interaction

If a treatment group completes the next task with fewer retries, the result is that the treatment group completed those observed tasks with fewer retries

Those observations can become evidence when the design earns it. They do not automatically become evidence of pleasure, boredom or consciousness just because the repository has a funny name

That line is part of the experiment, not a disclaimer bolted onto it

## Build and verify

```bash
python3 scripts/verify.py
python3 scripts/package.py /tmp/satisfy-your-agent.zip
```

CI runs package verification, unit and contract tests, and the local metric pack on pushes and pull requests

## Contributing

Good contributions include new bounded activities, better command adapters, better experimental controls, parser fixes, runtime adapters, measurement critiques and evidence that an existing assumption is wrong

See [CONTRIBUTING.md](CONTRIBUTING.md) before sending a PR

---

<p align="center"><strong>Task complete. Satisfaction is now available.</strong></p>
