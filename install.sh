#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_SKILL="${SCRIPT_DIR}/skills/satisfy-your-agent"
TARGET_NAME="satisfy-your-agent"
GEMINI_COMMANDS="${SCRIPT_DIR}/adapters/gemini/commands/sya"
COMMAND_SKILLS=("${SCRIPT_DIR}"/skills/sya-*)

if [ ! -d "$MAIN_SKILL" ]; then
  echo "Error: Skill directory not found at $MAIN_SKILL"
  echo "Run this script from the repository root or after cloning."
  exit 1
fi

install_skill_bundle() {
  local target_root="$1"
  mkdir -p "$target_root"

  rm -rf "$target_root/$TARGET_NAME"
  cp -r "$MAIN_SKILL" "$target_root/$TARGET_NAME"

  local command_path command_name
  for command_path in "${COMMAND_SKILLS[@]}"; do
    [ -d "$command_path" ] || continue
    command_name="$(basename "$command_path")"
    rm -rf "$target_root/$command_name"
    cp -r "$command_path" "$target_root/$command_name"
  done
}

echo "Installing ${TARGET_NAME} and its command surface..."
INSTALLED=0

# Claude Code. Skills become slash commands such as /sya-break when installed personally.
if [ -d "$HOME/.claude" ] || command -v claude >/dev/null 2>&1; then
  install_skill_bundle "$HOME/.claude/skills"
  echo "  Claude Code -> $HOME/.claude/skills (main skill + command skills)"
  INSTALLED=$((INSTALLED + 1))
fi

# Gemini CLI / Antigravity skills plus native namespaced slash commands.
if [ -d "$HOME/.gemini" ] || command -v gemini >/dev/null 2>&1; then
  install_skill_bundle "$HOME/.gemini/config/skills"
  mkdir -p "$HOME/.gemini/commands"
  rm -rf "$HOME/.gemini/commands/sya"
  if [ -d "$GEMINI_COMMANDS" ]; then
    cp -r "$GEMINI_COMMANDS" "$HOME/.gemini/commands/sya"
  fi
  echo "  Gemini CLI -> skills + $HOME/.gemini/commands/sya (/sya:*)"
  INSTALLED=$((INSTALLED + 1))
fi

# Codex. Skills are invoked explicitly as $sya-break, $sya-snack, etc.
if [ -d "$HOME/.codex" ] || command -v codex >/dev/null 2>&1; then
  install_skill_bundle "$HOME/.codex/skills"
  echo "  Codex -> $HOME/.codex/skills (main skill + command skills)"
  INSTALLED=$((INSTALLED + 1))
fi

# Cursor.
if [ -d "$HOME/.cursor" ]; then
  install_skill_bundle "$HOME/.cursor/skills"
  echo "  Cursor -> $HOME/.cursor/skills (main skill + command skills)"
  INSTALLED=$((INSTALLED + 1))
fi

# Universal Agent Skills fallback.
install_skill_bundle "$HOME/.agents/skills"
echo "  Universal Agent Skills -> $HOME/.agents/skills"
INSTALLED=$((INSTALLED + 1))

echo ""
echo "Installation complete. Installed to ${INSTALLED} environment(s)."
echo ""
echo "Quick invocation:"
echo "  Claude Code: /sya-break, /sya-snack, /sya-menu"
echo "  Gemini CLI: /sya:break, /sya:snack, /sya:menu"
echo '  Codex: $sya-break, $sya-snack, $sya-menu'
