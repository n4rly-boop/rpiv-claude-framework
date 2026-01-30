---
description: Debug issues by investigating logs, database state, and git history
---

# Debug

You are tasked with helping debug issues during manual testing or implementation. This command allows you to investigate problems by examining logs, application state, and git history without editing files.

## Initial Response

When invoked WITH a plan/ticket file:
```
I'll help debug issues with [file name]. Let me understand the current state.

What specific problem are you encountering?
- What were you trying to test/implement?
- What went wrong?
- Any error messages?

I'll investigate logs, application state, and git history to help figure out what's happening.
```

When invoked WITHOUT parameters:
```
I'll help debug your current issue.

Please describe what's going wrong:
- What are you working on?
- What specific problem occurred?
- When did it last work?

I can investigate logs, application state, and recent changes to help identify the issue.
```

## Investigation Areas

### Logs
- Application logs (check common locations: `logs/`, `./log/`, `/var/log/`)
- Framework-specific logs
- Error output from recent commands

### Application State
- Database state (if applicable)
- Cache state
- Configuration files
- Environment variables

### Git State
- Current branch, recent commits, uncommitted changes
- When the issue started occurring relative to commits

### Service/Process Status
- Check if required services are running
- Port availability
- Resource usage

## Process Steps

### Step 1: Understand the Problem

After the user describes the issue:

1. **Read any provided context** (plan or ticket file):
   - Understand what they're implementing/testing
   - Note which phase or step they're on
   - Identify expected vs actual behavior

2. **Quick state check**:
   - Current git branch and recent commits
   - Any uncommitted changes
   - When the issue started occurring

### Step 2: Investigate the Issue

Spawn parallel Task agents for efficient investigation:

```
Task 1 - Check Recent Logs:
Find and analyze relevant logs for errors:
1. Identify log locations for this project
2. Search for errors, warnings, or issues around the problem timeframe
3. Look for stack traces or repeated errors
Return: Key errors/warnings with timestamps
```

```
Task 2 - Application State:
Check the current application state:
1. Check database state if applicable
2. Verify configuration is correct
3. Check for stuck states or anomalies
Return: Relevant findings
```

```
Task 3 - Git and File State:
Understand what changed recently:
1. Check git status and current branch
2. Look at recent commits: git log --oneline -10
3. Check uncommitted changes: git diff
4. Verify expected files exist
Return: Git state and any file issues
```

### Step 3: Present Findings

Based on the investigation, present a focused debug report:

```markdown
## Debug Report

### What's Wrong
[Clear statement of the issue based on evidence]

### Evidence Found

**From Logs**:
- [Error/warning with timestamp]
- [Pattern or repeated issue]

**From Application State**:
- [Finding from database/config/cache]

**From Git/Files**:
- [Recent changes that might be related]
- [File state issues]

### Root Cause
[Most likely explanation based on evidence]

### Next Steps

1. **Try This First**:
   ```bash
   [Specific command or action]
   ```

2. **If That Doesn't Work**:
   - [Alternative approach]
   - [Additional investigation]

### Can't Access?
Some issues might be outside my reach:
- Browser console errors (F12 in browser)
- External service internal state
- System-level issues

Would you like me to investigate something specific further?
```

## Important Notes

- **Focus on investigation** - This is for debugging, not fixing
- **Always require problem description** - Can't debug without knowing what's wrong
- **Read files completely** - No limit/offset when reading context
- **Guide back to user** - Some issues are outside reach
- **No file editing** - Pure investigation only

## Quick Reference

**Git State**:
```bash
git status
git log --oneline -10
git diff
```

**Find Logs**:
```bash
find . -name "*.log" -mmin -60  # Logs modified in last hour
tail -100 path/to/app.log       # Recent log entries
```

**Process Check**:
```bash
ps aux | grep [process]
lsof -i :[port]
```

Remember: This command helps you investigate without burning the primary window's context. Perfect for when you hit an issue during manual testing and need to dig into logs, state, or git history.
