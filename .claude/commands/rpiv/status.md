---
description: Show current RPIV session status
model: haiku
---

# RPIV Session Status

Show the current state of an RPIV session.

## Process

### Step 1: Find Session

Use `--session` argument if provided, else find most recent session from `$VAULT_BASE/<repo_name>/sessions/`.

If not found: "No active RPIV session found. Run `/rpiv_start <task>` to begin."

### Step 2: Read Context

Read `index.md` and `00_context.md`. Extract session ID and task summary.

### Step 3: Scan & Classify Artifacts

List all `*.md` files in session. Classify: context (`00_*`), discussions (`D??_*`), research (`1?_*`), plan (`2?_*`), implement (`3?_*`), validate (`4?_*`), summary (`50_*`).

Determine phase: summary exists→Complete, validate→Validate, implement→Implement, plan→Plan, research→Research, discussions→Discuss, else→Start.

### Step 4: Report

```
## RPIV Session Status

**Session**: <id> | **Task**: <summary> | **Phase**: <current>

### Artifacts
| Type | Latest | Status |
|------|--------|--------|

### Iterations (if multiple versions exist)
### Discussions (if any)

Next: <phase-based suggestion>
```

## Phase → Next Command

| Phase | Next |
|-------|------|
| Start | `/rpiv_research` |
| Discuss | `/rpiv_research` or `/rpiv_plan --no-research` |
| Research | `/rpiv_plan` |
| Plan | `/rpiv_implement` |
| Implement | `/rpiv_validate` |
| Validate | `/rpiv_implement --fix` (if issues) or `/session_summary` |
| Complete | Session complete. `/rpiv_start` for new |
