---
description: RPIV Implement phase - execute implementation plan. REQUIRES plan artifact - will refuse without it.
model: opus
---

# RPIV Implement Phase

Execute an approved implementation plan. **Requires plan artifact.**

## Enforcement

```
IF --fix flag:
    LATEST_VALID = latest 4?_validation.md in session
    IF empty: REFUSE: "--fix requires a previous validation. Run /rpiv:validate first."
    ELSE: Use validation issues as guide, skip to Step 3

IF NOT --fix:
    LATEST_PLAN = latest 2?_plan.md in session
    IF empty: REFUSE: "Plan artifact not found. Run /rpiv:plan first, or use --fix for validation fixes."
```

## Process

### Step 1: Load Plan & Knowledge

1. Find active session, read latest plan completely
2. Check for existing checkmarks `- [x]` (partial completion)
3. Read all files mentioned in plan to understand context
4. Load knowledge artifacts from `$VAULT_BASE/<repo_name>/knowledge/`:
   - `conventions/main.md` → coding rules (naming, structure, error handling, imports)
   - `patterns/main.md` → implementation templates to follow
   - Any pattern files referenced in the plan's "Patterns Used" section

### Step 2: Create Implementation Tracking

Version: find existing `3?_implementation.md`, increment (start at `30`). Write via `obsidian` MCP.

**Frontmatter**: `repo`, `scope`, `session`, `type: implementation`, `fix_mode` (if --fix), `created`, `updated`, `sources`.

**Body**: Plan reference, progress table (phases × status/started/completed), phase execution log sections.

### Step 3: Execute Each Phase

**Fix mode** (`--fix`): Reference validation issues, fix sequentially. Consult knowledge for correct patterns before fixing (a validation failure may stem from a convention violation — fix the root cause, not just the symptom). Run `/tooling check` + `/tooling test` after all fixes. No plan phases.

**Normal mode** — for each plan phase:

1. Mark phase `in_progress` in tracking artifact
2. Read all files mentioned in phase
3. **Before writing code**, check loaded knowledge for:
   - Naming conventions (variables, functions, files, classes)
   - Error handling style (exceptions vs result types, logging patterns)
   - Import ordering and module structure rules
   - Anti-patterns or documented pitfalls to avoid
   - Existing patterns that match this phase's work — model new code after them
4. Apply changes following plan specs. Every new function/class/module must conform to conventions. When the plan references a pattern, follow the pattern's structure.
5. Run phase validation:
   - `/tooling check` (formatting, linting, type checking)
   - `/tooling test` (unit tests)
   - Execute manual tests from plan
   - Fix failures before proceeding
6. Update tracking: mark completed items in plan, update progress
7. If plan mismatch found, use `AskUserQuestion` with options: A) adapt (document deviation), B) update plan first, C) ask for guidance. **NEVER choose for the user.**

### Step 4: Phase Completion Protocol

After each phase, report:
- Changes made (file:lines format)
- Validation results (tooling check, test, manual)
- Deviations from plan

Then use `AskUserQuestion`: "Proceed to Phase N+1?" **Wait for actual confirmation. Do NOT auto-proceed.**

### Step 5: Finalize Implementation

Update tracking artifact with:
- **Summary**: completion timestamp, files changed table (file, lines changed, purpose), commits table (SHA, message, files)
- **Validation Status**: automated checks, unit tests, manual testing status
- **Deviations from Plan**: list with justifications

### Step 6: Update Session Index

Follow standard index update protocol:
- **Progress table**: Update "Implement | pending" row (first time) or add iteration row ("Implement (fixes)")
- **Artifacts section**: Append new artifact link
- **Timeline**: Append timestamped entry

### Step 7: Report

```
## RPIV Implementation Complete

Created/Updated:
- <vault_path>

Summary:
- Phases completed: N/total, Files changed: N
- Lines: +added, -removed, Tests: passed/total

Deviations: N documented

Next: /rpiv:validate
```
