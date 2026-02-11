# Commands Reference

Complete reference for all RPIV framework slash commands.

---

## RPIV Core Commands

### `/rpiv:start`

**Description**: Start an RPIV session with enhanced context gathering - scans vault for related knowledge, checks codebase, asks clarifying questions.

**Model**: `sonnet`

**Usage**:
```
/rpiv:start [task_description]
/rpiv:start "Add user authentication to API"
/rpiv:start --minimal                    # Skip context scan (fast start)
```

**Creates**:
- `$VAULT_BASE/<repo>/sessions/<session_id>/00_context.md` (enhanced)
- `$VAULT_BASE/<repo>/sessions/<session_id>/index.md`

**Enhanced Context Scan** (~2-3 min):
- Searches vault for related sessions
- Loads existing conventions/patterns
- Quick codebase scan for relevant files
- Interactive clarification questions

**Output**:
```
Session ID: <session_id>
Context: root|microservice
Task: <task_description>

Context Scan Results:
- Related sessions: N found
- Conventions: loaded|not found
- Patterns: N found
- Relevant files: N identified

Next: /rpiv:research (or /rpiv:discuss if questions remain)
```

---

### `/rpiv:discuss`

**Description**: Facilitate structured discussion and record decisions to vault. Produces decision summaries, not transcripts.

**Model**: `opus`

**Usage**:
```
/rpiv:discuss                           # Auto-detect context from latest artifacts
/rpiv:discuss --topic "approach"        # Specify topic for artifact naming
/rpiv:discuss --after research          # Discuss after specific phase
/rpiv:discuss --after validation        # Discuss validation results
```

**When to Use**:
- After research: Weigh approaches before planning (auto-suggested if open questions)
- After plan: Review design decisions before implementing
- After validation failure: Discuss what went wrong and how to fix
- Any time: When significant decisions need to be recorded

**Creates**:
- `$VAULT_BASE/<repo>/sessions/<session_id>/DXX_<topic>.md`

**Topic Defaults** (based on phase):
- After context → `scope`
- After research → `approach`
- After plan → `design`
- After implement → `review`
- After validation → `retrospective`

**Output**:
```
Key Decisions:
- <decision 1>
- <decision 2>

Impact:
- <how this affects next phase>

Next: <suggested command based on context>
```

**Note**: Discussion artifacts are **decision summaries** (300-500 lines max), not conversation transcripts. Focus on capturing the WHY behind decisions.

---

### `/rpiv:research`

**Description**: RPIV Research phase - gather context using distiller agents, write research artifact to vault.

**Model**: `opus`

**Usage**:
```
/rpiv:research                           # Use current session
/rpiv:research --session <session_id>    # Specify session
/rpiv:research --focus "authentication"  # Focus area
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

Next: /rpiv:discuss --topic "approach" (if open questions)
      /rpiv:plan (if no blocking questions)
```

**Note**: Auto-suggests `/rpiv:discuss` if research identifies open questions or high-risk items.

---

### `/rpiv:plan`

**Description**: RPIV Plan phase - create implementation plan from research. Requires research artifact unless `--no-research`.

**Model**: `opus`

**Usage**:
```
/rpiv:plan                              # Use research from current session
/rpiv:plan --session <session_id>       # Specify session
/rpiv:plan --no-research                # Skip research requirement
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

Next: /rpiv:implement
```

---

### `/rpiv:implement`

**Description**: RPIV Implement phase - execute implementation plan. REQUIRES plan artifact - will refuse without it.

**Model**: `opus`

**Usage**:
```
/rpiv:implement                         # Use plan from current session
/rpiv:implement --session <session_id>  # Specify session
/rpiv:implement --phase N               # Implement specific phase only
/rpiv:implement --resume                # Resume from last incomplete phase
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

Next: /rpiv:validate
```

---

### `/rpiv:validate`

**Description**: RPIV Validate phase - two-pass validation system.

**Model**: `opus`

**Usage**:
```
/rpiv:validate                          # Two-pass (default)
/rpiv:validate --fast                   # Pass 1 only
/rpiv:validate --session <session_id>   # Specify session
```

**Two-Pass System**:
- **Pass 1** (~5 min): `/tooling check`, `/tooling test`, `code-reviewer`
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
1. `/tooling format`
2. `/tooling check` (fix if fails)
3. `/tooling test` (fix if fails)
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
5. Verify with `/tooling format` and `/tooling check`

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
| `/rpiv:start` | sonnet | Start RPIV session (enhanced context) |
| `/rpiv:discuss` | opus | Facilitate & record decisions |
| `/rpiv:research` | opus | Research phase |
| `/rpiv:plan` | opus | Planning phase |
| `/rpiv:implement` | opus | Implementation phase |
| `/rpiv:validate` | opus | Validation phase |
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
