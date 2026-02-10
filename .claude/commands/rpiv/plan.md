---
description: RPIV Plan phase - create implementation plan from research, requires research artifact unless --no-research
model: opus
---

# RPIV Plan Phase

Create implementation plan based on research. Present understanding first, confirm with user, then design.

## Enforcement

```
LATEST_RESEARCH=$(ls -1 $SESSION_PATH/1?_research.md 2>/dev/null | sort -V | tail -1)

IF $LATEST_RESEARCH is empty AND --no-research NOT provided:
    REFUSE: "Research artifact not found. Run `/rpiv_research` first, or use `/rpiv_plan --no-research` to skip."
    EXIT
```

## Process

### Step 1: Load Context

1. **Find active session** from `$VAULT_BASE/<repo_name>/sessions/`
2. **Read 00_context.md** for task description
3. **Read latest research** (unless `--no-research`):
   ```bash
   LATEST_RESEARCH=$(ls -1 $SESSION_PATH/1?_research.md 2>/dev/null | sort -V | tail -1)
   ```
4. **Read knowledge artifacts** from `$VAULT_BASE/<repo_name>/knowledge/`

### Step 2: Present Understanding

Summarize what was read — no analysis yet:

```
## My Understanding

**Task**: <from 00_context.md>
**Scope**: <files/components affected>

**Key research findings**:
- <finding 1>
- <finding 2>

**Intended approach**: <high-level direction from research>
```

### Step 3: Confirm with User (MANDATORY)

Use `AskUserQuestion` to confirm understanding. **Never skip this step.**

```
Is this understanding correct?
- Yes, proceed with planning
- Partially — let me clarify
- No — here's what I actually need
```

Wait for response. Incorporate corrections before proceeding.

### Step 4: Analyze & Design

Based on confirmed understanding:

**Analyze:**

*Main flow:*
- What's the happy path?
- What are the core requirements?

*Edge cases:*
- What happens with empty/null inputs?
- Concurrent access scenarios?
- Error states and recovery?

*Tricky parts:*
- Integration points with existing code
- Potential breaking changes
- Performance implications
- Security considerations

**Design:**
1. **Break task into phases** - each independently testable
2. **For each phase** - define goal, files, patterns, validation
3. **Identify risks** - from edge cases and tricky parts analysis
4. **Define manual testing** - specific, actionable verification steps

### Step 5: Determine Next Artifact Version

```bash
EXISTING=$(ls -1 $SESSION_PATH/2?_plan.md 2>/dev/null | sort -V | tail -1)
if [ -z "$EXISTING" ]; then
    NEXT_VERSION="20_plan.md"
else
    CURRENT_NUM=$(basename "$EXISTING" | grep -o '^[0-9]*')
    NEXT_NUM=$((CURRENT_NUM + 1))
    NEXT_VERSION="${NEXT_NUM}_plan.md"
fi
```

### Step 6: Write Plan Artifact

Use `obsidian` MCP to write `$NEXT_VERSION`:

```markdown
---
repo: <repo_name>
scope: <root|microservice>
session: <session_id>
type: plan
created: <iso8601>
updated: <iso8601>
sources:
  - 00_context.md
  - $LATEST_RESEARCH
  - knowledge/*.md
---

# Implementation Plan: <task_description>

## Summary

[2-3 sentences: what will be built, high-level approach]

## Research Reference

Based on: [$LATEST_RESEARCH](./$LATEST_RESEARCH)

Key inputs from research:
- <insight 1>
- <insight 2>

## Requirements

### Explicit
- [ ] <requirement from task>

### Inferred
- [ ] <requirement from research/conventions>

## Affected Components

| Component | Change Type | Risk | Notes |
|-----------|-------------|------|-------|
| `path/to/file.py` | Modify | Low | Add method |
| `path/to/new.py` | Create | Medium | New service |

## Dependencies

- Requires: <prerequisites>
- Blocks: <what depends on this>

---

## Phase 1: <Name>

**Goal**: [One sentence]

**Pattern**: Follow `<pattern_from_knowledge>.md`

### Changes

#### `path/to/file.py`

At line X, add:
```python
# Pattern reference: knowledge/patterns/<pattern>.md
<code following convention>
```

#### `path/to/another.py`

[Similar structure]

### Validation
- [ ] `/tooling check` - formatting, linting, type checking
- [ ] `/tooling test` - unit tests
- [ ] Manual: <specific verification step from Manual Testing Plan>

---

## Phase 2: <Name>

[Same structure]

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| <risk from research> | High/Med/Low | <approach> |

## Manual Testing Plan (REQUIRED)

**This section is MANDATORY. Every plan MUST include specific, actionable manual testing steps.**

### Environment Setup
- **Environment**: <local/dev/staging>
- **Service startup**:
  ```bash
  docker-compose up chatbot_backend
  # OR: docker-compose up -d  (all services)
  ```
- **Required env vars**:
  - `ENV_VAR_NAME=<value or placeholder>`
- **Auth requirements**:
  - How to obtain token: <specific steps or "not required">

### Feature Verification

For EACH feature or endpoint implemented, provide:

#### Feature/Endpoint: <Name>

**Route**: `<METHOD> <PATH>`

**Request Example**:
```bash
curl -i -X <METHOD> "http://localhost:8001<PATH>" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN_IF_REQUIRED>" \
  -d '{
    "key": "value"
  }'
```

**Expected Response**:
- **Status**: `<200/201/etc>`
- **Body**:
  ```json
  {
    "key": "expected_value"
  }
  ```
- **Side Effects**:
  - **Logs**: `<pattern to grep or "check service logs for X">`
  - **Database**: `SELECT * FROM table WHERE ...` (if applicable)
  - **Cache/Events**: `<redis key pattern or event name>` (if applicable)

**Negative Test Cases**:
```bash
# Invalid input
curl -i -X <METHOD> "http://localhost:8001<PATH>" \
  -H "Content-Type: application/json" \
  -d '{"invalid": "data"}'
# Expected: 400 Bad Request

# Missing auth (if required)
curl -i -X <METHOD> "http://localhost:8001<PATH>"
# Expected: 401 Unauthorized
```

**Success Indicators**:
- [ ] Returns expected status code
- [ ] Response matches schema
- [ ] Side effects observable
- [ ] Negative cases handled correctly

## Rollback Plan

1. <step to undo>
2. <step to undo>

## Success Criteria

- [ ] <measurable outcome>
- [ ] All existing tests pass
- [ ] New tests cover added functionality
- [ ] Code follows conventions in `knowledge/conventions/main.md`

---

## Conventions Applied

From `knowledge/conventions/main.md`:
- <convention 1 applied>
- <convention 2 applied>

## Patterns Used

- `knowledge/patterns/<pattern1>.md` - used in Phase 1
- `knowledge/patterns/<pattern2>.md` - used in Phase 2

## References

- Research: [$LATEST_RESEARCH](./$LATEST_RESEARCH)
- Conventions: `$VAULT_BASE/<repo>/knowledge/conventions/main.md`
```

### Step 7: Update Session Index

**The index MUST track ALL artifacts. Follow this logic precisely:**

#### 7.1: Update Progress Table

```
IF $NEXT_VERSION == "20_plan.md":
    # First plan - UPDATE the existing "Plan | pending" row:
    REPLACE: | Plan | pending | - | - |
    WITH:    | Plan | complete | [20_plan.md](./20_plan.md) | <timestamp> |

ELSE (iteration - 21, 22, 23...):
    # Iteration - ADD a new row AFTER the last Plan-related row:
    ITERATION_NUM = $NEXT_VERSION[1]  # second digit
    ITERATION_LABEL = "Plan (fixes)" if ITERATION_NUM == 1 else "Plan (fixes $ITERATION_NUM)"

    ADD NEW ROW after last Plan row:
    | $ITERATION_LABEL | complete | [$NEXT_VERSION](./$NEXT_VERSION) | <timestamp> |
```

**Example after iterations:**
```markdown
| Phase | Status | Artifact | Updated |
|-------|--------|----------|---------|
| Context | complete | [00_context.md](./00_context.md) | 2026-01-13T11:15:00Z |
| Research | complete | [10_research.md](./10_research.md) | 2026-01-13T11:20:00Z |
| Plan | complete | [20_plan.md](./20_plan.md) | 2026-01-13T11:25:00Z |
| Plan (fixes) | complete | [21_plan.md](./21_plan.md) | 2026-01-13T14:00:00Z |
| Plan (fixes 2) | complete | [22_plan.md](./22_plan.md) | 2026-01-13T16:00:00Z |
| Implement | pending | - | - |
| Validate | pending | - | - |
```

#### 7.2: Update Artifacts Section

**ALWAYS append new artifact to the Artifacts list:**

```markdown
## Artifacts

- [00_context.md](./00_context.md) - Session context snapshot
- [10_research.md](./10_research.md) - Research findings
- [20_plan.md](./20_plan.md) - Implementation plan          <-- existing
- [21_plan.md](./21_plan.md) - Plan fixes iteration 1       <-- ADD THIS
```

#### 7.3: Update Timeline

**ALWAYS append new entry at the END of the Timeline table:**

```markdown
## Timeline

| Time | Event |
|------|-------|
| 2026-01-13T11:15:00Z | Session started |
| 2026-01-13T11:20:00Z | Research completed |
| 2026-01-13T11:25:00Z | Plan created (20_plan.md) |
| 2026-01-13T14:00:00Z | Plan iteration created (21_plan.md) - fixes for validation issues |  <-- ADD THIS
```

### Step 8: Report

```
## RPIV Plan Complete

Created/Updated:
- $VAULT_BASE/<repo_name>/sessions/<session_id>/$NEXT_VERSION

Plan Summary:
- Phases: <N>
- Files affected: <N>
- Risk level: <Low/Medium/High>

Key Phases:
1. <Phase 1 name> - <brief>
2. <Phase 2 name> - <brief>

Top Risks:
- <risk 1>

Next: /rpiv_implement
```
