---
description: Review changed code for issues, then optionally simplify
---

# Review Code Changes

Review recently changed code for issues, then offer to simplify.

## Process

1. **Get changed files**: `git diff --name-only` + `git diff --cached --name-only`

2. **Spawn parallel agents**:

   **Agent 1** (codebase-analyzer): Review files for logic errors, missing error handling, security issues (injection, XSS), breaking changes.

   **Agent 2** (codebase-pattern-finder): Check if changes follow existing patterns — endpoints, services, tests match established conventions.

3. **Synthesize**:

```
## Code Review

### Issues Found
- [severity] file:line - description

### Pattern Deviations
- file:line - doesn't match pattern in [reference]

### Suggestions
- [improvements that don't change functionality]
```
