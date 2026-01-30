---
description: RPIV Validate phase - two-pass validation system. Pass 1 (fast surface scan) always runs. Pass 2 (deep multi-agent review) auto-triggers on critical issues.
model: opus
---

# RPIV Validate Phase

Run two-pass validation pipeline on implementation.

## Two-Pass System

### Pass 1: Fast Surface Scan (Always Runs)
- `make check` - formatting, linting, type checking
- `make test` - unit tests
- `code-reviewer` - general code review
- **Fail-all-at-once**: Collects ALL issues, doesn't stop early
- **Duration**: ~5 minutes

### Pass 2: Deep Multi-Agent Analysis (Auto-triggers on Critical Issues)
- Runs 4 specialist agents **in parallel**:
  - `defensive-reviewer` - Edge cases, null safety, error handling
  - `integration-reviewer` - API contracts, breaking changes, dependencies
  - `security-reviewer` - Injection, auth bypasses, data leaks
  - `logic-reviewer` - Requirements fulfillment vs `$LATEST_PLAN`
- **Trigger**: Only if Pass 1 finds **CRITICAL** issues
- **Duration**: ~15-20 minutes

## Usage

```
/rpiv_validate                          # Two-pass (default): Pass 1, then Pass 2 if critical issues
/rpiv_validate --fast                   # Pass 1 only (skip Pass 2 even if issues found)
/rpiv_validate --session <session_id>   # Specify session
```

## Flags

### `--fast`
Run only Pass 1 (surface scan), skip Pass 2 even if critical issues found.

**Use when:**
- You want quick feedback
- You'll manually review issues
- You're iterating rapidly

### `--session <session_id>`
Specify which session to validate (default: most recent)

## Process

### Step 1: Load Context

1. **Find active session** from `$VAULT_BASE/<repo_name>/sessions/`
2. **Find and read latest artifacts**:
   ```bash
   LATEST_IMPL=$(ls -1 $SESSION_PATH/3?_implementation.md 2>/dev/null | sort -V | tail -1)
   LATEST_PLAN=$(ls -1 $SESSION_PATH/2?_plan.md 2>/dev/null | sort -V | tail -1)
   # Read $LATEST_IMPL to understand what changed
   # Read $LATEST_PLAN for requirements validation
   ```
3. **Check for --fast flag**

### Step 2: Discover Changed Files

```bash
# From implementation artifact or git
git diff --name-only HEAD~N..HEAD  # Where N = implementation commits
git status --porcelain              # Uncommitted changes
```

### Step 3: PASS 1 - Fast Surface Scan

**IMPORTANT: Fail-all-at-once - collect ALL issues, never exit early**

#### 3.1: Check for Makefile Targets
```bash
make -n check 2>/dev/null && echo "check target exists"
make -n test 2>/dev/null && echo "test target exists"
```

#### 3.2: Run Checks (Collect All Failures)
```bash
# Run make check - ALWAYS capture full output, don't stop on failure
CHECK_EXIT=0
if make -n check 2>/dev/null; then
    make check 2>&1 | tee check.log || CHECK_EXIT=$?
fi

# Run make test - ALWAYS run even if check failed
TEST_EXIT=0
if make -n test 2>/dev/null; then
    make test 2>&1 | tee test.log || TEST_EXIT=$?
fi
```

#### 3.3: Run code-reviewer Agent
**Always run, even if make checks failed**

```bash
# Spawn code-reviewer agent
Task(
  subagent_type: "code-reviewer",
  prompt: "Review changed files: <file_list>",
  description: "Review code changes"
)
```

#### 3.4: Analyze Pass 1 Results

Count issues by severity:
- Parse `make check` output for errors
- Parse `make test` output for failures
- Parse code-reviewer output for Critical/Warning/Suggestion

**Determine if Pass 2 needed:**
```
IF any CRITICAL issues found:
    IF --fast flag:
        SKIP Pass 2, write report
    ELSE:
        TRIGGER Pass 2
ELSE:
    SKIP Pass 2, write report (all good)
```

### Step 4: PASS 2 - Deep Multi-Agent Analysis

**Only runs if:**
1. Pass 1 found CRITICAL issues, AND
2. `--fast` flag NOT provided

#### 4.1: Launch Specialist Agents in Parallel

**Run all 4 agents simultaneously using single message with multiple Task calls:**

```bash
# Launch all agents in parallel
Task(subagent_type: "defensive-reviewer", prompt: "Review for edge cases...", ...)
Task(subagent_type: "integration-reviewer", prompt: "Review for breaking changes...", ...)
Task(subagent_type: "security-reviewer", prompt: "Review for vulnerabilities...", ...)
Task(subagent_type: "logic-reviewer", prompt: "Validate against $LATEST_PLAN...", ...)
```

**Pass to each agent:**
- List of changed files
- Path to `$LATEST_PLAN` (for logic-reviewer)
- Pass 1 results summary

#### 4.2: Collect Pass 2 Results

Wait for all 4 agents to complete, then read their outputs from vault:
- `defensive_review.md`
- `integration_review.md`
- `security_review.md`
- `logic_review.md`

#### 4.3: Aggregate All Findings

Combine Pass 1 + Pass 2 results:
- Deduplicate issues (same file:line)
- Group by severity across all sources
- Count total Critical/Warning/Suggestion

### Step 5: Determine Next Artifact Version

```bash
# Find existing validation artifacts and get next version
EXISTING=$(ls -1 $SESSION_PATH/4?_validation.md 2>/dev/null | sort -V | tail -1)
if [ -z "$EXISTING" ]; then
    NEXT_VERSION="40_validation.md"
else
    CURRENT_NUM=$(basename "$EXISTING" | grep -o '^[0-9]*')
    NEXT_NUM=$((CURRENT_NUM + 1))
    NEXT_VERSION="${NEXT_NUM}_validation.md"
fi
```

### Step 6: Write Validation Artifact

Use `obsidian` MCP to write `$NEXT_VERSION`:

```markdown
---
repo: <repo_name>
scope: <root|microservice>
session: <session_id>
type: validation
created: <iso8601>
updated: <iso8601>
validation_mode: two_pass | fast_only
pass_2_triggered: true | false
sources:
  - $LATEST_IMPL
  - $LATEST_PLAN
  - git diff
---

# Validation Report: <task_description>

## Validation Mode

- **Pass 1**: Completed
- **Pass 2**: <Triggered | Skipped (no critical issues) | Skipped (--fast flag)>

## Summary

### Pass 1: Fast Surface Scan

| Check | Status | Critical | Warnings | Details |
|-------|--------|----------|----------|---------|
| make check | PASS/FAIL/SKIP | N | N | <summary> |
| make test | PASS/FAIL/SKIP | N | N | <summary> |
| code-reviewer | PASS/WARN/FAIL | N | N | <summary> |

**Pass 1 Total**: Critical: N | Warnings: N | Suggestions: N

### Pass 2: Deep Multi-Agent Analysis

<IF Pass 2 ran:>

| Agent | Critical | Warnings | Suggestions | Status |
|-------|----------|----------|-------------|--------|
| defensive-reviewer | N | N | N | COMPLETE |
| integration-reviewer | N | N | N | COMPLETE |
| security-reviewer | N | N | N | COMPLETE |
| logic-reviewer | N | N | N | COMPLETE |

**Pass 2 Total**: Critical: N | Warnings: N | Suggestions: N

<IF Pass 2 skipped:>
**Pass 2**: Not triggered (no critical issues in Pass 1)

---

**Overall**: PASS / NEEDS_ATTENTION / FAIL
**Total Issues**: Critical: N | Warnings: N | Suggestions: N

## Implementation Reference

Based on: [$LATEST_IMPL](./$LATEST_IMPL)

Files validated:
- `path/to/file1.py`
- `path/to/file2.py`

## Pass 1 Details: Fast Surface Scan

### make check

**Status**: PASS / FAIL / SKIPPED (no target)
**Exit Code**: <N>

```
<truncated output, max 50 lines>
```

**Issues Found**: <N>
**Critical**: <N> | **Warnings**: <N>

### make test

**Status**: PASS / FAIL / SKIPPED (no target)
**Exit Code**: <N>

```
<truncated output, max 50 lines>
```

**Test Results**: <passed>/<total>
**Coverage**: <X>% (if available)
**Critical**: <N failing tests>

### code-reviewer

**Status**: APPROVE / REQUEST_CHANGES / NEEDS_DISCUSSION

#### Critical Issues (<N>)

| # | File:Line | Issue | Category |
|---|-----------|-------|----------|
| 1 | `file.py:45` | <description> | Logic Error |

#### Warnings (<N>)

| # | File:Line | Issue | Category |
|---|-----------|-------|----------|
| 1 | `file.py:67` | <description> | Pattern Violation |

#### Suggestions (<N>)

[List if any]

---

## Pass 2 Details: Deep Multi-Agent Analysis

<IF Pass 2 ran, include all sections below. IF Pass 2 skipped, show reason.>

### Pass 2 Trigger Reason

Pass 2 triggered because Pass 1 found **<N> critical issues**

### defensive-reviewer

**Focus**: Edge cases, null safety, error handling

#### Critical Issues (<N>)

| # | File:Line | Issue | Scenario |
|---|-----------|-------|----------|
| 1 | `file.py:45` | Missing null check | Crashes on empty input |

#### Warnings (<N>)

[List]

### integration-reviewer

**Focus**: API contracts, breaking changes, dependencies

#### Critical Issues (<N>)

| # | File:Line | Issue | Impact |
|---|-----------|-------|--------|
| 1 | `api.py:23` | Breaking change: removed field | Clients expecting field will break |

#### Warnings (<N>)

[List]

### security-reviewer

**Focus**: Injection, auth bypasses, data leaks

#### Critical Issues (<N>)

| # | File:Line | Issue | Attack Vector |
|---|-----------|-------|---------------|
| 1 | `query.py:12` | SQL injection | Attacker can dump database |

#### Warnings (<N>)

[List]

### logic-reviewer

**Focus**: Requirements fulfillment vs plan

#### Critical Issues (<N>)

| # | File:Line | Issue | Requirement |
|---|-----------|-------|-------------|
| 1 | `user.py:89` | Missing validation | Plan requires email format check |

#### Requirements Check

From [$LATEST_PLAN](./$LATEST_PLAN):

**Phase 1**:
- [x] Requirement 1 - IMPLEMENTED
- [ ] Requirement 2 - MISSING (see logic-reviewer critical issue #1)

**Phase 2**:
- [x] All requirements met

#### Test Coverage

**New Functions Without Tests**:
- `calculate_discount()` - No tests found
- `validate_email()` - Tests present ✓

---

## Success Criteria Check

From [$LATEST_PLAN](./$LATEST_PLAN):

- [x] <criterion 1> - VERIFIED
- [x] <criterion 2> - VERIFIED
- [ ] <criterion 3> - NOT VERIFIED (reason)

## Recommendations

### Must Fix (Blocking)
- <item 1>

### Should Fix (Before Merge)
- <item 1>

### Consider (Optional)
- <item 1>

## Validation Verdict

**Ready for Merge**: YES / NO / WITH_CAVEATS

**Caveats** (if applicable):
- <caveat 1>
```

### Step 7: Update Session Index

**CRITICAL: The index MUST track ALL artifacts. Follow this logic precisely:**

#### 7.1: Update Progress Table

**Determine if this is first validation or an iteration:**

```
IF $NEXT_VERSION == "40_validation.md":
    # First validation - UPDATE the existing "Validate | pending" row:
    REPLACE: | Validate | pending | - | - |
    WITH:    | Validate | <status> | [40_validation.md](./40_validation.md) | <timestamp> |
    # <status> = "complete" if PASS, "needs_attention" if issues found

ELSE (iteration - 41, 42, 43...):
    # Iteration - ADD a new row AFTER the last Validate-related row:
    ITERATION_NUM = $NEXT_VERSION[1]  # second digit (41 -> 1, 42 -> 2)

    # For validation, use ordinal numbers:
    ORDINAL = {1: "2nd", 2: "3rd", 3: "4th", 4: "5th", 5: "6th", 6: "Final"}
    ITERATION_LABEL = "Validate ($ORDINAL)"  # e.g., "Validate (2nd)", "Validate (3rd)"

    ADD NEW ROW after last Validate row:
    | $ITERATION_LABEL | <status> | [$NEXT_VERSION](./$NEXT_VERSION) | <timestamp> |
```

**Example Progress table after iterations:**
```markdown
| Validate | needs_attention | [40_validation.md](./40_validation.md) | 2026-01-13T11:45:00Z |
| Plan (fixes) | complete | [21_plan.md](./21_plan.md) | 2026-01-13T14:00:00Z |
| Implement (fixes) | complete | [31_implementation.md](./31_implementation.md) | 2026-01-13T14:30:00Z |
| Validate (2nd) | needs_attention | [41_validation.md](./41_validation.md) | 2026-01-13T15:00:00Z |
| Plan (fixes 2) | complete | [22_plan.md](./22_plan.md) | 2026-01-13T16:00:00Z |
| Implement (fixes 2) | complete | [32_implementation.md](./32_implementation.md) | 2026-01-13T16:30:00Z |
| Validate (3rd) | **PASS** | [42_validation.md](./42_validation.md) | 2026-01-13T17:00:00Z |
```

#### 7.2: Update Artifacts Section

**ALWAYS append new artifact to the Artifacts list:**
```markdown
- [40_validation.md](./40_validation.md) - Validation report (NEEDS_ATTENTION)
- [41_validation.md](./41_validation.md) - Re-validation report (NEEDS_ATTENTION)   <-- ADD
- [42_validation.md](./42_validation.md) - Final validation (PASS)                   <-- ADD
```

#### 7.3: Update Timeline

**ALWAYS append new entry at the END of the Timeline table:**
```markdown
| <timestamp> | Validation completed ($NEXT_VERSION) - <PASS/NEEDS_ATTENTION/FAIL> (<N> critical issues) |
```

### Step 8: Report

```
## RPIV Validation Complete

Created/Updated:
- $VAULT_BASE/<repo_name>/sessions/<session_id>/$NEXT_VERSION

### Pass 1 Results (Fast Surface Scan)
- make check: <PASS/FAIL/SKIP>
- make test: <PASS/FAIL/SKIP> (<N>/<total>)
- code-reviewer: <APPROVE/REQUEST_CHANGES>

Pass 1 Issues: Critical: <N> | Warnings: <N> | Suggestions: <N>

### Pass 2 Status
<IF Pass 2 ran:>
**Pass 2 Triggered**: Found <N> critical issues in Pass 1

Deep Analysis Results:
- defensive-reviewer: Critical: <N> | Warnings: <N>
- integration-reviewer: Critical: <N> | Warnings: <N>
- security-reviewer: Critical: <N> | Warnings: <N>
- logic-reviewer: Critical: <N> | Warnings: <N>

Pass 2 Issues: Critical: <N> | Warnings: <N> | Suggestions: <N>

<IF Pass 2 skipped:>
**Pass 2 Skipped**: No critical issues found in Pass 1 ✓
<OR if --fast:>
**Pass 2 Skipped**: --fast flag used

---

**Total Issues**: Critical: <N> | Warnings: <N> | Suggestions: <N>
**Verdict**: <PASS/NEEDS_ATTENTION/FAIL>

Next Steps:
<IF PASS:>
- ✓ All checks passed
- Run `make format` if not already done
- Ready for /commit

<IF NEEDS_ATTENTION:>
- Fix <N> warnings (non-blocking)
- Review suggestions
- Consider fixing before merge

<IF FAIL:>
- **MUST FIX <N> critical issues before merge**
- Review $NEXT_VERSION for details
- Fix issues and re-run /rpiv_validate
```

## Important Notes

- **Two-Pass System** - Pass 1 always runs, Pass 2 auto-triggers on critical issues
  - Pass 1: Fast (5 min) - surface scan
  - Pass 2: Deep (15-20 min) - multi-agent analysis
  - Use `--fast` to skip Pass 2 for quick iterations

- **Fail-All-At-Once** - Never exits early, collects ALL issues
  - make check runs even if make test would fail
  - Agents run even if make commands fail
  - You get complete picture in one run

- **Use make commands ONLY** - never invoke ruff, mypy, black, or pytest directly
  - ✓ CORRECT: `make check`, `make test`
  - ✗ WRONG: `ruff check .`, `pytest tests/`, `black .`

- **Pass 2 Trigger** - Only on CRITICAL issues (not warnings)
  - Critical from make check/test failures
  - Critical from code-reviewer agent
  - Warnings alone don't trigger Pass 2

- **Agent Focus** - All agents review changed files only
  - Agents don't review unchanged code
  - Success criteria from plan are verified (logic-reviewer)

- **Parallel Execution** - Pass 2 agents run simultaneously
  - All 4 specialist agents launch at once
  - Faster than sequential (4x speedup)

## Error Handling

If implementation artifact missing:
```
Warning: No implementation artifact found.
Running validation on current git state.

Changed files detected:
- <list from git>

Continuing with Pass 1...
```

If make targets don't exist:
```
Note: make check target not found - skipping
Note: make test target not found - skipping

Continuing with agent review...
```

If Pass 1 finds critical issues:
```
Pass 1 Complete - Critical Issues Found

Critical Issues: <N>
- make check: <N> errors
- make test: <N> failures
- code-reviewer: <N> critical

Triggering Pass 2 (Deep Multi-Agent Analysis)...

[Launches 4 specialist agents in parallel]

This will take ~15-20 minutes. Pass 2 will provide comprehensive analysis
of all critical issues from multiple perspectives.

Use --fast flag to skip Pass 2 for quick iterations.
```

If validation fails:
```
Validation FAILED

Total Critical Issues: <N>

Pass 1:
- make check: <N> errors
- make test: <N> failures
- code-reviewer: <N> critical

Pass 2 (triggered):
- defensive-reviewer: <N> critical
- integration-reviewer: <N> critical
- security-reviewer: <N> critical
- logic-reviewer: <N> critical

Required Actions:
1. Review $NEXT_VERSION for ALL issues (comprehensive list)
2. Fix critical issues
3. Run `/rpiv_validate` again

Do NOT merge until validation passes.

Note: All issues are listed in one place - no need for multiple validation rounds.
```

If agent timeout or failure:
```
Warning: Agent <agent_name> timed out or failed

Continuing with other agents...
Validation report will note which agents completed successfully.
```
