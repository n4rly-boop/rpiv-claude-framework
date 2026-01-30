---
description: RPIV Research phase - gather context using distiller agents, write research artifact to vault
model: opus
---

# RPIV Research Phase

Conduct research for an RPIV session using distiller agents. Produces compressed context, not raw dumps.

## Usage

```
/rpiv_research                           # Use current session
/rpiv_research --session <session_id>    # Specify session
/rpiv_research --focus "authentication"  # Focus area
```

## Prerequisites

- Active RPIV session (run `/rpiv_start` first)
- Session context artifact exists: `00_context.md`

## Process

### Step 1: Load Session Context

1. **Find active session**:
   - Read most recent session from `$VAULT_BASE/<repo_name>/claude/sessions/`
   - Or use `--session` argument if provided

2. **Read 00_context.md** to understand:
   - Task description
   - Context type (root/microservice)
   - Repo information

### Step 2: Spawn Distiller Agents (Parallel)

Based on context type, spawn appropriate distillers:

**If in ROOT repo:**

```
Agent 1: microservice-distiller (per detected microservice)
- Document each nested repo as black-box
- Output to: $VAULT_BASE/<repo_name>/claude/knowledge/microservices/<name>.md

Agent 2: codebase-locator
- Find relevant files for the task
- Return file map organized by category

Agent 3: codebase-pattern-finder
- Find similar implementations
- Return pattern catalog with examples
```

**If INSIDE microservice:**

```
Agent 1: repo-doc-distiller
- Comprehensive internal documentation
- Output to: $VAULT_BASE/<repo_name>/claude/knowledge/services/<repo_name>.md

Agent 2: codebase-analyzer
- Analyze specific components related to task
- Return implementation analysis

Agent 3: codebase-pattern-finder
- Find patterns for the task
- Return reusable templates
```

**Always spawn:**

```
Agent 4: convention-extractor (via extract_conventions logic)
- If conventions.md doesn't exist, extract conventions
- Update: $VAULT_BASE/<repo_name>/claude/knowledge/conventions/main.md
```

### Step 3: Synthesize Findings

Wait for ALL agents to complete. Then:

1. **Read all agent outputs** (they wrote to vault)
2. **Synthesize into research digest**:
   - Key findings (max 50 lines)
   - File references (paths only)
   - Patterns identified
   - Risks or concerns
   - Open questions

### Step 4: Determine Next Artifact Version

```bash
# Find existing research artifacts and get next version
# Pattern: 1X_research.md where X is iteration (0-9)
EXISTING=$(ls -1 $SESSION_PATH/1?_research.md 2>/dev/null | sort -V | tail -1)
if [ -z "$EXISTING" ]; then
    NEXT_VERSION="10_research.md"
else
    # Extract current number, increment
    CURRENT_NUM=$(basename "$EXISTING" | grep -o '^[0-9]*')
    NEXT_NUM=$((CURRENT_NUM + 1))
    NEXT_VERSION="${NEXT_NUM}_research.md"
fi
```

### Step 5: Write Research Artifact

Use `obsidian` MCP to write `$NEXT_VERSION`:

```markdown
---
repo: <repo_name>
scope: <root|microservice>
session: <session_id>
type: research
created: <iso8601>
updated: <iso8601>
sources:
  - Agent outputs
  - <list_of_paths_examined>
---

# Research: <task_description>

## Summary

[3-5 sentences: what was learned, key insights]

## Context Analysis

### Repository Structure
- Type: <root monorepo|microservice>
- Key directories: <list with purposes>

### Related Components
| Component | Path | Relevance |
|-----------|------|-----------|
| <name> | <path> | <why relevant> |

### Existing Patterns
| Pattern | Location | Applicability |
|---------|----------|---------------|
| <name> | <file:line> | <how it applies> |

## Microservice Analysis (if root repo)

| Microservice | Doc Path | Integration Points |
|--------------|----------|-------------------|
| <name> | <vault_path> | <how it connects> |

## Conventions to Follow

Reference: `$VAULT_BASE/<repo_name>/claude/knowledge/conventions/main.md`

Key conventions for this task:
- <convention 1>
- <convention 2>

## Risks and Concerns

| Risk | Impact | Mitigation |
|------|--------|------------|
| <risk> | High/Med/Low | <approach> |

## Open Questions

- [ ] <question needing clarification>
- [ ] <decision point for planning>

## Knowledge Artifacts Created/Updated

- `<vault_path_1>` - <description>
- `<vault_path_2>` - <description>

## Recommended Next Steps

1. <specific next step>
2. <specific next step>
```

### Step 6: Update Session Index

**CRITICAL: The index MUST track ALL artifacts. Follow this logic precisely:**

#### 6.1: Update Progress Table

**Determine if this is first research or an iteration:**

```
IF $NEXT_VERSION == "10_research.md":
    # First research - UPDATE the existing "Research | pending" row:
    REPLACE: | Research | pending | - | - |
    WITH:    | Research | complete | [10_research.md](./10_research.md) | <timestamp> |

ELSE (iteration - 11, 12, 13...):
    # Iteration - ADD a new row AFTER the last Research-related row:
    ITERATION_NUM = $NEXT_VERSION[1]  # second digit (11 -> 1, 12 -> 2)
    ITERATION_LABEL = "Research (deep dive)" if ITERATION_NUM == 1 else "Research (iteration $ITERATION_NUM)"

    ADD NEW ROW after last Research row:
    | $ITERATION_LABEL | complete | [$NEXT_VERSION](./$NEXT_VERSION) | <timestamp> |
```

**Example Progress table after iterations:**
```markdown
| Research | complete | [10_research.md](./10_research.md) | 2026-01-13T11:20:00Z |
| Research (deep dive) | complete | [11_research.md](./11_research.md) | 2026-01-13T14:00:00Z |
```

#### 6.2: Update Artifacts Section

**ALWAYS append new artifact to the Artifacts list:**
```markdown
- [10_research.md](./10_research.md) - Research findings
- [11_research.md](./11_research.md) - Deep dive research   <-- ADD
```

#### 6.3: Update Timeline

**ALWAYS append new entry at the END of the Timeline table:**
```markdown
| <timestamp> | Research completed ($NEXT_VERSION) |
```

### Step 7: Report

```
## RPIV Research Complete

Created/Updated:
- $VAULT_BASE/<repo_name>/claude/sessions/<session_id>/$NEXT_VERSION
- $VAULT_BASE/<repo_name>/claude/knowledge/microservices/*.md (if root)
- $VAULT_BASE/<repo_name>/claude/knowledge/conventions/main.md

Key Findings:
- <finding 1>
- <finding 2>
- <finding 3>

Open Questions: <N>
Risks Identified: <N>

Next: /rpiv_plan
```

## Important Notes

- **DO NOT paste agent outputs into chat** - they wrote to vault
- Return only paths and a 10-line max digest
- Research artifact becomes input for planning phase
- Knowledge artifacts in `knowledge/` persist across sessions

## Error Handling

If session not found:
```
Error: No active RPIV session found.
Run `/rpiv_start <task>` to begin a new session.
```

If 00_context.md missing:
```
Error: Session context not found at <path>.
Session may be corrupted. Run `/rpiv_start` to create new session.
```
