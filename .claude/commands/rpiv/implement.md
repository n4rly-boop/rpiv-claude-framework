---
description: RPIV Implement phase - execute implementation plan. REQUIRES plan artifact - will refuse without it.
model: opus
---

# RPIV Implement Phase

Execute an approved implementation plan. **Requires plan artifact - will refuse without it.**

## Usage

```
/rpiv_implement                         # Use plan from current session
/rpiv_implement --session <session_id>  # Specify session
/rpiv_implement --phase N               # Implement specific phase only
/rpiv_implement --resume                # Resume from last incomplete phase
/rpiv_implement --fix                   # Quick fix: bypass plan, fix validation issues
```

## Prerequisites

- Active RPIV session with `00_context.md`
- **Plan artifact `2X_plan.md` REQUIRED** (latest version, no override)
- **Exception**: `--fix` flag bypasses plan requirement (requires prior validation artifact)

## Enforcement

### Fix Mode Check (--fix flag)

```
IF --fix flag provided:
    # Bypass plan requirement
    LATEST_VALID=$(ls -1 $SESSION_PATH/4?_validation.md 2>/dev/null | sort -V | tail -1)

    IF $LATEST_VALID is empty:
        REFUSE with message:

        Error: --fix requires a previous validation. Run /rpiv_validate first.

        The --fix flag uses validation issues as a guide for fixes.
        No validation artifact found at: $SESSION_PATH/4?_validation.md

        EXIT

    ELSE:
        INFORM: "Fix mode: using validation issues from $LATEST_VALID as guide"
        READ $LATEST_VALID for issues to fix
        PROCEED to Step 3 (skip plan loading)
```

### Plan Requirement Check (CANNOT BE SKIPPED unless --fix)

```
# Find latest plan artifact
LATEST_PLAN=$(ls -1 $SESSION_PATH/2?_plan.md 2>/dev/null | sort -V | tail -1)

IF $LATEST_PLAN is empty:
    REFUSE with message:

    Error: Plan artifact not found. Implementation REQUIRES a plan.

    RPIV workflow enforces: Research -> Plan -> Implement -> Validate

    You cannot implement without a plan because:
    - Implementation without planning leads to inconsistent code
    - Plans ensure conventions are followed
    - Plans define validation criteria
    - Plans identify risks before they become problems

    Required action:
    1. Run `/rpiv_plan` to create a plan
    2. Review and approve the plan
    3. Run `/rpiv_implement` again

    If you have a plan elsewhere, copy it to:
    $VAULT_BASE/<repo>/sessions/<session>/2X_plan.md (e.g., 20_plan.md)

    Or use `/rpiv_implement --fix` to fix validation issues without a plan.

    EXIT
```

## Process

### Step 1: Load Plan

1. **Find active session** from `$VAULT_BASE/<repo_name>/sessions/`
2. **Find and read latest plan**:
   ```bash
   LATEST_PLAN=$(ls -1 $SESSION_PATH/2?_plan.md 2>/dev/null | sort -V | tail -1)
   # Read $LATEST_PLAN completely
   ```
3. **Check for existing checkmarks** `- [x]` (partial completion)
4. **Read all files mentioned in plan** to understand context

### Step 2: Determine Next Artifact Version

```bash
# Find existing implementation artifacts and get next version
EXISTING=$(ls -1 $SESSION_PATH/3?_implementation.md 2>/dev/null | sort -V | tail -1)
if [ -z "$EXISTING" ]; then
    NEXT_VERSION="30_implementation.md"
else
    CURRENT_NUM=$(basename "$EXISTING" | grep -o '^[0-9]*')
    NEXT_NUM=$((CURRENT_NUM + 1))
    NEXT_VERSION="${NEXT_NUM}_implementation.md"
fi
```

### Step 3: Create Implementation Tracking

Use `obsidian` MCP to create `$NEXT_VERSION`:

```markdown
---
repo: <repo_name>
scope: <root|microservice>
session: <session_id>
type: implementation
fix_mode: <true if --fix, omit otherwise>
created: <iso8601>
updated: <iso8601>
sources:
  - $LATEST_PLAN  # or $LATEST_VALID if --fix mode
---

# Implementation: <task_description>

## Plan Reference

Based on: [$LATEST_PLAN](./$LATEST_PLAN)

## Progress

| Phase | Status | Started | Completed |
|-------|--------|---------|-----------|
| Phase 1 | in_progress | <timestamp> | - |
| Phase 2 | pending | - | - |

## Phase Execution Log

### Phase 1: <Name>

**Started**: <timestamp>

#### Changes Made

| File | Action | Lines | Commit |
|------|--------|-------|--------|
| `path/to/file.py` | Modified | 45-67 | <sha> |

#### Deviations from Plan

[None / List any necessary deviations]

#### Validation Results

- [x] /tooling check - PASSED
- [x] /tooling test - PASSED
- [ ] Manual: <pending>

**Status**: <complete/blocked/in_progress>
```

### Step 4: Execute Each Phase

**If in fix mode (`--fix`):**
- Reference validation issues from `$LATEST_VALID` instead of plan phases
- No phases — fix each listed issue sequentially
- Still run `/tooling check` and `/tooling test` after all fixes
- Skip manual tests from plan (no plan in fix mode)

**If in normal mode:**

For each phase in the plan:

1. **Mark phase as in_progress** in `$NEXT_VERSION`

2. **Read all files** mentioned in the phase

3. **Apply changes** following:
   - Exact specifications in plan
   - Conventions from `knowledge/conventions/main.md`
   - Patterns from `knowledge/patterns/`

4. **Run phase validation**:
   - Run `/tooling check` (formatting, linting, type checking)
   - Run `/tooling test` (unit tests)
   - Execute manual tests from plan
   - If failures, fix before proceeding

5. **Update tracking**:
   - Mark completed items in plan `$LATEST_PLAN`
   - Update progress in `$NEXT_VERSION`

6. **If mismatch with plan**:
   ```
   Issue in Phase [N]:
   Expected: [what plan says]
   Found: [actual situation]

   Options:
   A. Adapt implementation (document deviation)
   B. Update plan first
   C. Ask for guidance

   How should I proceed?
   ```

### Step 5: Phase Completion Protocol

After each phase:

```
Phase [N] Complete - Ready for Validation

Changes made:
- `file1.py:45-67` - Added method X
- `file2.py:12` - Updated import

Validation:
- [x] /tooling check - PASSED
- [x] /tooling test - PASSED (15/15)
- [ ] Manual verification needed

Deviations: [None / List]

Proceed to Phase [N+1]? (y/n)
```

### Step 6: Finalize Implementation

After all phases:

1. **Update `$NEXT_VERSION`** with final status:

```markdown
## Summary

**Completed**: <timestamp>
**Total Duration**: <time>

### Files Changed

| File | Lines Changed | Purpose |
|------|--------------|---------|
| `path/to/file.py` | +45, -12 | New endpoint |

### Commits

| SHA | Message | Files |
|-----|---------|-------|
| abc123 | Add user endpoint | 3 |

### Validation Status

- [x] All automated checks pass
- [x] All unit tests pass
- [ ] Manual testing pending

### Deviations from Plan

[List any deviations with justification]
```

2. **Update session index** (CRITICAL - must track ALL artifacts):

#### Update Progress Table

**Determine if this is first implementation or an iteration:**

```
IF $NEXT_VERSION == "30_implementation.md":
    # First implementation - UPDATE the existing "Implement | pending" row:
    REPLACE: | Implement | pending | - | - |
    WITH:    | Implement | complete | [30_implementation.md](./30_implementation.md) | <timestamp> |

ELSE (iteration - 31, 32, 33...):
    # Iteration - ADD a new row AFTER the last Implement-related row:
    ITERATION_NUM = $NEXT_VERSION[1]  # second digit (31 -> 1, 32 -> 2)
    ITERATION_LABEL = "Implement (fixes)" if ITERATION_NUM == 1 else "Implement (fixes $ITERATION_NUM)"

    ADD NEW ROW after last Implement row:
    | $ITERATION_LABEL | complete | [$NEXT_VERSION](./$NEXT_VERSION) | <timestamp> |
```

**Example Progress table after iterations:**
```markdown
| Implement | complete | [30_implementation.md](./30_implementation.md) | 2026-01-13T11:30:00Z |
| Implement (fixes) | complete | [31_implementation.md](./31_implementation.md) | 2026-01-13T14:30:00Z |
| Implement (fixes 2) | complete | [32_implementation.md](./32_implementation.md) | 2026-01-13T16:30:00Z |
```

#### Update Artifacts Section

**ALWAYS append new artifact to the Artifacts list:**
```markdown
- [30_implementation.md](./30_implementation.md) - Implementation summary
- [31_implementation.md](./31_implementation.md) - Implementation fixes iteration 1   <-- ADD
```

#### Update Timeline

**ALWAYS append new entry at the END of the Timeline table:**
```markdown
| <timestamp> | Implementation iteration completed ($NEXT_VERSION) - <brief description of what was fixed> |
```

### Step 7: Report

```
## RPIV Implementation Complete

Created/Updated:
- $VAULT_BASE/<repo_name>/sessions/<session_id>/$NEXT_VERSION

Summary:
- Phases completed: <N>/<total>
- Files changed: <N>
- Lines: +<added>, -<removed>
- Tests: <passed>/<total>

Deviations: <N> documented

Next: /rpiv_validate

Note: Run validation to verify implementation meets all success criteria.
```

## Important Notes

- **NEVER skip plan requirement** - this is enforced, not optional
- **Use /tooling skill** for validation - never invoke linters/testers directly
  - ✓ CORRECT: `/tooling check`, `/tooling test`
  - ✗ WRONG: `ruff check .`, `pytest tests/`, `make check`
- **Document ALL deviations** from plan
- **Run validation after each phase** before proceeding
- **Keep tracking artifact updated** in real-time

## Error Handling

If plan missing:
```
Error: Plan artifact REQUIRED for implementation.

Cannot proceed because:
1. Implementation without planning leads to inconsistent code
2. No validation criteria defined
3. No risk assessment available

Path checked: $VAULT_BASE/<repo>/sessions/<session>/2?_plan.md (no matches)

Required: Run `/rpiv_plan` first.
```

If validation fails:
```
Phase [N] Validation Failed

Command: /tooling check  (or: /tooling test)
Exit code: 1
Output: [summary]

Options:
1. Fix issues and retry validation
2. Mark phase incomplete and document blocker
3. Rollback phase changes

Note: Use the /tooling skill for validation.
Never run linters or test frameworks directly.

How should I proceed?
```
