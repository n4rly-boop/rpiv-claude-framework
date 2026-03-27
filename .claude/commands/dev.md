---
description: Full development pipeline. Planner → Generator → Evaluator with USER GATE after planning. Usage: /dev "task description"
---

Run the full harness pipeline for: $ARGUMENTS

## Setup

```bash
REPO_NAME=$(basename $(git rev-parse --show-toplevel))
VAULT_REPO="$CONTEXT_VAULT/$REPO_NAME"
SESSION_ID=$(date +%Y%m%d-%H%M%S)-$(echo "$ARGUMENTS" | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | cut -c1-30)
SESSION_PATH="$VAULT_REPO/sessions/$SESSION_ID"
mkdir -p "$SESSION_PATH"
START_COMMIT=$(git rev-parse HEAD)
```

Read these files and store their contents (pass to agents as text, not paths):
- `$VAULT_REPO/PATTERNS.md`
- `$VAULT_REPO/CONVENTIONS.md`
- `$VAULT_REPO/git.md`
- `$VAULT_REPO/decisions.md` (optional — pass empty string if file doesn't exist)

If `--resume` flag: find most recent session via `ls $VAULT_REPO/sessions/ 2>/dev/null | sort | tail -1`,
use that as SESSION_ID/SESSION_PATH, skip to the last incomplete phase.

---

## Phase 1 — Planning

Spawn `planner` agent with:
- task: `$ARGUMENTS`
- session_id: `$SESSION_ID`
- session_path: `$SESSION_PATH`
- patterns_md: contents of `$VAULT_REPO/PATTERNS.md`
- conventions_md: contents of `$VAULT_REPO/CONVENTIONS.md`
- decisions_md: contents of `$VAULT_REPO/decisions.md` (or empty)
- handoffs: none (first run) or existing handoff contents (resume)

Wait for completion. Verify `$SESSION_PATH/plan.md` exists.

---

## USER GATE — Plan Review

Show the user:
```
## Plan Ready for Review

File: {SESSION_PATH}/plan.md

{full contents of plan.md}

---
Edit plan.md directly if needed, then reply "go" to continue, or "abort" to stop.
```

Wait for explicit confirmation. Do not proceed until user says "go" or equivalent.
If user edits plan.md and says "go": re-read the file before continuing.

---

## Phase 2 — Generate + Criteria (parallel)

Spawn both in parallel:

**Evaluator phase 1:**
- phase: 1
- session_id: `$SESSION_ID`
- session_path: `$SESSION_PATH`
- plan_md: full contents of `$SESSION_PATH/plan.md`

**Generator:**
- session_id: `$SESSION_ID`
- session_path: `$SESSION_PATH`
- plan_md: full contents of `$SESSION_PATH/plan.md`
- patterns_md: contents of `$VAULT_REPO/PATTERNS.md`
- conventions_md: contents of `$VAULT_REPO/CONVENTIONS.md`
- git_md: contents of `$VAULT_REPO/git.md`
- decisions_md: contents of `$VAULT_REPO/decisions.md` (or empty)
- handoffs: contents of `$SESSION_PATH/planner_1.md` + any existing generator handoffs
- issues: (none)
- fix_attempt: 0

If generator returns `status: blocked`:
→ Read blocker from `$SESSION_PATH/generator_N.md`
→ Show user the blocker description and options
→ Wait for user decision: edit plan.md and re-run / provide info and continue / abort

---

## Phase 3 — Evaluation

```bash
CHANGED_FILES=$(git diff --name-only $START_COMMIT..HEAD)
GIT_DIFF=$(git diff $START_COMMIT..HEAD)
```

Spawn `evaluator` agent with:
- phase: 2
- session_id: `$SESSION_ID`
- session_path: `$SESSION_PATH`
- plan_md: contents of `$SESSION_PATH/plan.md`
- eval_criteria_md: contents of `$SESSION_PATH/eval_criteria.md`
- changed_files: `$CHANGED_FILES`
- git_diff: `$GIT_DIFF`
- patterns_md: contents of `$VAULT_REPO/PATTERNS.md`
- conventions_md: contents of `$VAULT_REPO/CONVENTIONS.md`
- fix_attempt: 0

---

## Fix Loop

```
fix_attempt = 1
while verdict == FAIL and fix_attempt <= 2:
    Read all issues from most recent $SESSION_PATH/evaluator_N.md

    Spawn generator with:
    - session_id: $SESSION_ID
    - session_path: $SESSION_PATH
    - plan_md: contents of $SESSION_PATH/plan.md
    - issues: full issues list from latest evaluator verdict
    - patterns_md: contents of $VAULT_REPO/PATTERNS.md
    - conventions_md: contents of $VAULT_REPO/CONVENTIONS.md
    - git_md: contents of $VAULT_REPO/git.md
    - decisions_md: contents of $VAULT_REPO/decisions.md (or empty)
    - handoffs: contents of all existing generator handoffs in $SESSION_PATH
    - fix_attempt: fix_attempt

    # Recompute diff after generator commits fixes
    CHANGED_FILES=$(git diff --name-only $START_COMMIT..HEAD)
    GIT_DIFF=$(git diff $START_COMMIT..HEAD)

    Spawn evaluator with:
    - phase: 2
    - session_id: $SESSION_ID
    - session_path: $SESSION_PATH
    - plan_md: contents of $SESSION_PATH/plan.md
    - eval_criteria_md: contents of $SESSION_PATH/eval_criteria.md
    - changed_files: $CHANGED_FILES
    - git_diff: $GIT_DIFF
    - patterns_md: contents of $VAULT_REPO/PATTERNS.md
    - conventions_md: contents of $VAULT_REPO/CONVENTIONS.md
    - fix_attempt: fix_attempt

    fix_attempt++

if still FAIL:
    Show USER GATE with all remaining issues from evaluator
    Wait for decision
```

---

## Completion

On PASS:
```
## Done

Verdict: PASS
Session: {session_id}

Changes:
{git diff --stat $START_COMMIT..HEAD}

Commits:
{git log --oneline $START_COMMIT..HEAD}
```

---

## Flags

- `--fast` — skip evaluator phase 2 (eval_criteria still written, no functional verification)
- `--plan-only` — stop after USER GATE, do not run generator
- `--resume` — find most recent session and continue from last incomplete phase
