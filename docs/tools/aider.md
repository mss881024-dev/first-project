# Aider

## Setup

```bash
pip install aider-chat
export OPENAI_API_KEY=<your-key>   # or ANTHROPIC_API_KEY for Claude models
aider
```

## Key Features
- Git-native: every AI change is a committed diff
- Supports Claude, GPT-4o, Gemini, and local models
- `/add` files into context selectively
- Architect mode for multi-file planning

## Configuration
- Config file: `.aider/aider.conf.yml`
- Prompts: `prompts/aider/`
- Ignored by git: `.aider.chat.history.md`, `.aider.input.history`

## Common Commands
```
/add src/main.py        # add file to context
/drop src/main.py       # remove file
/diff                   # show pending diff
/commit                 # commit current changes
/architect "refactor X" # use architect+editor model pair
```

## Tips
- Use `--model claude-sonnet-4-6` to use Claude as the backend
- Keep `.aider/aider.conf.yml` committed so team shares settings
