---
description: Start an RPIV session - creates session folder in vault with context and index artifacts
model: sonnet
---

# RPIV Session Start

Initialize a new RPIV session.

## Process

### Step 1: Determine Context

```bash
REPO_ROOT=$(git rev-parse --show-toplevel)
REPO_NAME=$(basename "$REPO_ROOT")
CURRENT_BRANCH=$(git branch --show-current)
CURRENT_COMMIT=$(git rev-parse --short HEAD)
```

- Detect context type: check for nested `.git` directories (monorepo vs microservice)
- Generate session ID: `YYYYMMDD-HHMMSS-short-description`

### Step 2: Fast Context Scan (skip if `--minimal`)

#### 2.1: Scan Vault
Using `obsidian` MCP:
- Search for related sessions by task keywords
- Read existing conventions (`knowledge/conventions/main.md`)
- List patterns (`knowledge/patterns/`)
- Check recent handoffs (`handoffs/`)

#### 2.2: Quick Codebase Scan
Spawn `codebase-locator` agent: find top 10 relevant files (paths only, no analysis).

#### 2.3: Determine Research Tier

| Condition | Tier | Reason |
|-----------|------|--------|
| ≤3 files AND (bug fix OR simple change) AND conventions exist | micro | Small scope, synthesis sufficient |
| ≤10 files AND localized (≤3 dirs) AND NOT architectural | focused | Targeted analysis sufficient |
| Architectural OR refactor OR >10 files | full | Comprehensive research needed |
| Default | focused | Safe middle ground |

Task type keywords: fix/bug/patch → bug_fix, update/change/modify → simple, add/implement/create → feature, refactor/restructure → refactor, architecture/migrate/integrate → architectural.

### Step 3: Interactive Clarification (MANDATORY when applicable)

**NEVER fabricate user answers.** If there are questions to ask, you MUST use `AskUserQuestion` and wait for real responses. Do NOT fill in the "User Clarifications" table yourself.

Use `AskUserQuestion` when ANY of these are true:
- Related sessions found → Ask: "Build on previous work?"
- Conventions/patterns found → Ask: "Apply these constraints?"
- Task is ambiguous → Ask targeted questions about scope/approach

If none of these conditions apply, write "No clarifications needed" in the artifact. Do NOT invent question/answer pairs.

### Step 4: Create Session Structure

Use `obsidian` MCP to write `00_context.md` and `index.md`.

**00_context.md** frontmatter includes: `repo`, `scope`, `session`, `type: context`, `recommended_research_tier`, `tier_reason`, `created`, `updated`, `sources`.

**00_context.md** body sections:
- Task description
- User Clarifications (from Step 3 responses, or "No clarifications needed")
- Repository Context (repo, branch, commit, context type)
- Detected Microservices (if root monorepo)
- Related Knowledge (sessions, conventions, patterns from vault scan)
- Relevant Files (top 10 from codebase scan)
- Recommended Research Tier (with heuristic inputs)
- Environment (VAULT_BASE, session path)
- Session Goals (checklist: research, plan, implement, validate)

**index.md** frontmatter: `repo`, `scope`, `session`, `type: index`, `created`, `updated`.

**index.md** body: Task, Progress table (Context=complete, Research/Plan/Implement/Validate=pending), Artifacts list, Timeline, Notes.

### Step 5: Determine Next Step

- Open questions/ambiguous task → Suggest `/rpiv_discuss --topic "scope"`
- Rich context found → Suggest `/rpiv_research`
- Default → Suggest `/rpiv_research`

### Step 6: Report

```
## RPIV Session Started

Created/Updated:
- <session_path>/00_context.md
- <session_path>/index.md

Session ID: <id>, Context: <type>, Task: <description>

### Context Scan Results
- Related sessions: N, Conventions: loaded/not found, Patterns: N, Relevant files: N

### Recommended Research Tier
**<tier>** - <reason>
Override with: /rpiv_research --micro, --focused, or --full

Next: /rpiv_research
```
