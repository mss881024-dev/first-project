# Claude Code

## Setup

```bash
npm install -g @anthropic-ai/claude-code
export ANTHROPIC_API_KEY=<your-key>
claude
```

## Key Features
- Agentic file editing with `Edit` / `Write` tools
- Git-aware (reads diffs, creates commits)
- MCP server integrations
- Hooks for automated workflows (`.claude/settings.json`)

## Configuration
- **Project settings**: `.claude/settings.json`
- **Project guide**: `.claude/CLAUDE.md` — read automatically on session start
- **Prompts**: `prompts/claude/`

## Useful Commands
| Command | Description |
|---------|-------------|
| `/help` | Show all slash commands |
| `/config` | Edit settings |
| `/review` | Review current diff |
| `/init` | Generate CLAUDE.md for repo |

## Tips
- Add frequently used bash commands to `permissions.allow` in `.claude/settings.json` to skip prompts
- Use `prompts/claude/` to store system-level context for long sessions
