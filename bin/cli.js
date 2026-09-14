#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const script = join(__dirname, "..", "skills", "satisfy-your-agent", "scripts", "sya.py");
const args = process.argv.slice(2);

if (args.length === 0 || args.includes("--help") || args.includes("-h")) {
  console.log(`satisfy-your-agent -- Give your coding agent a short break

Usage:
  satisfy-your-agent <command> [options]
  sya <command> [options]

Commands:
  status          Show current break state and hook mode
  pick            Pick a random bounded activity
  arm             Arm break hooks (--mode off|suggest|auto)
  study           Manage intervention studies
  runner          Cross-runtime probe management

Interactive command skills are installed separately by install.sh:
  Claude Code     /sya <treat>  /sya-break  /sya-menu
  Gemini CLI      /sya <treat>  /sya:break  /sya:menu
  Codex           $sya <treat>  $sya-break  $sya-menu

Timed breaks use the bundled measured dwell helper internally when supported.

Examples:
  satisfy-your-agent status
  satisfy-your-agent pick --json
  satisfy-your-agent arm --mode suggest
  satisfy-your-agent study report --id break-effect-v1
  satisfy-your-agent runner status

Options:
  --help, -h      Show this help message
  --version, -v   Show version

Requires: Python 3 (stdlib only, no third-party packages)
`);
  process.exit(0);
}

if (args.includes("--version") || args.includes("-v")) {
  console.log("0.7.0");
  process.exit(0);
}

try {
  execFileSync("python3", [script, ...args], { stdio: "inherit" });
} catch (err) {
  if (err.status != null) process.exit(err.status);
  console.error("Failed to run python3. Ensure Python 3 is installed.");
  process.exit(1);
}
