# first-project — AI Coding Workspace

A multi-agent AI coding workspace integrating Claude Code, Gemini CLI, Codex, Aider, and Windsurf.

## Quick Start

```bash
# Clone and enter the repo
git clone <repo-url>
cd first-project

# Install tool-specific dependencies
# See docs/tools/<tool-name>.md for each tool's setup guide
```

## Workspace Structure

```
first-project/
├── .claude/               # Claude Code configuration
├── .aider/                # Aider configuration
├── .windsurf/             # Windsurf configuration
├── docs/
│   ├── tools/             # Per-tool setup & usage guides
│   └── workflows/         # Cross-tool workflow recipes
├── prompts/               # Shared prompt templates
│   ├── claude/
│   ├── gemini/
│   ├── codex/
│   ├── aider/
│   └── windsurf/
└── scripts/               # Utility scripts for AI workflows
```

## Integrated Tools

| Tool | Purpose | Config |
|------|---------|--------|
| [Claude Code](docs/tools/claude-code.md) | Agentic coding, file editing, git | `.claude/` |
| [Gemini CLI](docs/tools/gemini-cli.md) | Large-context analysis, multimodal | `GEMINI_API_KEY` |
| [Codex](docs/tools/codex.md) | Code generation, OpenAI models | `OPENAI_API_KEY` |
| [Aider](docs/tools/aider.md) | Git-native pair programming | `.aider/` |
| [Windsurf](docs/tools/windsurf.md) | IDE-integrated AI coding | `.windsurf/` |

## Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

## Conventions

- **Prompts**: Store reusable prompts in `prompts/<tool>/`.
- **Scripts**: Shared automation lives in `scripts/`.
- **Docs**: Tool-specific notes go in `docs/tools/`; cross-tool workflows in `docs/workflows/`.
