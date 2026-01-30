# Best Practices

Tips, patterns, and anti-patterns for effective RPIV usage.

---

## Core Principles

### 1. Artifacts Over Chat

**DO**:
```
Write findings to vault, return path + 10-line summary
```

**DON'T**:
```
Paste 500 lines of code analysis into chat
```

### 2. File Pointers Over Code Dumps

**DO**:
```
The authentication logic is in `src/middleware/auth.py:45-67`
```

**DON'T**:
```
Here's the entire auth middleware:
[200 lines of code]
```

### 3. Make Commands Only

**DO**:
```bash
make check
make test
make format
```

**DON'T**:
```bash
ruff check .
pytest tests/
black .
mypy src/
```

---

## Workflow Patterns

### Starting a Session

**Good**: Specific task description
```
/rpiv_start "Add JWT authentication to /api/users endpoint with refresh token support"
```

**Bad**: Vague description
```
/rpiv_start "fix auth"
```

### Research Phase

**Good**: Let distillers do the work
- Spawns parallel agents
- Writes to vault
- Returns only paths

**Bad**: Manual exploration
- Reading files one by one in chat
- Pasting code snippets to understand

### Plan Phase

**Good**: Phased with specific files
```markdown
## Phase 1: Add JWT Middleware
**Goal**: Create reusable auth middleware

### Changes
#### `src/middleware/auth.py`
At line 45, add JWT validation logic following pattern in `knowledge/patterns/middleware.md`

### Validation
- [ ] make check
- [ ] make test
- [ ] Manual: curl -H "Authorization: Bearer <token>" /api/protected
```

**Bad**: Vague plan
```markdown
## Step 1
Add authentication somehow
```

### Implementation Phase

**Good**: Phase by phase with validation
```
Phase 1 Complete - Ready for Validation

Changes made:
- `auth.py:45-67` - Added JWT validation

Validation:
- [x] make check - PASSED
- [x] make test - PASSED

Proceed to Phase 2? (y/n)
```

**Bad**: All at once without checks
- Implementing everything before any validation
- Skipping `make check` between phases

### Validation Phase

**Good**: Use two-pass system
```
/rpiv_validate           # Full validation
/rpiv_validate --fast    # Quick iteration
```

**Bad**: Manual validation only
- Running tests but skipping agent review
- Not using the specialized reviewers

---

## Validation Best Practices

### When to Use `--fast`

**Use `--fast`**:
- Quick iterations during active development
- You know the issue and just want surface validation
- Time-constrained and will do full validation later

**Don't use `--fast`**:
- Before creating PR
- After major refactoring
- When touching security-sensitive code
- When modifying API contracts

### Pass 2 Triggers

Pass 2 only triggers on CRITICAL issues:
- Test failures
- Type errors
- Linting errors
- Security vulnerabilities flagged by code-reviewer

Warnings alone don't trigger Pass 2.

---

## Manual Testing Requirements

Every plan MUST include manual testing steps.

### Good Manual Testing Plan
```markdown
## Manual Testing Plan

### Environment Setup
- Service: `docker-compose up chatbot_backend`
- Required env: `JWT_SECRET=test-secret`

### Feature: POST /api/auth/login

**Request**:
```bash
curl -i -X POST "http://localhost:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "secret"}'
```

**Expected**:
- Status: 200
- Body: `{"token": "...", "refresh_token": "..."}`

**Side Effects**:
- Logs: "User login successful: test@example.com"
- Redis: New session key at `session:<user_id>`

**Negative Cases**:
```bash
# Invalid password
curl -i -X POST "http://localhost:8001/api/auth/login" \
  -d '{"email": "test@example.com", "password": "wrong"}'
# Expected: 401 Unauthorized
```
```

### Bad Manual Testing Plan
```markdown
## Testing
Test the login endpoint works.
```

---

## Session Continuity

### Creating Handoffs

Create a handoff when:
- Ending session mid-work
- Context window getting full
- Switching to different task temporarily

```
/create_handoff
```

Include in handoff:
- Task status (completed, in progress, planned)
- Recent changes with file:line
- Key learnings
- Action items

### Resuming Work

```
/resume_handoff <repo>/handoffs/2026-01-15_14-30-22_add-auth.md
```

The resume process:
1. Reads handoff completely
2. Spawns agents to verify current state
3. Presents analysis
4. Asks for confirmation before proceeding

---

## Context Management

### Budget Awareness

| Artifact Type | Max Lines |
|---------------|-----------|
| Distiller output | 200-400 |
| Analyzer output | 200-600 |
| Locator output | 100-300 |

### Avoiding Context Overflow

**DO**:
- Use distillers for deep analysis
- Return paths, not content
- Keep summaries to 10 lines

**DON'T**:
- Read large files in main context
- Paste agent outputs into chat
- Include full code blocks in responses

---

## Anti-Patterns

### 1. Skipping Phases

**Bad**:
```
/rpiv_start "add feature"
[immediately starts coding without research/plan]
```

**Good**:
```
/rpiv_start "add feature"
/rpiv_research
/rpiv_plan
/rpiv_implement
/rpiv_validate
```

### 2. Ignoring Validation Failures

**Bad**:
```
Validation: FAIL (3 critical issues)
[ignores and commits anyway]
```

**Good**:
```
Validation: FAIL (3 critical issues)
[fixes issues]
/rpiv_validate
Validation: PASS
/commit
```

### 3. Manual File Operations

**Bad**:
```bash
# Creating artifacts manually
echo "# Research" > .claude/artifacts/research.md
```

**Good**:
```
# Use MCP server
obsidian.write_note("<repo>/sessions/<id>/10_research.md", content)
```

### 4. Overwriting Artifacts

**Bad**:
```
# Modifying existing artifact
10_research.md → (overwritten with new research)
```

**Good**:
```
# Version increment
10_research.md exists → create 11_research.md
```

### 5. Breaking the Black Box Rule

**Bad** (from root repo):
```
Reading internal implementation of microservice/src/internal/...
```

**Good** (from root repo):
```
Using microservice-distiller to document external interfaces only
```

---

## Model Selection

| Command | Model | Rationale |
|---------|-------|-----------|
| `/rpiv_start` | sonnet | Simple setup task |
| `/rpiv_research` | opus | Complex synthesis |
| `/rpiv_plan` | opus | Architecture decisions |
| `/rpiv_implement` | opus | Code generation |
| `/rpiv_validate` | opus | Comprehensive review |
| Reviewer agents | sonnet | Focused analysis |
| Distiller agents | sonnet | Context compression |

### When to Use Haiku

Consider haiku for:
- Simple file location tasks
- Pattern matching without analysis
- Quick status checks

---

## Troubleshooting

### MCP Connection Issues

```
Error: MCP server not responding
```

**Check**:
1. Obsidian running
2. MCP plugin enabled
3. Vault path correct in settings.json

### Session Not Found

```
Error: No active RPIV session found
```

**Fix**:
```
/rpiv_start "task description"
```

### Plan Requirement Error

```
Error: Plan artifact not found
```

**Fix**:
```
/rpiv_plan
# Then retry /rpiv_implement
```

### Research Requirement Error

```
Error: Research artifact not found
```

**Fix**:
```
/rpiv_research
# Then retry /rpiv_plan
```

Or skip (not recommended):
```
/rpiv_plan --no-research
```
