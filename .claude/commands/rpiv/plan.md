---
description: RPIV Plan phase - create implementation plan from research, requires research artifact unless --no-research
model: opus
---

# RPIV Plan Phase

Create an implementation plan based on research findings. **Requires research artifact unless `--no-research` flag provided.**

## Usage

```
/rpiv_plan                              # Use research from current session
/rpiv_plan --session <session_id>       # Specify session
/rpiv_plan --no-research                # Skip research requirement
```

## Prerequisites

- Active RPIV session with `00_context.md`
- **Research artifact `1X_research.md` REQUIRED** (latest version, unless `--no-research`)

## Enforcement

### Research Requirement Check

```
# Find latest research artifact
LATEST_RESEARCH=$(ls -1 $SESSION_PATH/1?_research.md 2>/dev/null | sort -V | tail -1)

IF $LATEST_RESEARCH is empty AND --no-research NOT provided:
    REFUSE with message:

    Error: Research artifact not found.

    RPIV workflow requires research before planning.

    Options:
    1. Run `/rpiv_research` first
    2. Use `/rpiv_plan --no-research` to skip (not recommended)

    Research helps ensure:
    - Existing patterns are followed
    - Risks are identified early
    - Implementation aligns with codebase conventions

    EXIT
```

## Process

### Step 1: Load Session Context

1. **Find active session** from `$VAULT_BASE/<repo_name>/sessions/`
2. **Read 00_context.md** for task description
3. **Find and read latest research** (unless `--no-research`):
   ```bash
   LATEST_RESEARCH=$(ls -1 $SESSION_PATH/1?_research.md 2>/dev/null | sort -V | tail -1)
   # Read $LATEST_RESEARCH for research findings
   ```

### Step 2: Load Knowledge Artifacts

Read from `$VAULT_BASE/<repo_name>/knowledge/`:
- `conventions/main.md` - coding standards
- `patterns/` - relevant patterns
- `microservices/` or `services/` - component docs

### Step 3: Design Implementation

Based on research and conventions:

1. **Break task into phases**:
   - Each phase independently testable
   - Order by dependencies
   - Max 2-3 files per phase

2. **For each phase**:
   - Define clear goal
   - List files to modify (with line numbers if known)
   - Reference patterns to follow
   - Define validation criteria

3. **Identify risks**:
   - Breaking changes
   - Performance implications
   - Security considerations

4. **Define manual testing steps** (MANDATORY):
   - Specific curl commands for each endpoint/feature
   - Expected responses with actual values (not placeholders)
   - Observable side effects (logs, DB, cache)
   - Negative test cases

### Step 4: Determine Next Artifact Version

```bash
# Find existing plan artifacts and get next version
EXISTING=$(ls -1 $SESSION_PATH/2?_plan.md 2>/dev/null | sort -V | tail -1)
if [ -z "$EXISTING" ]; then
    NEXT_VERSION="20_plan.md"
else
    CURRENT_NUM=$(basename "$EXISTING" | grep -o '^[0-9]*')
    NEXT_NUM=$((CURRENT_NUM + 1))
    NEXT_VERSION="${NEXT_NUM}_plan.md"
fi
```

### Step 5: Write Plan Artifact

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
# Test 1: Invalid input
curl -i -X <METHOD> "http://localhost:8001<PATH>" \
  -H "Content-Type: application/json" \
  -d '{"invalid": "data"}'
# Expected: 400 Bad Request

# Test 2: Missing auth (if required)
curl -i -X <METHOD> "http://localhost:8001<PATH>"
# Expected: 401 Unauthorized
```

**Success Indicators**:
- [ ] Returns expected status code
- [ ] Response matches schema
- [ ] Side effects observable
- [ ] Negative cases handled correctly

### Validation Checklist
- [ ] All features have manual test steps
- [ ] All curl commands are copy-pasteable (with placeholders clearly marked)
- [ ] Expected responses are specific, not vague
- [ ] Side effects are observable and documented

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

### Step 6: Update Session Index

**CRITICAL: The index MUST track ALL artifacts. Follow this logic precisely:**

#### 6.1: Update Progress Table

**Determine if this is first plan or an iteration:**

```
IF $NEXT_VERSION == "20_plan.md":
    # First plan - UPDATE the existing "Plan | pending" row:
    REPLACE: | Plan | pending | - | - |
    WITH:    | Plan | complete | [20_plan.md](./20_plan.md) | <timestamp> |

ELSE (iteration - 21, 22, 23...):
    # Iteration - ADD a new row AFTER the last Plan-related row:
    # Extract iteration number: 21 -> "1", 22 -> "2", etc.
    ITERATION_NUM = $NEXT_VERSION[1]  # second digit
    ITERATION_LABEL = "Plan (fixes)" if ITERATION_NUM == 1 else "Plan (fixes $ITERATION_NUM)"

    ADD NEW ROW after last Plan row:
    | $ITERATION_LABEL | complete | [$NEXT_VERSION](./$NEXT_VERSION) | <timestamp> |
```

**Example Progress table after multiple iterations:**
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

#### 6.2: Update Artifacts Section

**ALWAYS append new artifact to the Artifacts list:**

```markdown
## Artifacts

- [00_context.md](./00_context.md) - Session context snapshot
- [10_research.md](./10_research.md) - Research findings
- [20_plan.md](./20_plan.md) - Implementation plan          <-- existing
- [21_plan.md](./21_plan.md) - Plan fixes iteration 1       <-- ADD THIS
```

#### 6.3: Update Timeline

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

### Step 7: Report

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

## Important Notes

- **Plan MUST reference research findings**
- **Plan MUST apply conventions from knowledge/**
- Each phase should be completable in one focused session
- Validation criteria must be specific and testable

## Error Handling

If research missing (without `--no-research`):
```
Error: Research artifact required.

Path checked: $VAULT_BASE/<repo>/sessions/<session>/1?_research.md (no matches)

Run `/rpiv_research` first, or use `--no-research` to proceed without research.

Note: Skipping research may result in:
- Missing existing patterns
- Convention violations
- Undiscovered risks
```

If session not found:
```
Error: No active RPIV session.
Run `/rpiv_start <task>` to begin.
```
