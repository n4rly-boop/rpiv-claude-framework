---
description: RPIV Validate phase - two-pass validation system. Pass 1 (fast surface scan) always runs. Pass 2 (deep multi-agent review) auto-triggers on critical issues.
model: opus
---

# RPIV Validate Phase

Run two-pass validation pipeline on implementation with **smart scoping**.

## Two-Pass System

**Pass 1** (always): `/tooling check` + `/tooling test` + `code-reviewer`. Collect ALL issues, never exit early.

**Pass 2** (conditional): Deep multi-agent review. Only triggers if Pass 1 finds CRITICAL issues.

### Pass 2 Agent Selection (Change-Type Gating)

| Change Type | Detection Pattern | Agents |
|-------------|-------------------|--------|
| Docs/config only | All files match `*.md, *.txt, *.json, *.yaml, *.toml, *.ini, *.cfg` | None (skip Pass 2) |
| Security-sensitive | Files in `**/auth/**, **/security/**, **/login/**` or match `*password*, *token*, *credential*` | security + defensive |
| API/schema change | Files in `**/api/**, **/routes/**, **/schema/**` or match `*openapi*, *swagger*` | integration + security |
| Localized fix | ≤3 files in ≤1 directory | defensive + logic |
| Multi-file feature | Everything else | All 4 agents |

**Flags**: `--fast` skips Pass 2. `--full` forces all 4 agents on ALL changed files.

## Process

### Step 1: Load Context & Knowledge

1. Find active session from `$VAULT_BASE/<repo_name>/sessions/`
2. Read latest implementation (`3?_implementation.md`) and plan (`2?_plan.md`)
3. Load knowledge for compliance checking:
   - `$VAULT_BASE/<repo_name>/knowledge/conventions/main.md` → rules to validate against
   - `$VAULT_BASE/<repo_name>/knowledge/patterns/main.md` → expected patterns to verify adherence
   - Any topic-specific knowledge files referenced in the plan
4. Check for `--fast` or `--full` flags

### Step 2: Discover Changed Files & Classify Change Type

```bash
git diff --name-only HEAD~N..HEAD  # Implementation commits
git status --porcelain              # Uncommitted changes
```

Classify using the change-type table above. Store `change_type` and `pass2_agents`.

### Step 3: Pass 1 — Fast Surface Scan

**Run ALL checks even if earlier ones fail:**

1. `/tooling check` — capture full output
2. `/tooling test` — capture full output
3. Spawn `code-reviewer` agent on changed files — include loaded conventions in the prompt so the reviewer checks convention compliance (naming, structure, error handling, import order)

**Collect files with issues** from all three sources. **Determine Pass 2 trigger:**

- `docs_config` → Skip Pass 2
- No CRITICAL issues → Skip Pass 2
- `--fast` flag → Skip Pass 2
- `--full` flag → Run all 4 agents on all changed files
- Otherwise → Run selected agents on files with issues only

### Step 4: Pass 2 — Deep Multi-Agent Analysis (if triggered)

Launch selected agents **in parallel**, passing `files_to_review` and relevant knowledge context:

```
IF "defensive-reviewer" in agents: Task(subagent_type: "defensive-reviewer", prompt includes known anti-patterns and error handling conventions)
IF "integration-reviewer" in agents: Task(subagent_type: "integration-reviewer", prompt includes API conventions and integration patterns)
IF "security-reviewer" in agents: Task(subagent_type: "security-reviewer", prompt includes security conventions and known pitfalls)
IF "logic-reviewer" in agents: Task(subagent_type: "logic-reviewer", prompt includes $LATEST_PLAN path and business logic patterns)
```

Collect results, deduplicate issues (same `file:line`), aggregate by severity.

### Step 5: Write Validation Artifact

Version: find existing `4?_validation.md`, increment. Write via `obsidian` MCP.

**Frontmatter** must include: `repo`, `scope`, `session`, `type: validation`, `created`, `updated`, `validation_mode`, `change_type`, `pass_2_triggered`, `pass_2_agents`, `pass_2_files`, `sources`.

**Body structure:**

```markdown
# Validation Report: <task_description>

## Validation Mode
- Pass 1: Completed
- Pass 2: <status and reason>
- Change Type: <type> → <agents selected>
- Scope: N agents on M files

## Summary

### Pass 1: Fast Surface Scan
| Check | Status | Critical | Warnings | Details |
|-------|--------|----------|----------|---------|

### Pass 2: Deep Multi-Agent Analysis
| Agent | Critical | Warnings | Suggestions | Status |
|-------|----------|----------|-------------|--------|

**Overall**: PASS / NEEDS_ATTENTION / FAIL

## Pass 1 Details
[For each check: status, command run, exit code, truncated output (max 50 lines), issue counts]

## Pass 2 Details (if ran)
[For each agent: focus area, critical/warning/suggestion tables with file:line]

## Convention Compliance
| Convention | Status | Notes |
|------------|--------|-------|
[Check changed files against loaded conventions. Flag violations as issues.]

## Success Criteria Check
[From plan: checkbox list of criteria with VERIFIED/NOT VERIFIED]

## Recommendations
### Must Fix (Blocking)
### Should Fix (Before Merge)
### Consider (Optional)

## Validation Verdict
**Ready for Merge**: YES / NO / WITH_CAVEATS
```

### Step 6: Update Session Index

Follow the standard index update protocol:
- **Progress table**: Update existing "Validate | pending" row (first time) or add iteration row ("Validate (2nd)", "Validate (3rd)")
- **Artifacts section**: Append new artifact link
- **Timeline**: Append timestamped entry

### Step 7: Report

```
## RPIV Validation Complete

Created/Updated:
- <vault_path>

### Change Analysis
- Change Type: <type>, Files Changed: N, Files with Issues: M

### Pass 1 Results
- /tooling check: <status>, /tooling test: <status>, code-reviewer: <status>
- Issues: Critical: N | Warnings: N | Suggestions: N

### Pass 2 Status
<Triggered (scoped/full) or Skipped (reason)>

**Total Issues**: Critical: N | Warnings: N | Suggestions: N
**Verdict**: <PASS/NEEDS_ATTENTION/FAIL>

### Next Steps
<Context-dependent recommendations based on verdict>
```
