---
description: RPIV Plan phase - create implementation plan from research, requires research artifact unless --no-research
model: opus
---

# RPIV Plan Phase

Create implementation plan based on research. Present understanding first, confirm with user, then design.

## Enforcement

```
LATEST_RESEARCH = latest 1?_research.md in session
IF empty AND --no-research NOT provided:
    REFUSE: "Research artifact not found. Run /rpiv:research first, or use /rpiv:plan --no-research."
```

## Process

### Step 1: Load Context & Knowledge

1. Find active session, read `00_context.md` for task description
2. Read latest research (unless `--no-research`)
3. Load knowledge artifacts from `$VAULT_BASE/<repo_name>/knowledge/`:
   - `conventions/main.md` → **design constraints** (naming, structure, error handling rules to follow)
   - `patterns/main.md` → **reusable designs** (implementation templates to model after)
   - Any topic-specific files in `patterns/` or `conventions/` relevant to the task
4. Internalize knowledge as planning inputs: conventions are hard constraints (must follow), patterns are preferred solutions (use when applicable)

### Step 2: Present Understanding (MANDATORY)

Summarize what was read — no analysis yet:

```
## My Understanding
**Task**: <from context>
**Scope**: <files/components affected>
**Key research findings**: <bullet list>
**Intended approach**: <high-level direction>
```

### Step 3: Confirm with User (MANDATORY — never skip)

**NEVER fabricate the user's response.** You MUST call `AskUserQuestion` with "Is this understanding correct?" and options: Yes / Partially / No. Wait for the real answer. Do NOT assume "Yes" and proceed.

Incorporate corrections before proceeding. Do NOT proceed to Step 4 until you have the user's actual response.

### Step 4: Analyze & Design

**Analyze**: Happy path, edge cases (empty/null, concurrent, error states), tricky parts (integration, breaking changes, performance, security).

**Design with knowledge**:
- Check loaded patterns for existing solutions — reuse before inventing. If a pattern covers the task (e.g., "API endpoint pattern", "service layer pattern"), base the phase design on it.
- Apply conventions as constraints — naming, file placement, import order, error handling style must match `conventions/main.md`. Flag any case where the task requires deviating from convention.
- Check for documented anti-patterns or pitfalls in knowledge and design around them.
- Break into independently testable phases. For each: goal, files, pattern reference (if applicable), validation. Identify risks. Define manual testing steps.

### Step 5: Write Plan Artifact

Version: find existing `2?_plan.md`, increment. Write via `obsidian` MCP.

**Frontmatter**: `repo`, `scope`, `session`, `type: plan`, `created`, `updated`, `sources` (context, research, knowledge).

**Body structure:**

```markdown
# Implementation Plan: <task>

## Summary
[2-3 sentences]

## Research Reference
Based on: [<research_artifact>](./<research_artifact>)

## Requirements
### Explicit
- [ ] <from task>
### Inferred
- [ ] <from research/conventions>

## Affected Components
| Component | Change Type | Risk | Notes |
|-----------|-------------|------|-------|

## Phase 1: <Name>
**Goal**: [one sentence]
**Pattern**: Follow `<pattern>.md`

### Changes
#### `path/to/file.py`
At line X, add: [code snippet following convention]

### Validation
- [ ] /tooling check
- [ ] /tooling test
- [ ] Manual: <specific step from Manual Testing Plan>

## Phase N: ...
[Same structure]

## Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|

## Manual Testing Plan (REQUIRED)

### Environment Setup
- Service startup command
- Required env vars (from .env.example)
- Auth: how to obtain token

### Feature Verification (per endpoint/feature)
**Route**: `METHOD PATH`
**Request**: copy-pasteable curl command
**Expected Response**: status code + JSON structure
**Side Effects**: logs/DB/cache to verify
**Negative Cases**: invalid input (400), missing auth (401)
**Success Indicators**: checkbox list

## Rollback Plan
1. <undo steps>

## Success Criteria
- [ ] <measurable outcomes>
- [ ] All existing tests pass
- [ ] New tests cover added functionality

## Conventions Applied
From `knowledge/conventions/main.md`: <list>

## Patterns Used
<list with vault paths>
```

### Step 6: Update Session Index

Follow standard index update protocol:
- **Progress table**: Update "Plan | pending" row (first time) or add iteration row ("Plan (fixes)")
- **Artifacts section**: Append new artifact link
- **Timeline**: Append timestamped entry

### Step 7: Report

```
## RPIV Plan Complete

Created/Updated:
- <vault_path>

Plan Summary: Phases: N, Files affected: N, Risk level: <level>
Key Phases: <numbered list>
Top Risks: <list>

Next: /rpiv:implement
```
