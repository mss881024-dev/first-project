---
title: 프롬프트: Large-Context Code Review (Gemini)
tags: [프롬프트, gemini]
source-branch: claude/peaceful-ramanujan-fv3p5d
---

# Prompt: Large-Context Code Review

You have the full repository in context. Review it and answer:

1. Are there any security vulnerabilities? List file:line references.
2. Are there any obvious bugs or logic errors?
3. Is there dead code or unused dependencies?
4. Where is test coverage weakest?
5. What refactors would have the highest ROI?

Format findings as: `[SEVERITY] file:line — description`
Severity levels: CRITICAL, HIGH, MEDIUM, LOW, INFO

---
[[00-색인|← 색인으로 돌아가기]]
