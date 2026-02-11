# RPIV Workflow Guide

This guide walks through the complete RPIV (Research → Plan → Implement → Validate) workflow.

## Workflow Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   START     │────▶│  RESEARCH   │────▶│    PLAN     │────▶│  IMPLEMENT  │
│  (enhanced) │     │             │     │             │     │             │
│ /rpiv:start │     │ /rpiv:      │     │ /rpiv:plan  │     │ /rpiv:      │
│             │     │ research    │     │             │     │ implement   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   │
  ┌─────────┐         ┌─────────┐         ┌─────────┐             │
  │ DISCUSS │         │ DISCUSS │         │ DISCUSS │             │
  │(optional)│        │(auto if │         │(optional)│            │
  │D01_scope │        │questions)│        │D03_design│            │
  └─────────┘         └─────────┘         └─────────┘             │
                                                                   │
                    ┌─────────────┐     ┌─────────────┐            │
                    │   SUMMARY   │◀────│  VALIDATE   │◀───────────┘
                    │             │     │             │
                    │ /session_   │     │ /rpiv:      │
                    │ summary     │     │ validate    │
                    └─────────────┘     └──────┬──────┘
                                               │
                                          ┌────┴────┐
                                          │ DISCUSS │
                                          │(if fail)│
                                          │D0X_retro│
                                          └─────────┘
```

**Discussion points** (`/rpiv:discuss`) are optional but recommended when:
- Research finds open questions (auto-suggested)
- Multiple valid approaches exist
- Significant trade-offs need user input
- Validation fails and next steps need clarification

---

## Phase 1: Start Session (Enhanced)

### Command
```
/rpiv:start [task_description]
/rpiv:start "Add user authentication to API"
/rpiv:start --minimal                    # Skip context scan (fast start)
```

### What Happens
1. **Detects repository context**
   - Root monorepo or microservice
   - Current branch and commit
   - Nested git repos (microservices)

2. **Generates session ID**
   - Format: `YYYYMMDD-HHMMSS-short-description`
   - Example: `20260115-143022-add-auth`

3. **Fast context scan** (~2-3 min, skip with `--minimal`):
   - Searches vault for related sessions
   - Loads existing conventions/patterns
   - Quick codebase scan for relevant files

4. **Interactive clarification**:
   - Asks targeted questions based on scan results
   - Records user responses in context artifact

5. **Creates session structure**
   ```
   $VAULT_BASE/<repo>/sessions/<session_id>/
   ├── 00_context.md    # Enhanced context snapshot
   └── index.md         # Session tracker
   ```

### Output
```
## RPIV Session Started

Created/Updated:
- $VAULT_BASE/<repo>/sessions/<session_id>/00_context.md
- $VAULT_BASE/<repo>/sessions/<session_id>/index.md

Session ID: 20260115-143022-add-auth
Context: root
Task: Add user authentication to API

### Context Scan Results
- Related sessions: 2 found
- Conventions: loaded
- Patterns: 3 found
- Relevant files: 8 identified

### User Clarifications
- Scope: Standard (core + common edge cases)
- Build on previous session: Yes

Next: /rpiv:research (or /rpiv:discuss --topic "scope" if questions remain)
```

---

## Phase 1.5: Discussion (Optional)

### Command
```
/rpiv:discuss                           # Auto-detect context
/rpiv:discuss --topic "approach"        # Specify topic
/rpiv:discuss --after research          # Discuss after specific phase
```

### When to Use
- **After start**: Clarify scope before research
- **After research**: Weigh approaches before planning (auto-suggested if open questions)
- **After plan**: Review design before implementing
- **After validation fails**: Discuss what went wrong

### What Happens
1. **Loads current state** from latest artifacts
2. **Presents summary** (max 20 lines) with decision points
3. **Facilitates discussion** via questions
4. **Records decisions** to vault artifact

### Output
```
## RPIV Discussion Complete

Created:
- $VAULT_BASE/<repo>/sessions/<session_id>/D02_approach.md

Key Decisions:
- Use existing auth middleware pattern
- JWT with refresh tokens
- Store sessions in Redis

Impact:
- Plan will follow patterns/auth-middleware.md
- Need to add Redis dependency

Next: /rpiv:plan
```

### Discussion Artifact Structure
```markdown
# Discussion: Approach

## Context
Task: Add user authentication
Trigger: Open questions from research

## Options Considered
### Option A: Extend existing middleware
- Pros: Follows patterns, less code
- Cons: May need refactoring

### Option B: New auth service
- Pros: Clean separation
- Cons: More complexity

## Decision
**Chosen**: Option A
**Reasoning**: Aligns with existing patterns, faster to implement
**Trade-offs**: Will need to refactor if auth grows complex

## Impact on Next Phase
- Follow patterns/auth-middleware.md
- Focus on JWT validation logic
```

**Key principle**: Discussion artifacts are **decision summaries**, not transcripts. Focus on the WHY.

---

## Phase 2: Research

### Command
```
/rpiv:research                           # Use current session
/rpiv:research --session <session_id>    # Specify session
/rpiv:research --focus "authentication"  # Focus area
```

### Prerequisites
- Active RPIV session (run `/rpiv:start` first)
- Session context artifact exists: `00_context.md`

### What Happens
1. **Loads session context** from `00_context.md`

2. **Spawns distiller agents** (in parallel):

   **If in ROOT repo:**
   - `microservice-distiller` - Documents each nested repo as black-box
   - `codebase-locator` - Finds relevant files for the task
   - `codebase-pattern-finder` - Finds similar implementations

   **If INSIDE microservice:**
   - `repo-doc-distiller` - Comprehensive internal documentation
   - `codebase-analyzer` - Analyzes specific components
   - `codebase-pattern-finder` - Finds patterns for the task

   **Always spawns:**
   - Convention extractor - Updates `knowledge/conventions/main.md`

3. **Synthesizes findings** into research digest:
   - Key findings (max 50 lines)
   - File references (paths only)
   - Patterns identified
   - Risks or concerns
   - Open questions

4. **Writes research artifact**: `10_research.md` (or `11`, `12`... for iterations)

5. **Updates session index**

### Output
```
## RPIV Research Complete

Created/Updated:
- $VAULT_BASE/<repo>/sessions/<session_id>/10_research.md
- $VAULT_BASE/<repo>/knowledge/conventions/main.md

Key Findings:
- Existing auth pattern in src/middleware/auth.py
- JWT tokens used throughout
- Rate limiting already implemented

Open Questions: 2
Risks Identified: 1

Next: /rpiv:plan
```

---

## Phase 3: Plan

### Command
```
/rpiv:plan                              # Use research from current session
/rpiv:plan --session <session_id>       # Specify session
/rpiv:plan --no-research                # Skip research requirement (not recommended)
```

### Prerequisites
- Active RPIV session with `00_context.md`
- **Research artifact `1X_research.md` REQUIRED** (unless `--no-research`)

### Research Requirement
If research artifact not found:
```
Error: Research artifact not found.

RPIV workflow requires research before planning.

Options:
1. Run `/rpiv:research` first
2. Use `/rpiv:plan --no-research` to skip (not recommended)
```

### What Happens
1. **Loads session context and latest research**

2. **Loads knowledge artifacts**:
   - `conventions/main.md` - coding standards
   - `patterns/` - relevant patterns
   - `microservices/` or `services/` - component docs

3. **Designs implementation**:
   - Breaks task into phases (max 2-3 files per phase)
   - Each phase independently testable
   - Defines validation criteria per phase
   - Identifies risks and mitigations

4. **Creates Manual Testing Plan** (REQUIRED):
   - Specific curl commands for each endpoint
   - Expected responses with actual values
   - Observable side effects (logs, DB, cache)
   - Negative test cases

5. **Writes plan artifact**: `20_plan.md` (or `21`, `22`... for iterations)

### Plan Structure
```markdown
# Implementation Plan: <task>

## Summary
## Research Reference
## Requirements (Explicit & Inferred)
## Affected Components

---
## Phase 1: <Name>
**Goal**: [One sentence]
**Pattern**: Follow `<pattern>.md`

### Changes
#### `path/to/file.py`
At line X, add: [code]

### Validation
- [ ] /tooling check
- [ ] /tooling test
- [ ] Manual: <specific step>

---
## Phase 2: <Name>
[Same structure]

---
## Risks & Mitigations
## Manual Testing Plan (REQUIRED)
## Rollback Plan
## Success Criteria
## Conventions Applied
## Patterns Used
```

### Output
```
## RPIV Plan Complete

Created/Updated:
- $VAULT_BASE/<repo>/sessions/<session_id>/20_plan.md

Plan Summary:
- Phases: 3
- Files affected: 5
- Risk level: Medium

Key Phases:
1. Add auth middleware - JWT validation
2. Protect API routes - Apply middleware
3. Add tests - Unit and integration

Top Risks:
- Breaking change to existing clients

Next: /rpiv:implement
```

---

## Phase 4: Implement

### Command
```
/rpiv:implement                         # Use plan from current session
/rpiv:implement --session <session_id>  # Specify session
/rpiv:implement --phase N               # Implement specific phase only
/rpiv:implement --resume                # Resume from last incomplete phase
```

### Prerequisites
- Active RPIV session with `00_context.md`
- **Plan artifact `2X_plan.md` REQUIRED** (no override)

### Plan Requirement (CANNOT BE SKIPPED)
```
Error: Plan artifact not found. Implementation REQUIRES a plan.

RPIV workflow enforces: Research -> Plan -> Implement -> Validate

Required action:
1. Run `/rpiv:plan` to create a plan
2. Review and approve the plan
3. Run `/rpiv:implement` again
```

### What Happens
1. **Loads latest plan**

2. **Creates implementation tracking**: `30_implementation.md`

3. **For each phase**:
   - Marks phase as `in_progress`
   - Reads all files mentioned in phase
   - Applies changes following plan, conventions, patterns
   - Runs phase validation (`/tooling check`, `/tooling test`)
   - If failures: fix before proceeding
   - Updates tracking artifact
   - Asks to proceed to next phase

4. **Handles mismatches**:
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

5. **Finalizes implementation**: Updates summary with files changed, commits, deviations

### Phase Completion Protocol
```
Phase [N] Complete - Ready for Validation

Changes made:
- `file1.py:45-67` - Added method X
- `file2.py:12` - Updated import

Validation:
- [x] /tooling check - PASSED
- [x] /tooling test - PASSED (15/15)
- [ ] Manual verification needed

Deviations: None

Proceed to Phase [N+1]? (y/n)
```

### Output
```
## RPIV Implementation Complete

Created/Updated:
- $VAULT_BASE/<repo>/sessions/<session_id>/30_implementation.md

Summary:
- Phases completed: 3/3
- Files changed: 5
- Lines: +245, -12
- Tests: 15/15

Deviations: 0 documented

Next: /rpiv:validate
```

---

## Phase 5: Validate

### Command
```
/rpiv:validate                          # Two-pass (default)
/rpiv:validate --fast                   # Pass 1 only
/rpiv:validate --session <session_id>   # Specify session
```

### Two-Pass System

#### Pass 1: Fast Surface Scan (~5 min)
- `/tooling check` - formatting, linting, type checking
- `/tooling test` - unit tests
- `code-reviewer` - general code review
- **Fail-all-at-once**: Collects ALL issues, never exits early

#### Pass 2: Deep Multi-Agent Analysis (~15-20 min)
- **Triggers**: Only if Pass 1 finds CRITICAL issues
- **Agents** (run in parallel):
  - `defensive-reviewer` - Edge cases, null safety
  - `integration-reviewer` - API contracts, breaking changes
  - `security-reviewer` - Injection, auth bypasses
  - `logic-reviewer` - Requirements vs implementation

### The `--fast` Flag
Skip Pass 2 for quick iterations:
- Use when iterating rapidly
- Use when you'll manually review
- **Don't use** before creating PR
- **Don't use** after major refactoring

### What Happens
1. **Loads context** (latest implementation and plan)

2. **Discovers changed files** via git diff

3. **Runs Pass 1**:
   - Runs `/tooling check` (captures full output)
   - Runs `/tooling test` (even if check failed)
   - Spawns `code-reviewer` agent
   - Counts issues by severity

4. **Determines Pass 2**:
   ```
   IF any CRITICAL issues AND NOT --fast:
       TRIGGER Pass 2
   ELSE:
       SKIP Pass 2, write report
   ```

5. **Runs Pass 2** (if triggered):
   - Launches 4 specialist agents in parallel
   - Waits for all to complete
   - Aggregates findings, deduplicates issues

6. **Writes validation artifact**: `40_validation.md`

7. **Updates session index**

### Output
```
## RPIV Validation Complete

Created/Updated:
- $VAULT_BASE/<repo>/sessions/<session_id>/40_validation.md

### Pass 1 Results (Fast Surface Scan)
- /tooling check: PASS
- /tooling test: PASS (15/15)
- code-reviewer: APPROVE

Pass 1 Issues: Critical: 0 | Warnings: 2 | Suggestions: 3

### Pass 2 Status
**Pass 2 Skipped**: No critical issues found in Pass 1 ✓

---

**Total Issues**: Critical: 0 | Warnings: 2 | Suggestions: 3
**Verdict**: PASS

Next Steps:
- ✓ All checks passed
- Run `/tooling format` if not already done
- Ready for /commit
```

---

## Phase 6: Session Summary

### Command
```
/session_summary
/session_summary --session <session_id>
/session_summary --since <git_ref>
```

### What Happens
1. **Resolves session** (most recent or specified)

2. **Loads all session artifacts** (best-effort):
   - `00_context.md`, `index.md`
   - Latest research, plan, implementation, validation

3. **Summarizes code changes** via git diff/log

4. **Builds empirical verification playbook**:
   - Extracts from plan/implementation/validation
   - Infers from FastAPI code if needed
   - Constructs manual test scripts

5. **Creates Future Work section**:
   - Integration guidance
   - Known limitations
   - Recommended next steps

6. **Writes**: `50_session_summary.md`

### Empirical Verification Playbook
```markdown
## Empirical verification playbook

### Preconditions
- Environment: local
- Required env vars:
  - DATABASE_URL=...
  - JWT_SECRET=...

### Start the service
```bash
docker-compose up chatbot_backend
```

### Verify behavior

#### 1) POST /api/auth/login

**Route**: POST /api/auth/login

**Request**:
```bash
curl -i -X POST "http://localhost:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "secret"}'
```

**Expected**:
- Status: 200
- Response: `{"token": "...", "expires_at": "..."}`
- Side effects: Login event logged

**Negative case**:
```bash
curl -i -X POST "http://localhost:8001/api/auth/login" \
  -d '{"email": "invalid"}'
# Expected: 400 Bad Request
```
```

---

## Iteration Flow

When validation fails, the RPIV workflow supports iterations:

```
First iteration:
  10_research.md → D01_approach.md → 20_plan.md → 30_implementation.md → 40_validation.md (FAIL)

Discuss what went wrong:
  D02_retrospective.md

Fix cycle:
  21_plan.md → 31_implementation.md → 41_validation.md (FAIL)

Another fix:
  22_plan.md → 32_implementation.md → 42_validation.md (PASS)

Finalize:
  50_session_summary.md
```

**Note**: Discussion artifacts (DXX) can be created at any point when decisions need to be recorded. They're numbered sequentially (D01, D02, D03...) regardless of which phase they follow.

### Index Tracking
The `index.md` tracks all artifacts:
```markdown
## Progress

| Phase | Status | Artifact | Updated |
|-------|--------|----------|---------|
| Context | complete | [00_context.md] | 2026-01-15T14:30:00Z |
| Research | complete | [10_research.md] | 2026-01-15T14:35:00Z |
| Discussion | complete | [D01_approach.md] | 2026-01-15T14:40:00Z |
| Plan | complete | [20_plan.md] | 2026-01-15T14:45:00Z |
| Implement | complete | [30_implementation.md] | 2026-01-15T15:00:00Z |
| Validate | needs_attention | [40_validation.md] | 2026-01-15T15:15:00Z |
| Discussion | complete | [D02_retrospective.md] | 2026-01-15T15:20:00Z |
| Plan (fixes) | complete | [21_plan.md] | 2026-01-15T15:30:00Z |
| Implement (fixes) | complete | [31_implementation.md] | 2026-01-15T15:45:00Z |
| Validate (2nd) | **PASS** | [41_validation.md] | 2026-01-15T16:00:00Z |
```

---

## Session Continuity

### Create Handoff
When ending a session mid-work:
```
/create_handoff
```

Creates: `$VAULT_BASE/<repo>/handoffs/YYYY-MM-DD_HH-MM-SS_description.md`

### Resume Handoff
When starting a new session:
```
/resume_handoff path/to/handoff.md
```

The handoff includes:
- Task status
- Recent changes
- Learnings
- Artifacts
- Action items
- Next steps
