---
description: Review changed code and simplify without breaking functionality
---

# Simplify Code

Review changed files and apply simplifications using the code-simplifier agent.

## Process

1. **Get changed files**:
   ```bash
   git diff --name-only
   git diff --cached --name-only
   ```

2. **Spawn code-simplifier agent** on changed files:
   ```
   Review these files for simplification:
   [list of files]

   Find opportunities to make code cleaner and more concise.
   Present suggestions with before/after.
   ```

3. **Review suggestions** - ensure no functionality breaks

4. **Apply approved changes**

5. **Verify**:
   ```
   /tooling format
   /tooling check
   ```
