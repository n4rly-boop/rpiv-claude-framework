---
description: Review changed code and simplify without breaking functionality
---

# Simplify Code

Review changed files and apply simplifications using the code-simplifier agent.

## Process

1. **Get changed files**: `git diff --name-only` + `git diff --cached --name-only`
2. **Spawn code-simplifier agent** on changed files — find opportunities for cleaner, more concise code
3. **Review suggestions** — ensure no functionality breaks
4. **Apply approved changes**
5. **Verify**: `/tooling format` → `/tooling check`
