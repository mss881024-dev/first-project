# Gemini CLI

## Setup

```bash
npm install -g @google/gemini-cli
export GEMINI_API_KEY=<your-key>
gemini
```

## Key Features
- 1M token context window — ideal for whole-repo analysis
- Multimodal: accepts images, PDFs, and code
- Built-in Google Search grounding
- MCP client support

## Configuration
- API key: `GEMINI_API_KEY` environment variable
- Model override: `GEMINI_MODEL` (default: `gemini-2.5-pro`)
- Prompts: `prompts/gemini/`

## Useful Flags
```bash
gemini -m gemini-2.5-flash   # faster/cheaper model
gemini -p "$(cat prompts/gemini/analyze-repo.md)"
```

## Tips
- Pipe entire directory contents for large-context analysis: `find . -type f | xargs cat | gemini`
- Use `prompts/gemini/` for pre-built analysis templates
