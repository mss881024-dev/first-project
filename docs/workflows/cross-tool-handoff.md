# Cross-Tool Handoff Workflow

Use this when switching between AI tools mid-task to preserve context.

## Exporting Context

When finishing a session in one tool, save a context snapshot:

```bash
# Example: save Claude session context
cat > prompts/shared/context-snapshot.md << 'EOF'
## Current Task
<describe what you were working on>

## Files Modified
- path/to/file.py — <what changed and why>

## Next Steps
1. <what still needs to be done>
2. ...

## Key Decisions
- <any architectural decisions made>
EOF
```

## Tool Strengths — When to Switch

| Scenario | Recommended Tool |
|----------|-----------------|
| Large codebase analysis (>100k tokens) | Gemini CLI |
| Precise file edits with git commits | Claude Code or Aider |
| IDE-integrated multi-file refactor | Windsurf |
| Quick code generation snippet | Codex |
| Pair programming with auto-commits | Aider |

## Handoff Pattern

1. **Save state** → write `prompts/shared/context-snapshot.md`
2. **Switch tool** → open new session
3. **Load context** → paste or reference the snapshot file
4. **Continue task** → pick up from Next Steps
