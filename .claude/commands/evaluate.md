---
description: Run evaluator on current git state. Useful for checking code without running the full pipeline. Uses most recent session's eval_criteria.md if exists.
---

Run evaluator on current working tree.

## Load Context

```bash
REPO_NAME=$(basename $(git rev-parse --show-toplevel))
VAULT_REPO="$CONTEXT_VAULT/$REPO_NAME"
# Find most recent session
SESSION_PATH=$(ls -d $VAULT_REPO/sessions/*/ 2>/dev/null | sort | tail -1)

# Get changes
CHANGED_FILES=$(git diff --name-only HEAD~1..HEAD 2>/dev/null || git status --porcelain | awk '{print $2}')
GIT_DIFF=$(git diff HEAD~1..HEAD 2>/dev/null || git diff)
```

If no session found: inform user to run `/plan` first to create eval criteria.

## Spawn Evaluator

Spawn `evaluator` agent with:
- phase: 2
- eval_criteria_md: contents of `$SESSION_PATH/eval_criteria.md` (if exists, else "none — review code quality only")
- changed_files: `$CHANGED_FILES`
- git_diff: `$GIT_DIFF`
- patterns_md: contents of `$VAULT_REPO/PATTERNS.md`
- conventions_md: contents of `$VAULT_REPO/CONVENTIONS.md`
- fix_attempt: 0

## Show Result

Display the full evaluator verdict.
