---
description: Review changed code for issues, then optionally simplify
---

# Review Code Changes

Review recently changed code for issues, then offer to simplify.

## Process

1. **Get changed files**:
   ```bash
   git diff --name-only
   git diff --cached --name-only
   ```

2. **Spawn parallel agents**:

   **Agent 1: Check Issues** (subagent_type: codebase-analyzer)
   ```
   Review these changed files for:
   - Logic errors or bugs
   - Missing error handling
   - Security issues (injection, XSS, etc)
   - Breaking changes to existing behavior
   Files: [list]
   ```

   **Agent 2: Pattern Conformance** (subagent_type: codebase-pattern-finder)
   ```
   Check if changes follow existing patterns:
   - Do new endpoints match existing endpoint patterns?
   - Do new services match service patterns?
   - Are tests structured like existing tests?
   Files: [list]
   ```

3. **Synthesize review**:

   ```
   ## Code Review

   ### Issues Found
   - [severity] file:line - description

   ### Pattern Deviations
   - file:line - doesn't match pattern in [reference]

   ### Suggestions
   - [improvements that don't change functionality]
   ```
