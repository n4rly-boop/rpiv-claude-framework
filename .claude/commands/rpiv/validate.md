---
description: RPIV Validate phase - two-pass validation system. Pass 1 (fast surface scan) always runs. Pass 2 (deep multi-agent review) auto-triggers on critical issues.
model: opus
---

# RPIV Validate Phase

Run two-pass validation pipeline on implementation with **smart scoping**.

## Two-Pass System

### Pass 1: Fast Surface Scan (Always Runs)
- `/tooling check` - formatting, linting, type checking
- `/tooling test` - unit tests
- `code-reviewer` - general code review
- **Fail-all-at-once**: Collects ALL issues, doesn't stop early

### Pass 2: Deep Multi-Agent Analysis (Scoped & Conditional)
- **Change-Type Gating**: Selects relevant agents based on what changed
- **Differential Targeting**: Only reviews files with Pass 1 issues
- **Trigger**: Only if Pass 1 finds **CRITICAL** issues

## Pass 2 Agent Selection (Change-Type Gating)

| Change Type | Agents Run | Agents Skipped |
|-------------|------------|----------------|
| Docs/config only | None | All 4 |
| Single file fix | defensive + logic | integration, security |
| API/schema change | integration + security | defensive, logic |
| Auth/security code | security + defensive | integration, logic |
| Multi-file feature | All 4 (scoped to issue files) | - |

**Default (no pattern match)**: Run all 4 agents, but only on files with Pass 1 issues.

Flags: `--fast` skips Pass 2. `--full` forces all 4 agents on all changed files.

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

### Step 2: Discover Changed Files & Detect Change Type

```bash
# From implementation artifact or git
git diff --name-only HEAD~N..HEAD  # Where N = implementation commits
git status --porcelain              # Uncommitted changes
```

#### 2.1: Classify Change Type

Analyze changed files to determine validation scope:

```
changed_files = list of all changed files
file_extensions = unique extensions from changed_files
directories = unique parent directories

# Classification rules (in priority order)
IF all files match (*.md, *.txt, *.rst, *.json, *.yaml, *.yml, *.toml, *.ini, *.cfg):
    change_type = "docs_config"
    pass2_agents = []  # Skip Pass 2 entirely

ELSE IF any file matches (**/auth/**, **/security/**, **/login/**, **/session/**,
                          **password**, **token**, **credential**, **secret**):
    change_type = "security_sensitive"
    pass2_agents = ["security-reviewer", "defensive-reviewer"]

ELSE IF any file matches (**/api/**, **/routes/**, **/endpoints/**, **/schema/**,
                          **openapi**, **swagger**, **/models/**):
    change_type = "api_schema"
    pass2_agents = ["integration-reviewer", "security-reviewer"]

ELSE IF len(changed_files) <= 3 AND len(directories) == 1:
    change_type = "localized_fix"
    pass2_agents = ["defensive-reviewer", "logic-reviewer"]

ELSE:
    change_type = "multi_file_feature"
    pass2_agents = ["defensive-reviewer", "integration-reviewer", "security-reviewer", "logic-reviewer"]
```

**Store change_type and pass2_agents for later use.**

### Step 3: PASS 1 - Fast Surface Scan

**IMPORTANT: Fail-all-at-once - collect ALL issues, never exit early**

#### 3.1: Run Tooling Checks (Collect All Failures)

Use the `/tooling` skill to run project checks. The skill auto-detects project type or uses project-specific configuration.

```
/tooling check   # Linting, type checking - capture full output
/tooling test    # Test suite - capture full output even if check failed
```

**Important:**
- Always run BOTH check and test, even if one fails
- Capture full output from each
- The tooling skill handles project-specific command detection

#### 3.2: Run code-reviewer Agent
**Always run, even if tooling checks failed**

```bash
# Spawn code-reviewer agent
Task(
  subagent_type: "code-reviewer",
  prompt: "Review changed files: <file_list>",
  description: "Review code changes"
)
```

#### 3.3: Analyze Pass 1 Results & Collect Issue Files

Count issues by severity:
- Parse `/tooling check` output for errors
- Parse `/tooling test` output for failures
- Parse code-reviewer output for Critical/Warning/Suggestion

**Collect files with issues (for differential Pass 2):**
```
files_with_issues = []

# From /tooling check - extract file paths from error messages
for error in tooling_check_errors:
    file_path = extract_file_path(error)
    if file_path:
        files_with_issues.append(file_path)

# From /tooling test - extract file paths from test failures
for failure in test_failures:
    file_path = extract_file_path(failure)
    if file_path:
        files_with_issues.append(file_path)

# From code-reviewer - extract file:line references
for issue in code_reviewer_issues:
    if issue.severity in ["CRITICAL", "WARNING"]:
        files_with_issues.append(issue.file_path)

files_with_issues = unique(files_with_issues)
```

**Determine if Pass 2 needed:**
```
IF change_type == "docs_config":
    SKIP Pass 2 entirely (no code changes)

ELSE IF any CRITICAL issues found:
    IF --fast flag:
        SKIP Pass 2, write report
    ELSE IF --full flag:
        TRIGGER Pass 2 with ALL agents on ALL changed files
    ELSE:
        TRIGGER Pass 2 with SELECTED agents on FILES_WITH_ISSUES only
ELSE:
    SKIP Pass 2, write report (all good)
```

### Step 4: PASS 2 - Deep Multi-Agent Analysis (Scoped)

**Only runs if:**
1. Pass 1 found CRITICAL issues, AND
2. `--fast` flag NOT provided, AND
3. change_type != "docs_config"

#### 4.1: Determine Scope

```
IF --full flag:
    # Override: run all agents on all changed files
    agents_to_run = ["defensive-reviewer", "integration-reviewer", "security-reviewer", "logic-reviewer"]
    files_to_review = all_changed_files
ELSE:
    # Smart scoping: selected agents on issue files only
    agents_to_run = pass2_agents  # From Step 2.1 change-type detection
    files_to_review = files_with_issues  # From Step 3.3

# Log scoping decision
INFORM user: "Pass 2 Scope: <N> agents on <M> files"
```

#### 4.2: Launch Selected Agents in Parallel

**Run only selected agents simultaneously:**

```bash
# Launch ONLY the agents determined by change-type gating
# Pass ONLY files_to_review (differential targeting)

IF "defensive-reviewer" in agents_to_run:
    Task(subagent_type: "defensive-reviewer",
         prompt: "Review these files for edge cases: <files_to_review>", ...)

IF "integration-reviewer" in agents_to_run:
    Task(subagent_type: "integration-reviewer",
         prompt: "Review these files for breaking changes: <files_to_review>", ...)

IF "security-reviewer" in agents_to_run:
    Task(subagent_type: "security-reviewer",
         prompt: "Review these files for vulnerabilities: <files_to_review>", ...)

IF "logic-reviewer" in agents_to_run:
    Task(subagent_type: "logic-reviewer",
         prompt: "Validate these files against $LATEST_PLAN: <files_to_review>", ...)
```

**Pass to each agent:**
- `files_to_review` (NOT all changed files - differential targeting)
- Path to `$LATEST_PLAN` (for logic-reviewer)
- Pass 1 results summary for context

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
validation_mode: two_pass | fast_only | full
change_type: <docs_config|security_sensitive|api_schema|localized_fix|multi_file_feature>
pass_2_triggered: true | false
pass_2_agents: [<list of agents run>]
pass_2_files: [<list of files reviewed>]
sources:
  - $LATEST_IMPL
  - $LATEST_PLAN
  - git diff
---

# Validation Report: <task_description>

## Validation Mode

- **Pass 1**: Completed
- **Pass 2**: <Triggered (scoped) | Triggered (full) | Skipped (no critical issues) | Skipped (docs only) | Skipped (--fast flag)>
- **Change Type**: <change_type> → <agents selected>
- **Scope**: <N> agents on <M> files (vs 4 agents on <total> files)

## Summary

### Pass 1: Fast Surface Scan

| Check | Status | Critical | Warnings | Details |
|-------|--------|----------|----------|---------|
| /tooling check | PASS/FAIL/SKIP | N | N | <summary> |
| /tooling test | PASS/FAIL/SKIP | N | N | <summary> |
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

### /tooling check

**Status**: PASS / FAIL / SKIPPED (not configured)
**Command**: `<actual command run>`
**Exit Code**: <N>

```
<truncated output, max 50 lines>
```

**Issues Found**: <N>
**Critical**: <N> | **Warnings**: <N>

### /tooling test

**Status**: PASS / FAIL / SKIPPED (not configured)
**Command**: `<actual command run>`
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

### Change Analysis
- **Change Type**: <change_type>
- **Files Changed**: <N total>
- **Files with Issues**: <M> (targeted for Pass 2)

### Pass 1 Results (Fast Surface Scan)
- /tooling check: <PASS/FAIL/SKIP>
- /tooling test: <PASS/FAIL/SKIP> (<N>/<total>)
- code-reviewer: <APPROVE/REQUEST_CHANGES>

Pass 1 Issues: Critical: <N> | Warnings: <N> | Suggestions: <N>

### Pass 2 Status
<IF Pass 2 ran (scoped):>
**Pass 2 Triggered (Scoped)**: <change_type> → <N> agents on <M> files

Agents Run:
- <agent_name>: Critical: <N> | Warnings: <N>
- <agent_name>: Critical: <N> | Warnings: <N>

Agents Skipped: <list or "none">

<IF Pass 2 ran (full - via --full flag):>
**Pass 2 Triggered (Full)**: All 4 agents on all <N> changed files

<IF Pass 2 skipped:>
**Pass 2 Skipped**: <reason: "docs/config only" | "no critical issues in Pass 1" | "--fast flag used">

---

**Total Issues**: Critical: <N> | Warnings: <N> | Suggestions: <N>
**Verdict**: <PASS/NEEDS_ATTENTION/FAIL>

### Recommended Next Steps

Based on validation results:

<IF PASS:>
- ✓ All checks passed
- Run `/tooling format` if not already done
- Ready for `/session_summary` then commit

<IF NEEDS_ATTENTION (warnings only, no critical):>
- Fix <N> warnings (non-blocking)
- Review suggestions, consider fixing before merge

<IF FAIL - code-level issues (lint, test, formatting):>
- Fix code directly, then `/rpiv_validate` again
- Or use `/rpiv_implement --fix` for guided fixes from validation issues

<IF FAIL - logic/requirements mismatch (logic-reviewer issues):>
- Create new plan iteration: `/rpiv_plan` (produces next 2X_plan.md)
- Then `/rpiv_implement` with updated plan

<IF FAIL - architectural/design problems:>
- Discuss: `/rpiv_discuss --topic "approach"`
- Then re-research if needed: `/rpiv_research --focus "<problem>"`

<IF FAIL - security vulnerabilities:>
- Fix immediately, then `/rpiv_validate` again
- Consider `/rpiv_validate --full` for comprehensive re-check

*(Use --full flag to force comprehensive review if needed)*
```

