---
description: Show current session state — phase, files created, handoffs, verdict.
model: claude-haiku-4-5-20251001
---

Show current harness session status.

```bash
REPO_NAME=$(basename $(git rev-parse --show-toplevel))
VAULT_REPO="$CONTEXT_VAULT/$REPO_NAME"
# Find most recent session
SESSION_PATH=$(ls -d $VAULT_REPO/sessions/*/ 2>/dev/null | sort | tail -1)
SESSION_ID=$(basename "${SESSION_PATH%/}" 2>/dev/null)
```

If no session: "No active session. Run `/dev \"task\"` to start."

## Gather State

Read all files in `$SESSION_PATH/`:
- `plan.md` — exists? (Y/N)
- `eval_criteria.md` — exists? (Y/N)
- `planner_*.md` — list with status field from frontmatter
- `generator_*.md` — list with status field from frontmatter
- `evaluator_*.md` — list with verdict field from frontmatter

```bash
# Show only commits from this session start
# Session ID starts with date: YYYYMMDD-HHMMSS
SESSION_DATE=$(echo $SESSION_ID | cut -c1-15 | tr '-' ' ')
git log --oneline --after="$SESSION_DATE" 2>/dev/null | head -10
```

## Output

```
## Session Status

ID: {session_id}

### Phase Progress
- [x/] Planning      {planner_1.md status or "not started"}
- [x/] User review   {"approved" if plan.md exists, else "pending"}
- [x/] Generating    {generator_N.md status or "not started"}
- [x/] Evaluating    {evaluator_N.md verdict or "not started"}

### Files
{list all files in $SESSION_PATH with sizes}

### Git Changes This Session
{git log --oneline from session start}

### Next Step
{inferred from current state: what to run next}
```
