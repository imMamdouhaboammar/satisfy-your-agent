#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="${SCRIPT_DIR}/skills/satisfy-your-agent"
TARGET_NAME="satisfy-your-agent"

if [ ! -d "$SKILL_DIR" ]; then
  echo "Error: Skill directory not found at $SKILL_DIR"
  echo "Run this script from the repository root or after cloning."
  exit 1
fi

echo "Installing ${TARGET_NAME} across AI agent environments..."
INSTALLED=0

# Claude Code
if [ -d "$HOME/.claude" ] || command -v claude >/dev/null 2>&1; then
  mkdir -p "$HOME/.claude/skills"
  rm -rf "$HOME/.claude/skills/${TARGET_NAME}"
  cp -r "$SKILL_DIR" "$HOME/.claude/skills/${TARGET_NAME}"
  echo "  Installed for Claude Code -> $HOME/.claude/skills/${TARGET_NAME}"
  INSTALLED=$((INSTALLED + 1))
fi

# Antigravity / Gemini CLI
if [ -d "$HOME/.gemini" ]; then
  mkdir -p "$HOME/.gemini/config/skills"
  rm -rf "$HOME/.gemini/config/skills/${TARGET_NAME}"
  cp -r "$SKILL_DIR" "$HOME/.gemini/config/skills/${TARGET_NAME}"
  echo "  Installed for Antigravity / Gemini CLI -> $HOME/.gemini/config/skills/${TARGET_NAME}"
  INSTALLED=$((INSTALLED + 1))
fi

# Codex / OpenCode
if [ -d "$HOME/.codex" ]; then
  mkdir -p "$HOME/.codex/skills"
  rm -rf "$HOME/.codex/skills/${TARGET_NAME}"
  cp -r "$SKILL_DIR" "$HOME/.codex/skills/${TARGET_NAME}"
  echo "  Installed for Codex / OpenCode -> $HOME/.codex/skills/${TARGET_NAME}"
  INSTALLED=$((INSTALLED + 1))
fi

# Cursor
if [ -d "$HOME/.cursor" ]; then
  mkdir -p "$HOME/.cursor/skills"
  rm -rf "$HOME/.cursor/skills/${TARGET_NAME}"
  cp -r "$SKILL_DIR" "$HOME/.cursor/skills/${TARGET_NAME}"
  echo "  Installed for Cursor -> $HOME/.cursor/skills/${TARGET_NAME}"
  INSTALLED=$((INSTALLED + 1))
fi

# Global Agent Skills (~/.agents/skills)
mkdir -p "$HOME/.agents/skills"
rm -rf "$HOME/.agents/skills/${TARGET_NAME}"
cp -r "$SKILL_DIR" "$HOME/.agents/skills/${TARGET_NAME}"
echo "  Installed for Universal Agent Kernel -> $HOME/.agents/skills/${TARGET_NAME}"
INSTALLED=$((INSTALLED + 1))

echo ""
echo "Installation complete! Installed to ${INSTALLED} location(s)."
