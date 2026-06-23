# Codex (OpenAI)

## Setup

```bash
npm install -g @openai/codex
export OPENAI_API_KEY=<your-key>
codex
```

## Key Features
- Sandboxed code execution environment
- Network-disabled by default for safe execution
- Multimodal input support
- Git-aware change suggestions

## Configuration
- API key: `OPENAI_API_KEY` environment variable
- Model: `CODEX_MODEL` (default: `codex-davinci-002`)
- Prompts: `prompts/codex/`

## Approval Modes
| Mode | Description |
|------|-------------|
| `suggest` | Show diffs, user approves each |
| `auto-edit` | Apply file edits, ask before shell |
| `full-auto` | Fully autonomous (use carefully) |

## Tips
- Start in `suggest` mode for unfamiliar codebases
- Store context-setting prompts in `prompts/codex/context.md`
