---
description: Start an RPIV session - creates session folder in vault with context and index artifacts
model: sonnet
---

# RPIV Session Start

Initialize a new RPIV session.

## Process

### Step 1: Determine Context

1. **Get repo information**:
   ```bash
   REPO_ROOT=$(git rev-parse --show-toplevel)
   REPO_NAME=$(basename "$REPO_ROOT")
   CURRENT_BRANCH=$(git branch --show-current)
   CURRENT_COMMIT=$(git rev-parse --short HEAD)
   ```

2. **Detect context type**:
   - Check if we're in root monorepo or inside a microservice
   - Look for nested `.git` directories to identify microservices
   ```bash
   # If current dir has nested .git dirs, we're in root
   find . -maxdepth 2 -name .git -type d -not -path './.git' | head -5
   ```

3. **Generate session ID**:
   - Format: `YYYYMMDD-HHMMSS-short-description`
   - Example: `20260111-143022-add-auth`

### Step 2: Fast Context Scan (Medium Depth, ~2-3 min)

**Skip this step if `--minimal` flag provided.**

#### 2.1: Scan Vault for Related Knowledge

Use `obsidian` MCP to search:

```
1. Search for related sessions:
   - obsidian.search_notes(query=<keywords from task>)
   - Look in: $VAULT_BASE/<repo>/sessions/
   - Find sessions with similar task descriptions

2. Check existing knowledge:
   - Read: $VAULT_BASE/<repo>/knowledge/conventions/main.md (if exists)
   - Read: $VAULT_BASE/<repo>/knowledge/patterns/*.md (list)
   - Check: $VAULT_BASE/<repo>/knowledge/microservices/ (if root repo)

3. Check for recent handoffs:
   - List: $VAULT_BASE/<repo>/handoffs/ (last 5)
```

#### 2.2: Quick Codebase Scan

Spawn `codebase-locator` agent (quick mode):

```
Prompt: "Find files related to: <task_description>
         Return only file paths, grouped by relevance.
         Limit: top 10 most relevant files.
         Do NOT analyze content - just locate."
```

#### 2.3: Collect Scan Results

Aggregate findings:
- Related sessions found: [list of session IDs]
- Conventions loaded: yes/no
- Patterns found: [list of pattern names]
- Relevant files: [list of paths]

#### 2.4: Determine Recommended Research Tier

Analyze context to recommend optimal research depth:

```
# Inputs for heuristic
relevant_files_count = len(relevant_files)
task_lower = task_description.lower()
directories_touched = unique directories from relevant_files
conventions_exist = conventions loaded from vault

# Task type detection
is_bug_fix = any(word in task_lower for word in ["fix", "bug", "patch", "hotfix"])
is_simple_change = any(word in task_lower for word in ["update", "change", "modify", "rename"])
is_feature = any(word in task_lower for word in ["add", "implement", "create", "build"])
is_refactor = any(word in task_lower for word in ["refactor", "restructure", "reorganize"])
is_architectural = any(word in task_lower for word in ["architecture", "migrate", "integrate", "overhaul"])

# Directory spread
single_directory = len(directories_touched) <= 1
localized_change = len(directories_touched) <= 3

# Decision tree
IF relevant_files_count <= 3 AND (is_bug_fix OR is_simple_change) AND conventions_exist:
    recommended_tier = "micro"
    reason = "Small scope with existing conventions - synthesis sufficient"

ELSE IF relevant_files_count <= 10 AND localized_change AND NOT is_architectural:
    recommended_tier = "focused"
    reason = "Localized change - targeted analysis sufficient"

ELSE IF is_architectural OR is_refactor OR relevant_files_count > 10:
    recommended_tier = "full"
    reason = "Cross-cutting change - comprehensive research needed"

ELSE:
    recommended_tier = "focused"  # safe middle ground
    reason = "Moderate scope - targeted analysis recommended"
```

**Store in context for research phase to use.**

### Step 3: Interactive Clarification

Based on scan results, ask targeted questions using `AskUserQuestion`:

**If related sessions found:**
```
I found a related session from <date>: "<task description>"
Should I reference its artifacts for this session?
- Yes, build on previous work
- No, start fresh
```

**If conventions/patterns found:**
```
I found existing patterns that may apply:
- <pattern 1>: <brief description>
- <pattern 2>: <brief description>

Should I use these as constraints for this task?
- Yes, follow existing patterns
- No, this task may need different approaches
- Let me clarify which ones apply
```

**If task is ambiguous:**
```
A few clarifying questions about "<task>":

1. <Specific question based on context>
   - Option A
   - Option B

2. <Scope question>
   - Minimal (just the core feature)
   - Standard (core + common edge cases)
   - Comprehensive (full implementation with tests)
```

**Collect responses** for inclusion in context artifact.

### Step 4: Create Session Structure

Use `obsidian` MCP server to create:

```
$VAULT_BASE/<repo_name>/sessions/<session_id>/
├── 00_context.md
└── index.md
```

### Step 5: Write 00_context.md (Enhanced)

```markdown
---
repo: <repo_name>
scope: <root|microservice>
microservice: <name_or_null>
session: <session_id>
type: context
recommended_research_tier: <micro|focused|full>
tier_reason: <reason from heuristic>
created: <iso8601>
updated: <iso8601>
sources:
  - git rev-parse --show-toplevel
  - git branch --show-current
  - vault search results
  - codebase-locator output
---

# Session Context: <session_id>

## Task

<task_description_from_argument_or_prompt>

## User Clarifications

| Question | Response |
|----------|----------|
| <question 1> | <user response> |
| <question 2> | <user response> |

*(If no clarifications were gathered, note: "No clarifications - using defaults")*

## Repository Context

| Property | Value |
|----------|-------|
| Repo | <repo_name> |
| Branch | <current_branch> |
| Commit | <current_commit> |
| Context | <root/microservice> |

## Detected Microservices (if root)

| Name | Path | Status |
|------|------|--------|
| service_name | ./service_name | detected |
| ... | ... | ... |

## Related Knowledge (from vault scan)

### Related Sessions

| Session | Date | Task | Relevance |
|---------|------|------|-----------|
| <session_id> | <date> | <task> | <high/medium/low> |

*"None found" if no related sessions*

### Conventions Loaded

- [ ] `knowledge/conventions/main.md` - <status: loaded/not found>

Key conventions for this task:
- <convention 1>
- <convention 2>

*"Conventions not found - will extract during research" if missing*

### Relevant Patterns

| Pattern | Path | Applicability |
|---------|------|---------------|
| <name> | knowledge/patterns/<name>.md | <how it applies> |

*"No patterns found" if none*

## Relevant Files (from quick scan)

| File | Relevance | Notes |
|------|-----------|-------|
| `path/to/file.py` | High | <brief note> |
| `path/to/another.py` | Medium | <brief note> |

*Top 10 files only - deep analysis in research phase*

## Recommended Research Tier

| Tier | Reason |
|------|--------|
| **<micro\|focused\|full>** | <reason from heuristic> |

**Override:** Use `/rpiv_research --micro`, `--focused`, or `--full` to override.

**Heuristic inputs:**
- Relevant files: <N>
- Directories touched: <N>
- Task type: <bug_fix|simple_change|feature|refactor|architectural>
- Conventions exist: <yes|no>

## Working Directory

<current_working_directory_relative_to_repo_root>

## Environment

| Variable | Value |
|----------|-------|
| VAULT_BASE | <vault_base> |
| Session Path | <full_session_path> |

## Session Goals

- [ ] Research: Gather context and understand requirements
- [ ] Plan: Create implementation plan
- [ ] Implement: Execute changes
- [ ] Validate: Verify implementation

## Notes

<Any additional notes from user or context scan>
```

### Step 6: Write index.md

```markdown
---
repo: <repo_name>
scope: <root|microservice>
session: <session_id>
type: index
created: <iso8601>
updated: <iso8601>
---

# Session Index: <session_id>

## Task

<task_description>

## Progress

| Phase | Status | Artifact | Updated |
|-------|--------|----------|---------|
| Context | complete | [00_context.md](./00_context.md) | <timestamp> |
| Research | pending | - | - |
| Plan | pending | - | - |
| Implement | pending | - | - |
| Validate | pending | - | - |

## Artifacts

- [00_context.md](./00_context.md) - Session context snapshot

## Timeline

| Time | Event |
|------|-------|
| <timestamp> | Session started |

## Notes

<additional_notes_will_be_appended_here>
```

### Step 7: Determine Next Step

Based on context gathered:

```
IF open questions identified OR task seems ambiguous:
    SUGGEST: /rpiv_discuss --topic "scope"
    REASON: "I have some questions that would help focus the research."

ELSE IF rich context found (conventions, patterns, related sessions):
    SUGGEST: /rpiv_research
    REASON: "Good context gathered - ready for deep research."

ELSE:
    SUGGEST: /rpiv_research
    REASON: "Standard path - research will gather more context."
```

### Step 8: Report

```
## RPIV Session Started

Created/Updated:
- $VAULT_BASE/<repo_name>/sessions/<session_id>/00_context.md
- $VAULT_BASE/<repo_name>/sessions/<session_id>/index.md

Session ID: <session_id>
Context: <root|microservice>
Task: <task_description>

### Context Scan Results
- Related sessions: <N found>
- Conventions: <loaded|not found>
- Patterns: <N found>
- Relevant files: <N identified>

### Recommended Research Tier
**<micro|focused|full>** - <reason>

| Tier | When to Use |
|------|-------------|
| micro | Bug fixes, <3 files, clear scope |
| focused | Single component, 3-10 files |
| full | Multi-component, architectural |

*Override with: `/rpiv_research --micro`, `--focused`, or `--full`*

### User Clarifications
- <clarification 1>
- <clarification 2>
*(or "None gathered" if --minimal or no questions asked)*

Next: /rpiv_research (will use <recommended_tier> tier)
```

