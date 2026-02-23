---
description: Run full RPIV pipeline autonomously - Start through Summary with smart decision gates
model: opus
---

# RPIV Auto — Autonomous Pipeline

Run Start → Research → Plan → Implement → Validate [→ Fix Cycle] → Summarize as a single command. Asks the user **only when there is a real decision to make**.

## Flags

- `--micro`, `--focused`, `--full`: Research tier override
- `--fast`: Skip validation Pass 2
- `--resume`: Continue from last completed phase (auto-detected from artifacts)

## Phase 0: Session Detection & Resume

```
IF --resume OR user says "resume/continue":
    Find most recent session from $VAULT_BASE/<repo_name>/sessions/
    Read index.md → determine last completed phase from progress table
    Skip to next incomplete phase (jump to that phase section below)
    Print: "[auto] Resuming session <id> from Phase <N>: <phase_name>"

ELSE:
    Run full pipeline from Phase 1
```

## Phase 1: Start

Same logic as `/rpiv:start` with auto-decisions:

1. Determine context (repo root, branch, commit, monorepo detection)
2. Generate session ID: `YYYYMMDD-HHMMSS-short-description`
3. Fast context scan (vault + codebase-locator agent)
4. Research tier detection (same heuristics as start.md)

**Auto-decisions** (skip AskUserQuestion):
- Related sessions found → auto-apply context (don't ask "Build on previous work?")
- Conventions found → auto-apply as constraints (don't ask "Apply these?")

**Decision gate — ASK USER when**:
- Task is ambiguous or scope unclear → use `AskUserQuestion` with targeted clarifying questions
- If task is well-defined → proceed without asking

5. Write `00_context.md` (add `auto_mode: true` to frontmatter) and `index.md` via `obsidian` MCP
6. Print: `[auto] Phase 1/7 complete: Start | Artifact: <path> | Next: Research`

## Phase 2: Research

Same logic as `/rpiv:research`:

1. Determine tier: explicit flag → recommended from context → `focused` default
2. Load existing knowledge, identify gaps
3. Execute by tier:
   - **Micro**: Direct synthesis, no agents
   - **Focused**: `codebase-analyzer` agent on relevant paths
   - **Full**: All distillers in parallel (same agent set as research.md)
4. Synthesize findings, write `1X_research.md` via `obsidian` MCP, update index

**Decision gate — ASK USER when**:
- Open questions exist with HIGH impact (blocks design, multiple valid interpretations) → present questions via `AskUserQuestion`
- Low-impact open questions → note in artifact, proceed

5. Print: `[auto] Phase 2/7 complete: Research | Artifact: <path> | Next: Plan`

## Phase 3: Plan

Same logic as `/rpiv:plan` with auto-decisions:

1. Load context, research, and knowledge (conventions = hard constraints, patterns = preferred solutions)
2. Analyze: happy path, edge cases, tricky parts
3. Design phases, manual test plan, rollback plan, success criteria

**Auto-decisions** (skip AskUserQuestion):
- **SKIP** the "Is this understanding correct?" confirmation (Step 3 of plan.md)
- Single clear approach → proceed without asking

**Decision gate — ASK USER when**:
- Multiple valid approaches with **materially different tradeoffs** (performance vs simplicity, breaking change vs compatibility, etc.) → present options via `AskUserQuestion`
- Scope is significantly larger than expected → ask "Scope is X files across Y components. Proceed or narrow?"

4. Write `2X_plan.md` via `obsidian` MCP, update index
5. Print: `[auto] Phase 3/7 complete: Plan | Artifact: <path> | Next: Implement`

## Phase 4: Implement

Same logic as `/rpiv:implement` with auto-decisions:

1. Load plan, knowledge (conventions, patterns)
2. For each plan phase:
   a. Read all files mentioned
   b. Check knowledge for conventions BEFORE writing code
   c. Apply changes following plan specs
   d. Run `/tooling format` then `/tooling check`
      - If check fails: attempt fix, retry (up to 2 mechanical retries)
      - These formatting retries do NOT count toward the fix cycle limit
   e. Run `/tooling test` — fix failures before continuing
   f. Update tracking artifact

**Auto-decisions** (skip AskUserQuestion):
- **SKIP** per-phase "Proceed to Phase N+1?" gates
- Plan deviations that are mechanical (different line numbers, minor API changes) → auto-adapt, document in artifact

**Decision gate — ASK USER when**:
- A plan requirement is **fundamentally blocked** (not just a different approach — actually impossible) → explain blocker, present options via `AskUserQuestion`

3. Write `3X_implementation.md` via `obsidian` MCP, update index
4. Print: `[auto] Phase 4/7 complete: Implement | Artifact: <path> | Next: Validate`

## Phase 5: Validate

Same logic as `/rpiv:validate`:

1. Discover changed files, classify change type (same table as validate.md)
2. **Pass 1** (always): `/tooling check` + `/tooling test` + `code-reviewer` agent
3. **Pass 2** (conditional, same gating as validate.md):
   - `--fast` → skip
   - No CRITICAL issues → skip
   - Otherwise → spawn selected agents per change-type table
4. Write `4X_validation.md` via `obsidian` MCP, update index

**Verdict routing**:
- **PASS** → proceed to Phase 7 (Summary)
- **FAIL** → enter Phase 6 (Fix Cycle)

5. Print: `[auto] Phase 5/7 complete: Validate | Verdict: <PASS/FAIL> | Artifact: <path> | Next: <Summary or Fix Cycle>`

## Phase 6: Fix Cycle (max 2 iterations)

```
fix_attempts = 0

WHILE verdict == FAIL AND fix_attempts < 2:
    1. Read validation issues from latest 4?_validation.md
    2. Implement fixes (same as implement --fix logic)
       - Consult knowledge for correct patterns
       - Fix root causes, not symptoms
    3. Run /tooling format + /tooling check (up to 2 mechanical retries)
    4. Write next 3{X+1}_implementation.md via obsidian MCP
    5. Re-validate: Pass 1 + conditional Pass 2 (same gating)
    6. Write next 4{X+1}_validation.md via obsidian MCP
    7. Update index with new artifacts
    8. fix_attempts++
    9. Print: "[auto] Fix cycle {fix_attempts}/2 | Verdict: <PASS/FAIL>"
```

**Decision gate — ASK USER when**:
- Still FAIL after 2 fix cycles → use `AskUserQuestion`:
  - "These issues persist after 2 fix attempts: [list]. Options:"
  - A) Generate summary as-is (I'll fix manually)
  - B) Try one more fix cycle
  - C) Abandon session

**If PASS** at any point → proceed to Phase 7.

## Phase 7: Summary

Same logic as `/session_summary`:

1. Resolve baseline commit from `00_context.md`
2. Load all session artifacts
3. Summarize code changes (`git diff`, `git log`, `git status`)
4. Build verification playbook (curl commands, expected responses, side effects)
5. Build future work section
6. Write `50_session_summary.md` via `obsidian` MCP, update index

7. Print final report:

```
## RPIV Auto Complete

Created/Updated:
- <list all artifact paths>

Pipeline: Start → Research → Plan → Implement → Validate → Summary
Research Tier: <tier> | Phases: N | Fix Cycles: N
Verdict: <PASS/FAIL/WITH_CAVEATS>

Key Changes:
- <1-3 line summary>

Verification: See 50_session_summary.md for full playbook

Session: <session_path>
```

## Decision Gates Summary

| Gate | Trigger | Ask User | Auto-Proceed When |
|------|---------|----------|-------------------|
| Ambiguous task | Start: task unclear | Clarifying questions | Task is well-defined |
| Research questions | Research: high-impact open questions | Present questions | No high-impact questions |
| Approach choice | Plan: multiple valid approaches | Options with tradeoffs | Single clear approach |
| Scope surprise | Plan: scope much larger than expected | "Scope is X. Proceed?" | Scope matches expectation |
| Implementation blocker | Implement: requirement impossible | Explain blocker + options | All requirements achievable |
| Fix cycle exhausted | Validate: FAIL after 2 fix cycles | Present remaining issues | Validation passes |

## Error Handling

- **MCP write failure**: Retry once. If still fails, pause and report — artifact data is in context, not lost. User can retry or save manually.
- **Subagent failure**: Log warning, continue with reduced information. Only escalate if ALL agents for a phase fail.
- **No test suite**: `/tooling test` reports SKIPPED, not FAIL. Note "manual verification required" in validation artifact.
- **Context approaching limits**: Write checkpoint to index (mark last completed phase), suggest user run `/rpiv:auto --resume`.

## Key Differences from Manual RPIV

| Aspect | Manual | Auto |
|--------|--------|------|
| Related sessions | Asks "Build on?" | Auto-applies |
| Conventions | Asks "Apply these?" | Auto-applies |
| Plan confirmation | Asks "Understanding correct?" | Skips |
| Phase transitions | Asks "Proceed to N+1?" | Auto-proceeds |
| Plan deviations | Asks user to choose | Auto-adapts (documents) |
| Research questions | Always presents | Only HIGH impact |
| Approach choice | Always presents | Only when materially different |
