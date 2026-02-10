---
description: Show current RPIV session status
model: haiku
---

# RPIV Session Status

Show the current state of an RPIV session.

## Process

### Step 1: Find Session

```
IF --session argument provided:
    SESSION_PATH = $VAULT_BASE/<repo_name>/sessions/<session_id>
ELSE:
    # Find most recent session
    LIST $VAULT_BASE/<repo_name>/sessions/
    SESSION_PATH = most recently modified session directory
```

IF session not found:
```
No active RPIV session found.
Run `/rpiv_start <task>` to begin a new session.
```

### Step 2: Read Session Context

1. Read `index.md` from session directory
2. Read `00_context.md` for task description
3. Extract session ID and task summary

### Step 3: Scan Artifacts

```
# List all files in session directory
artifacts = list all *.md files in SESSION_PATH

# Classify by type
context    = 00_context.md (if exists)
discussions = D??_*.md files
research   = 1?_research.md files (latest = highest number)
plan       = 2?_plan.md files (latest = highest number)
implement  = 3?_implementation.md files (latest = highest number)
validate   = 4?_validation.md files (latest = highest number)
summary    = 50_session_summary.md (if exists)

# Determine current phase
IF summary exists: phase = "Complete"
ELSE IF validate files exist: phase = "Validate"
ELSE IF implement files exist: phase = "Implement"
ELSE IF plan files exist: phase = "Plan"
ELSE IF research files exist: phase = "Research"
ELSE IF discussions exist: phase = "Discuss"
ELSE: phase = "Start"
```

### Step 4: Report

```
## RPIV Session Status

**Session**: <session_id>
**Task**: <from 00_context.md summary>
**Phase**: <current phase>

### Artifacts

| Type | Latest | Status |
|------|--------|--------|
| Context | 00_context.md | complete |
| Research | <latest or -> | <complete/pending> |
| Plan | <latest or -> | <complete/pending> |
| Implement | <latest or -> | <complete/pending> |
| Validate | <latest or -> | <complete/pending> |
| Summary | <50_session_summary.md or -> | <complete/pending> |

### Iterations
<IF multiple versions of any artifact type exist:>
- Research: <count> versions (latest: 1X_research.md)
- Plan: <count> versions (latest: 2X_plan.md)
- etc.

### Discussions
<IF discussion artifacts exist:>
- D01_<topic>.md
- D02_<topic>.md

Next: <suggested command based on current phase>
```

## Phase Suggestions

```
IF phase == "Start":     Next: /rpiv_research
IF phase == "Discuss":   Next: /rpiv_research (or /rpiv_plan --no-research)
IF phase == "Research":  Next: /rpiv_plan
IF phase == "Plan":      Next: /rpiv_implement
IF phase == "Implement": Next: /rpiv_validate
IF phase == "Validate":  Next: /rpiv_implement --fix (if issues) or /session_summary (if pass)
IF phase == "Complete":  Next: Session complete. Start new with /rpiv_start
```
