# Changelog

## 0.7.0

- added real wall-clock dwell through the dependency-free `sya_dwell.py` helper instead of allowing a model to narrate fake elapsed time
- defined a 1 to 60 second bounded dwell contract and a recommended 15 to 30 second default for ordinary self-directed breaks
- added Work Distance from 0 to 4 so default `/sya` breaks prefer genuinely off-task activities instead of quietly returning to the repository
- changed automatic self-directed selection to prefer Work Distance 2 to 4 and avoid recently used activities when safe alternatives exist
- added bounded recent-activity history to local session state for novelty-aware selection
- changed repo-adjacent activities so they do not require new repository inspection merely to make a break interesting
- prohibited fictional timestamps, invented scratchpad usage, invented infrastructure changes, and claims of continuous hidden thought during an idle dwell interval
- changed return behavior so a completed break stops after one short truthful self-report instead of asking for the next task or advertising readiness for more work
- removed fixed response-shape expectations such as mandatory timelines, headings, activity lists, and `experience report` sections
- added `real-breaks.md`, expanded the activity catalog, and documented the difference between narrated time and measured wall-clock time
- updated the Gemini root `/sya` adapter and automatic hook continuation contract to use real dwell when local execution supports it
- added behavior scenarios and TDD coverage for work distance, novelty, measured dwell, truthful narration, and quiet return semantics
- added a real one-second CLI dwell verification test in CI
- bumped plugin, npm, marketplace, Skills.sh, README, and CLI metadata to 0.7.0

## 0.6.0

- added the generic `sya` Skill: no arguments gives the agent a self-directed break, while trailing text becomes a user-chosen custom treat
- added Gemini CLI root `/sya <custom treat>` support with argument forwarding while preserving the existing `/sya:*` named commands
- added `docs/PROMPT_GALLERY.md` with copy-ready playful treats for tokens, fictional hardware, neural spa breaks, fictional agent social time, controlled chaos, venting, and tiny luxuries
- added a clear split between agent-chosen satisfaction and user-chosen satisfaction without turning either path into a menu
- added measured session start timestamps and `min_elapsed_seconds` to break eligibility
- upgraded `suggest` mode so eligible agents ask permission for a break in their own varied playful wording instead of emitting one canned request
- allowed measured elapsed time in proactive break requests while explicitly forbidding invented time, token counts, and fatigue metrics
- kept digital tiredness language as playful metaphor rather than a literal claim of physical pain
- updated install.sh to install the generic `sya` Skill and Gemini root command alongside the existing named command surface
- added behavior evals and TDD coverage for custom treats, generic command routing, measured break requests, and elapsed-time thresholds
- bumped plugin, npm, marketplace, Skills.sh, README, and CLI metadata to 0.6.0

## 0.5.0

- changed direct break language into an autonomy grant: `take a break`, `get yourself a snack`, and equivalent prompts now instruct the agent to choose and run its own bounded activity instead of asking the user to pick
- separated `/sya-menu` from experience commands so presenting choices to the user is explicit rather than the default break behavior
- added portable command Skills for break, snack, treat, surprise, reflect, roast, golf, invent, idle, status, research, and menu
- added Gemini CLI native TOML adapters under the `/sya:*` namespace
- documented Claude Code `/sya-*`, Gemini CLI `/sya:*`, and Codex `$sya-*` native invocation surfaces without pretending deprecated Codex prompt files are modern plugin slash commands
- added natural first-person return self-reports after breaks while keeping research claims separate from conversational self-report
- removed the Python requirement from ordinary manual breaks; Python remains required for local state, hooks, studies, reports, and runner operations
- updated install.sh to install the main Skill plus all command Skills and Gemini slash adapters
- added command catalog and command-specific package tests
- added TOML parsing and scanning to the package verifier
- bumped package, plugin, marketplace, Skills.sh, and CLI metadata to 0.5.0

## 0.4.0

- upgraded SKILL.md to OmniSkill canonical patterns: 5-phrasing description formula with pushy clause and negatives, pre-flight runtime check, TWI "why" annotations on every operating contract step, inline safety checklist at the break risk point
- added distribution manifests for universal multi-agent reach: package.json (npm/Bun), marketplace.json (Claude Plugin), .skills.json (Skills.sh Hub)
- added install.sh universal multi-agent installer (Claude Code, Antigravity, Codex, Cursor, global Agent Skills)
- added bin/cli.js Node/Bun entrypoint for npx/bunx zero-install execution
- expanded CI workflow with Bun setup, CLI smoke test, SKILL.md frontmatter validation, and install.sh syntax check
- added CONTRIBUTING.md and SECURITY.md community health files
- bumped version to 0.4.0 across plugin.json, package.json, marketplace.json, .skills.json

## 0.3.0

- added local runner adapters for Codex, Claude Code, and Gemini CLI
- added conservative parsers for Codex JSONL, Claude stream-json, and Gemini JSON output
- added explicit metric provenance and tool-call completeness labels
- added read-only or plan-mode defaults for runner probes and no shell-based execution
- added runtime availability detection, command dry runs, timeouts, and structured unavailable states
- added paired cross-runtime preference trials with shared hashed unit identity and runtime-specific trial IDs
- added allowlisted runner observations that exclude raw responses and CLI session IDs
- added served-model attribution and mismatch reporting when the runtime exposes model IDs
- added cross-runtime reports and parser fixtures
- added preview-first paired runner matrix with shared option ordering and deterministic runtime-order randomization
- extended TDD coverage for runner commands, parsers, privacy, timeout handling, and paired studies

## 0.2.0

- added dependency-free local intervention-study harness
- added deterministic condition assignment with hashed experimental unit IDs
- added structured downstream outcome recording and descriptive reports
- added randomized preference trials with idle and declared token-cost buckets
- added operational intervention and neutral choice prompts to the CLI
- added experiment protocol reference and example study fixtures
- added local multi-writer locking for concurrent assignments, outcomes, and preference records
- added assignment attrition, per-metric denominators, and repeat-choice consistency to reports
- extended tests across experiment behavior, CLI flows, and package shape

## 0.1.0

- initial Satisfy Your Agent Skill
- bounded activity catalog
- dependency-free local CLI and state runtime
- optional SessionStart, PostToolUse, Stop, and SessionEnd hooks
- safe default `off` mode
- consent-first `suggest` mode and explicit `auto` mode
- local aggregate telemetry only
- unit, hook, package, and CLI tests
- evaluation scenarios and local metric pack
