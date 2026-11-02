#!/usr/bin/env bash
# Verify required API keys are set before starting an AI tool session.

MISSING=()

check() {
  local var="$1"
  local tool="$2"
  if [ -z "${!var}" ]; then
    MISSING+=("$var ($tool)")
  else
    echo "  [ok] $var"
  fi
}

echo "Checking AI tool environment variables..."
check ANTHROPIC_API_KEY "Claude Code"
check GEMINI_API_KEY    "Gemini CLI"
check OPENAI_API_KEY    "Codex / Aider"

if [ ${#MISSING[@]} -gt 0 ]; then
  echo ""
  echo "Missing variables:"
  for v in "${MISSING[@]}"; do
    echo "  [!] $v"
  done
  echo ""
  echo "Set them in .env and run: source .env"
  exit 1
else
  echo ""
  echo "All keys present. Ready to go."
fi
