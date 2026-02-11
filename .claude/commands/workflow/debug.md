---
description: Debug issues by investigating logs, database state, and git history
---

# Debug

Investigate problems by examining logs, application state, and git history. **Read-only — do not edit files.**

## Initial Response

Use `AskUserQuestion` to ask the user — **do NOT fabricate their answers**:
- What were you trying to test/implement?
- What went wrong? Any error messages?
- When did it last work?

If a plan/ticket file was provided, read it first for context. Wait for actual user response before starting investigation.

## Investigation Areas

| Area | What to Check |
|------|---------------|
| Logs | App logs (`logs/`, `./log/`, `/var/log/`), framework logs, error output |
| App State | Database, cache, config files, env vars |
| Git State | Branch, recent commits, uncommitted changes, timing vs issue onset |
| Services | Running processes, port availability, resource usage |

## Process

### Step 1: Understand the Problem
1. Read any provided context (plan/ticket), note expected vs actual behavior
2. Quick state check: git branch, recent commits, uncommitted changes

### Step 2: Investigate (Parallel Agents)

**Agent 1** (codebase-analyzer): Check logs — find log locations, search for errors/warnings/stack traces around problem timeframe.

**Agent 2** (codebase-analyzer): Check app state — database, configuration, stuck states or anomalies.

**Agent 3** (Explore): Check git/file state — git status, recent commits (`git log --oneline -10`), uncommitted changes, expected files exist.

### Step 3: Present Debug Report

```markdown
## Debug Report

### What's Wrong
[Clear statement based on evidence]

### Evidence
**Logs**: [errors/warnings with timestamps]
**App State**: [DB/config/cache findings]
**Git/Files**: [related recent changes, file issues]

### Root Cause
[Most likely explanation]

### Next Steps
1. **Try first**: [specific command/action]
2. **If that fails**: [alternative approach]

### Beyond Reach
[Things user must check: browser console, external service state, system issues]
```
