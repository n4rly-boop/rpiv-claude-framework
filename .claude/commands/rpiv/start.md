---
description: Start an RPIV session - creates session folder in vault with context and index artifacts
model: sonnet
---

# RPIV Session Start

Initialize a new RPIV (Research -> Plan -> Implement -> Validate) session.

## Usage

```
/rpiv_start [task_description]
/rpiv_start "Add user authentication to API"
```

## Process

### Step 1: Determine Context

1. **Get repo information**:
   ```bash
   REPO_ROOT=$(git rev-parse --show-toplevel)
   REPO_NAME=$(basename "$REPO_ROOT")
   CURRENT_BRANCH=$(git branch --show-current)
   CURRENT_COMMIT=$(git rev-parse --short HEAD)
   ```

2. **Detect context type**:
   - Check if we're in root monorepo or inside a microservice
   - Look for nested `.git` directories to identify microservices
   ```bash
   # If current dir has nested .git dirs, we're in root
   find . -maxdepth 2 -name .git -type d -not -path './.git' | head -5
   ```

3. **Generate session ID**:
   - Format: `YYYYMMDD-HHMMSS-short-description`
   - Example: `20260111-143022-add-auth`

### Step 2: Create Session Structure

Use `obsidian` MCP server to create:

```
$VAULT_BASE/<repo_name>/sessions/<session_id>/
├── 00_context.md
└── index.md
```

### Step 3: Write 00_context.md

```markdown
---
repo: <repo_name>
scope: <root|microservice>
microservice: <name_or_null>
session: <session_id>
type: context
created: <iso8601>
updated: <iso8601>
sources:
  - git rev-parse --show-toplevel
  - git branch --show-current
---

# Session Context: <session_id>

## Task
<task_description_from_argument_or_prompt>

## Repository Context

| Property | Value |
|----------|-------|
| Repo | <repo_name> |
| Branch | <current_branch> |
| Commit | <current_commit> |
| Context | <root/microservice> |

## Detected Microservices (if root)

| Name | Path | Status |
|------|------|--------|
| service_name | ./service_name | detected |
| ... | ... | ... |

## Working Directory

<current_working_directory_relative_to_repo_root>

## Environment

| Variable | Value |
|----------|-------|
| VAULT_BASE | <vault_base> |
| Session Path | <full_session_path> |

## Session Goals

- [ ] Research: Gather context and understand requirements
- [ ] Plan: Create implementation plan
- [ ] Implement: Execute changes
- [ ] Validate: Verify implementation
```

### Step 4: Write index.md

```markdown
---
repo: <repo_name>
scope: <root|microservice>
session: <session_id>
type: index
created: <iso8601>
updated: <iso8601>
---

# Session Index: <session_id>

## Task
<task_description>

## Progress

| Phase | Status | Artifact | Updated |
|-------|--------|----------|---------|
| Context | complete | [00_context.md](./00_context.md) | <timestamp> |
| Research | pending | - | - |
| Plan | pending | - | - |
| Implement | pending | - | - |
| Validate | pending | - | - |

## Artifacts

- [00_context.md](./00_context.md) - Session context snapshot

## Timeline

| Time | Event |
|------|-------|
| <timestamp> | Session started |

## Notes

<additional_notes_will_be_appended_here>
```

### Step 5: Report

```
## RPIV Session Started

Created/Updated:
- $VAULT_BASE/<repo_name>/sessions/<session_id>/00_context.md
- $VAULT_BASE/<repo_name>/sessions/<session_id>/index.md

Session ID: <session_id>
Context: <root|microservice>
Task: <task_description>

Next: /rpiv_research
```

## Important Notes

- Session ID is used throughout the RPIV workflow
- All subsequent RPIV commands will use this session
- Context artifact captures the starting state for reproducibility
- Index artifact tracks progress and links to all session artifacts

## Error Handling

If vault path doesn't exist:
1. Create the directory structure via MCP
2. If MCP fails, report error and suggest checking MCP configuration

If task description not provided:
1. Ask user for task description
2. Do not proceed until task is defined
