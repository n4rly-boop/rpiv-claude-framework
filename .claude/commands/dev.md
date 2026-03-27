---
description: Full development pipeline. Planner → Generator → Evaluator with USER GATE after planning. Usage: /dev "task description"
---

Run the full harness pipeline for: $ARGUMENTS

## Setup

```bash
SESSION_ID=$(date +%Y%m%d-%H%M%S)-$(echo "$ARGUMENTS" | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | cut -c1-30)
SESSION_PATH=".harness/sessions/$SESSION_ID"
mkdir -p "$SESSION_PATH"
```

Read these files if they exist (pass to agents):
- `.harness/PATTERNS.md`
- `.harness/CONVENTIONS.md`
- `.harness/git.md`

Check for existing session to resume: `ls .harness/sessions/ 2>/dev/null | sort | tail -1`
If `--resume` flag: use most recent session, skip to the last incomplete phase.

---

## Phase 1 — Planning

Spawn `planner` agent with:
- task: `$ARGUMENTS`
- session_id: `$SESSION_ID`
- session_path: `$SESSION_PATH`
- patterns_md: contents of `.harness/PATTERNS.md`
- conventions_md: contents of `.harness/CONVENTIONS.md`
- handoffs: none (first run) or existing handoffs (resume)

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
- plan_md: contents of plan.md[What section only]
- session_path: `$SESSION_PATH`

**Generator:**
- plan_md: contents of plan.md
- session_path: `$SESSION_PATH`
- patterns_md: `.harness/PATTERNS.md`
- conventions_md: `.harness/CONVENTIONS.md`
- git_md: `.harness/git.md`
- handoffs: planner_1.md + any existing generator handoffs

If generator returns `status: blocked`:
→ Show user the blocker from `generator_N.md`
→ Wait for user decision
→ Options: edit plan.md and re-run, provide info and continue, abort

---

## Phase 3 — Evaluation

```bash
CHANGED_FILES=$(git diff --name-only HEAD~1..HEAD 2>/dev/null || git diff --name-only HEAD)
GIT_DIFF=$(git diff HEAD~1..HEAD 2>/dev/null || git diff HEAD)
```

Spawn `evaluator` agent with:
- phase: 2
- eval_criteria_md: contents of `$SESSION_PATH/eval_criteria.md`
- changed_files: `$CHANGED_FILES`
- git_diff: `$GIT_DIFF`
- patterns_md: `.harness/PATTERNS.md`
- conventions_md: `.harness/CONVENTIONS.md`
- fix_attempt: 0

---

## Fix Loop

```
fix_attempt = 0
while verdict == FAIL and fix_attempt < 2:
    Read issues from evaluator_N.md
    
    Spawn generator with:
    - plan_md: plan.md
    - issues: issues list from evaluator
    - generator handoffs: all existing
    - fix_attempt: fix_attempt + 1
    
    Spawn evaluator phase 2 again with updated diff
    
    fix_attempt++

if still FAIL:
    Show USER GATE with all remaining issues
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
{git diff --stat}

Commits:
{git log --oneline since session start}
```

---

## Flags

- `--fast` — skip evaluator phase 2 (eval_criteria still written, code review skipped)
- `--plan-only` — stop after USER GATE, do not generate
- `--resume` — find most recent session and continue from last incomplete phase
