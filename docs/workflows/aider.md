# Aider Workflows

## Feature Development
```
aider --model claude-sonnet-4-6
/add src/feature.py tests/test_feature.py
> Implement X following the pattern in src/existing.py
/diff
/commit
```

## Bug Fix
```
aider
/add src/buggy.py
> The function foo() returns wrong value when input is empty. Fix it and add a test.
```

## Architect Mode (multi-file)
```
aider --architect
> Refactor the authentication module to support OAuth2
```
