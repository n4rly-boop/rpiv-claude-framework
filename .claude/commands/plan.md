---
description: Planning only. Runs Planner, shows plan.md, stops. User edits and runs /dev --resume to continue. Usage: /plan "task description"
---

Run planning phase only for: $ARGUMENTS

## Setup

```bash
SESSION_ID=$(date +%Y%m%d-%H%M%S)-$(echo "$ARGUMENTS" | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | cut -c1-30)
SESSION_PATH=".harness/sessions/$SESSION_ID"
mkdir -p "$SESSION_PATH"
```

## Run Planner

Spawn `planner` agent with:
- task: `$ARGUMENTS`
- session_id: `$SESSION_ID`
- session_path: `$SESSION_PATH`
- patterns_md: contents of `.harness/PATTERNS.md`
- conventions_md: contents of `.harness/CONVENTIONS.md`

## Show Result

```
## Plan Created

Session: {session_id}
File: {SESSION_PATH}/plan.md

{full contents of plan.md}

---
Edit plan.md directly, then run `/dev --resume` when ready.
```

Stop here. Do not run generator or evaluator.
