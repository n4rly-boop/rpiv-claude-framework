---
description: Show current session state — phase, files created, handoffs, verdict.
model: claude-haiku-4-5-20251001
---

Show current harness session status.

```bash
REPO_NAME=$(basename $(git rev-parse --show-toplevel))
VAULT_REPO="$HOME/context_vault/$REPO_NAME"
# Find most recent session
SESSION_PATH=$(ls -d $HOME/context_vault/$REPO_NAME/sessions/*/ 2>/dev/null | sort | tail -1)
SESSION_ID=$(basename "$SESSION_PATH" 2>/dev/null)
```

If no session: "No active session. Run `/dev \"task\"` to start."

## Gather State

Read all files in `$SESSION_PATH/`:
- `plan.md` — exists? (Y/N)
- `eval_criteria.md` — exists? (Y/N)
- `planner_*.md` — list with status field
- `generator_*.md` — list with status field
- `evaluator_*.md` — list with verdict field

```bash
git log --oneline $(git rev-list --max-parents=0 HEAD)..HEAD 2>/dev/null | head -10
```

## Output

```
## Session Status

ID: {session_id}

### Phase Progress
- [ ] Planning      {planner_1.md status or "not started"}
- [ ] User review   {plan.md exists? "pending" or "approved"}
- [ ] Generating    {generator_N.md status or "not started"}
- [ ] Evaluating    {evaluator_N.md verdict or "not started"}

### Files
{list all $HOME/context_vault/$REPO_NAME/sessions/{id}/* files}

### Git Changes
{git log --oneline from session start}

### Next Step
{inferred from current state: what to run next}
```
