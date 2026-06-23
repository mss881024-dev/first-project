# Claude Code Workspace Guide

## Project Overview
Multi-agent AI coding workspace. Other tools in use: Gemini CLI, Codex, Aider, Windsurf.

## Key Directories
- `prompts/claude/` — reusable Claude prompt templates
- `docs/workflows/` — cross-tool workflow recipes
- `scripts/` — shared automation scripts

## Conventions
- Commit messages: `<type>: <short description>` (feat, fix, docs, chore)
- Branch names: `feature/<name>`, `fix/<name>`
- Keep prompts in `prompts/` so other tools can reference them

## Common Tasks
- **Analyze codebase**: Read files in context, then answer questions
- **Cross-tool handoff**: Export context to `prompts/` for use in other tools
