# Changelog

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
