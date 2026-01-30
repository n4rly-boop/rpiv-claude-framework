# Commands Reference

Complete reference for all RPIV framework slash commands.

---

## RPIV Core Commands

### `/rpiv_start`

**Description**: Start an RPIV session - creates session folder in vault with context and index artifacts.

**Model**: `sonnet`

**Usage**:
```
/rpiv_start [task_description]
/rpiv_start "Add user authentication to API"
```

**Creates**:
- `$VAULT_BASE/<repo>/sessions/<session_id>/00_context.md`
- `$VAULT_BASE/<repo>/sessions/<session_id>/index.md`

**Output**:
```
Session ID: <session_id>
Context: root|microservice
Task: <task_description>

Next: /rpiv_research
```

---

### `/rpiv_research`

**Description**: RPIV Research phase - gather context using distiller agents, write research artifact to vault.

**Model**: `opus`

**Usage**:
```
/rpiv_research                           # Use current session
/rpiv_research --session <session_id>    # Specify session
/rpiv_research --focus "authentication"  # Focus area
```

**Prerequisites**:
- Active RPIV session
- `00_context.md` exists

**Spawns Agents**:
- `microservice-distiller` (if root repo)
- `codebase-locator`
- `codebase-pattern-finder`
- `repo-doc-distiller` (if inside microservice)
- `codebase-analyzer`

**Creates**:
- `$VAULT_BASE/<repo>/sessions/<session_id>/1X_research.md`

**Output**:
```
Key Findings: [list]
Open Questions: N
Risks Identified: N

Next: /rpiv_plan
```

---

### `/rpiv_plan`

**Description**: RPIV Plan phase - create implementation plan from research. Requires research artifact unless `--no-research`.

**Model**: `opus`

**Usage**:
```
/rpiv_plan                              # Use research from current session
/rpiv_plan --session <session_id>       # Specify session
/rpiv_plan --no-research                # Skip research requirement
```

**Prerequisites**:
- Active RPIV session
- `1X_research.md` exists (unless `--no-research`)

**Creates**:
- `$VAULT_BASE/<repo>/sessions/<session_id>/2X_plan.md`

**Output**:
```
Phases: N
Files affected: N
Risk level: Low|Medium|High

Next: /rpiv_implement
```

---

### `/rpiv_implement`

**Description**: RPIV Implement phase - execute implementation plan. REQUIRES plan artifact - will refuse without it.

**Model**: `opus`

**Usage**:
```
/rpiv_implement                         # Use plan from current session
/rpiv_implement --session <session_id>  # Specify session
/rpiv_implement --phase N               # Implement specific phase only
/rpiv_implement --resume                # Resume from last incomplete phase
```

**Prerequisites**:
- Active RPIV session
- `2X_plan.md` exists (REQUIRED, cannot be skipped)

**Creates**:
- `$VAULT_BASE/<repo>/sessions/<session_id>/3X_implementation.md`

**Output**:
```
Phases completed: N/total
Files changed: N
Lines: +added, -removed

Next: /rpiv_validate
```

---

### `/rpiv_validate`

**Description**: RPIV Validate phase - two-pass validation system.

**Model**: `opus`

**Usage**:
```
/rpiv_validate                          # Two-pass (default)
/rpiv_validate --fast                   # Pass 1 only
/rpiv_validate --session <session_id>   # Specify session
```

**Two-Pass System**:
- **Pass 1** (~5 min): `make check`, `make test`, `code-reviewer`
- **Pass 2** (~15-20 min): 4 specialist agents in parallel (auto-triggers on critical issues)

**Creates**:
- `$VAULT_BASE/<repo>/sessions/<session_id>/4X_validation.md`

**Output**:
```
Pass 1 Issues: Critical: N | Warnings: N | Suggestions: N
Pass 2 Status: Triggered|Skipped
Verdict: PASS|NEEDS_ATTENTION|FAIL

Next: /commit or fix issues
```

---

## Workflow Commands

### `/session_summary`

**Description**: Summarize RPIV session artifacts and produce an empirical verification playbook.

**Model**: `opus`

**Usage**:
```
/session_summary
/session_summary --session <session_id>
/session_summary --since <git_ref>
/session_summary --light
```

**Creates**:
- `$VAULT_BASE/<repo>/sessions/<session_id>/50_session_summary.md`

**Output**:
- Task summary
- Code changes
- Empirical verification playbook (curl commands, expected responses)
- Future work & integration guidance

---

### `/debug`

**Description**: Debug issues by investigating logs, database state, and git history.

**Usage**:
```
/debug
/debug path/to/plan.md
```

**Process**:
1. Ask user to describe the problem
2. Spawn parallel agents to investigate:
   - Recent logs
   - Application state
   - Git and file state
3. Present debug report with root cause and next steps

**Note**: Investigation only - does not edit files.

---

### `/pr_ready`

**Description**: Full pre-PR checklist - format, check, test, simplify.

**Usage**:
```
/pr_ready
```

**Process**:
1. `make format`
2. `make check` (fix if fails)
3. `make test` (fix if fails)
4. Launch `code-simplifier` agent
5. Final verification

**Output**:
```
Format: ✓/✗
Lint & Types: ✓/✗
Tests: ✓/✗
Code Quality: Simplifications applied

Status: READY | NEEDS WORK
```

---

### `/create_handoff`

**Description**: Create handoff document for transferring work to another session.

**Usage**:
```
/create_handoff
```

**Creates**:
- `$VAULT_BASE/<repo>/handoffs/YYYY-MM-DD_HH-MM-SS_description.md`

**Contents**:
- Task(s) and status
- Critical references
- Recent changes
- Learnings
- Artifacts
- Action items & next steps

---

### `/resume_handoff`

**Description**: Resume work from handoff document with context analysis and validation.

**Usage**:
```
/resume_handoff                                    # List available handoffs
/resume_handoff <repo>/handoffs/YYYY-MM-DD_....md  # Resume specific handoff
```

**Process**:
1. Read handoff document
2. Spawn research tasks to verify current state
3. Present analysis and recommended actions
4. Create task list
5. Begin implementation

---

## Code Commands

### `/review`

**Description**: Review changed code for issues, then optionally simplify.

**Usage**:
```
/review
```

**Process**:
1. Get changed files via git diff
2. Spawn agents:
   - `codebase-analyzer` - Check for issues
   - `codebase-pattern-finder` - Check pattern conformance
3. Synthesize review with issues, deviations, suggestions

---

### `/simplify`

**Description**: Review changed code and simplify without breaking functionality.

**Usage**:
```
/simplify
```

**Process**:
1. Get changed files via git diff
2. Spawn `code-simplifier` agent
3. Review suggestions
4. Apply approved changes
5. Verify with `make format && make check`

**What Gets Simplified**:
- Verbose conditionals → concise expressions
- Unnecessary intermediate variables
- Loops → comprehensions (when clearer)
- Nested ifs → early returns
- String concat → f-strings

---

## Git Commands

### `/commit`

**Description**: Create git commits with user approval and no Claude attribution.

**Usage**:
```
/commit
```

**Process**:
1. Review conversation and `git status`/`git diff`
2. Plan commit(s) with messages
3. Present plan to user for approval
4. Execute upon confirmation

**Important**:
- Never adds co-author or Claude attribution
- Commits authored solely by user
- Uses imperative mood in messages

---

### `/describe_pr`

**Description**: Generate comprehensive PR descriptions following repository templates.

**Usage**:
```
/describe_pr
```

**Prerequisites**:
- PR template at `$VAULT_BASE/<repo>/templates/pr_description.md`

**Process**:
1. Read PR template
2. Identify PR (current branch or list open PRs)
3. Gather PR info via `gh` CLI
4. Analyze changes thoroughly
5. Run verification commands
6. Generate description
7. Ask for confirmation
8. Update PR via `gh pr edit`

---

## Research Commands

### `/docs`

**Description**: Generate or update documentation for code, APIs, or features.

**Model**: `sonnet`

**Usage**:
```
/docs src/services/auth.ts              # Document specific file
/docs api                               # Generate API docs
/docs readme                            # Update README
/docs feature "user authentication"     # Document feature
```

**Creates**:
- `$VAULT_BASE/<repo>/knowledge/api/reference.md`
- `$VAULT_BASE/<repo>/knowledge/services/<service>.md`
- Or updates inline documentation

---

### `/research_codebase`

**Description**: Document codebase as-is comprehensively.

**Model**: `opus`

**Usage**:
```
/research_codebase
```

Then provide research query when prompted.

**Process**:
1. Read mentioned files
2. Decompose research question
3. Spawn parallel agents:
   - `codebase-locator` - Find where code lives
   - `codebase-analyzer` - Understand how code works
   - `codebase-pattern-finder` - Find patterns
4. Synthesize findings
5. Write research document

**Creates**:
- `$VAULT_BASE/<repo>/research/YYYY-MM-DD-description.md`
- Or `$VAULT_BASE/<repo>/sessions/<session_id>/1X_research.md` if in RPIV session

---

## Planning Commands

### `/extract_conventions`

**Description**: Extract code conventions, patterns, architecture, and dependencies from codebase.

**Model**: `opus`

**Usage**:
```
/extract_conventions
```

**Process**:
1. Initial scan - identify stack, docs, configs
2. Deep analysis via parallel agents:
   - Code Style Analysis
   - Architecture Analysis
   - Pattern Analysis
   - Dependency Analysis
3. Synthesize findings
4. Write documentation

**Creates**:
- `$VAULT_BASE/<repo>/knowledge/conventions/main.md`
- `$VAULT_BASE/<repo>/knowledge/patterns/main.md`
- `$VAULT_BASE/<repo>/knowledge/architecture.md`
- `$VAULT_BASE/<repo>/knowledge/dependencies.md`

---

## Quick Reference

| Command | Model | Purpose |
|---------|-------|---------|
| `/rpiv_start` | sonnet | Start RPIV session |
| `/rpiv_research` | opus | Research phase |
| `/rpiv_plan` | opus | Planning phase |
| `/rpiv_implement` | opus | Implementation phase |
| `/rpiv_validate` | opus | Validation phase |
| `/session_summary` | opus | Create session summary |
| `/debug` | - | Debug issues |
| `/pr_ready` | - | Pre-PR checklist |
| `/create_handoff` | - | Create handoff |
| `/resume_handoff` | - | Resume from handoff |
| `/review` | - | Review code changes |
| `/simplify` | - | Simplify code |
| `/commit` | - | Create git commits |
| `/describe_pr` | - | Generate PR description |
| `/docs` | sonnet | Generate documentation |
| `/research_codebase` | opus | Research codebase |
| `/extract_conventions` | opus | Extract conventions |
