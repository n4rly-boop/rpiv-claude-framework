---
description: RPIV Research phase - gather context using distiller agents, write research artifact to vault
model: opus
---

# RPIV Research Phase

Conduct research for an RPIV session using distiller agents. Produces compressed context, not raw dumps.

## Research Tiers

| Tier | When to Use | Agents |
|------|-------------|--------|
| **Micro** | Bug fix, clear scope, <3 files | None (synthesis only) |
| **Focused** | Single component, 3-10 files | codebase-analyzer only |
| **Full** | Multi-component, architectural | All distillers |

## Process

### Step 1: Load Session Context & Determine Tier

1. **Find active session**:
   - Read most recent session from `$VAULT_BASE/<repo_name>/sessions/`
   - Or use `--session` argument if provided

2. **Read 00_context.md** to understand:
   - Task description
   - Context type (root/microservice)
   - Repo information
   - **Recommended research tier** (if present)
   - **Relevant files count** (for auto-detection)

3. **Determine research tier**:
   ```
   IF explicit flag (--micro, --focused, --full):
       tier = flag value
   ELSE IF 00_context.md has "recommended_research_tier":
       tier = recommended value
       INFORM user: "Using recommended tier: <tier> (override with --micro/--focused/--full)"
   ELSE:
       tier = "full"  # safe default
   ```

### Step 1.5: Check Existing File Discovery

```
IF 00_context.md "Relevant Files" section has entries:
    relevant_files = files from context
    SKIP codebase-locator agent in Full tier
    INFORM: "Using <N> files from session context (skip re-discovery)"
ELSE:
    PROCEED with codebase-locator as normal
```

### Step 2: Execute Research by Tier

**Branch based on tier:**

---

#### TIER: Micro (No Agents)

Skip all distillers. Synthesize directly from existing context.

```
1. Read 00_context.md thoroughly
2. Read any patterns/conventions referenced in context
3. If --focus provided, use Grep to find specific references
4. Synthesize findings into research artifact

NO AGENT SPAWNING - direct synthesis only
```

**Output budget**: 100-200 lines (lighter artifact)

---

#### TIER: Focused (Single Agent)

Spawn only `codebase-analyzer` on specific paths from context.

```
Agent: codebase-analyzer
Prompt: "Analyze these specific files for task: <task_description>
        Files: <relevant_files_from_context>
        Focus: <--focus value if provided>
        Return: Implementation details, dependencies, patterns used"
```

**If conventions not found**: Also spawn convention-extractor (one-time cost)

**Output budget**: 200-300 lines

---

#### TIER: Full (All Agents)

Spawn all distillers as documented below.

### Step 2-Full: Spawn Distiller Agents (Parallel)

**Only for --full tier.** Based on context type, spawn appropriate distillers:

**If in ROOT repo:**

```
Agent 1: microservice-distiller (per detected microservice)
- Document each nested repo as black-box
- Output to: $VAULT_BASE/<repo_name>/knowledge/microservices/<name>.md

Agent 2: codebase-locator (if not already discovered in context)
- SKIP if Step 1.5 found relevant files in 00_context.md
- Find relevant files for the task
- Return file map organized by category

Agent 3: codebase-pattern-finder
- Find similar implementations
- Return pattern catalog with examples
```

**If INSIDE microservice:**

```
Agent 1: repo-doc-distiller
- Comprehensive internal documentation
- Output to: $VAULT_BASE/<repo_name>/knowledge/services/<repo_name>.md

Agent 2: codebase-analyzer
- Analyze specific components related to task
- Return implementation analysis

Agent 3: codebase-pattern-finder
- Find patterns for the task
- Return reusable templates
```

**Always spawn:**

```
Agent 4: convention-extractor (via extract_conventions logic)
- If conventions.md doesn't exist, extract conventions
- Update: $VAULT_BASE/<repo_name>/knowledge/conventions/main.md
```

### Step 3: Synthesize Findings

Wait for ALL agents to complete. Then:

1. **Read all agent outputs** (they wrote to vault)
2. **Synthesize into research digest**:
   - Key findings (max 50 lines)
   - File references (paths only)
   - Patterns identified
   - Risks or concerns
   - Open questions

### Step 4: Determine Next Artifact Version

```bash
# Find existing research artifacts and get next version
# Pattern: 1X_research.md where X is iteration (0-9)
EXISTING=$(ls -1 $SESSION_PATH/1?_research.md 2>/dev/null | sort -V | tail -1)
if [ -z "$EXISTING" ]; then
    NEXT_VERSION="10_research.md"
else
    # Extract current number, increment
    CURRENT_NUM=$(basename "$EXISTING" | grep -o '^[0-9]*')
    NEXT_NUM=$((CURRENT_NUM + 1))
    NEXT_VERSION="${NEXT_NUM}_research.md"
fi
```

### Step 5: Write Research Artifact

Use `obsidian` MCP to write `$NEXT_VERSION`:

```markdown
---
repo: <repo_name>
scope: <root|microservice>
session: <session_id>
type: research
tier: <micro|focused|full>
created: <iso8601>
updated: <iso8601>
sources:
  - Agent outputs (if tier=focused or full)
  - <list_of_paths_examined>
---

# Research: <task_description>

**Research Tier:** <micro|focused|full> *(override with --micro/--focused/--full)*

## Summary

[3-5 sentences: what was learned, key insights]

## Context Analysis

### Repository Structure
- Type: <root monorepo|microservice>
- Key directories: <list with purposes>

### Related Components
| Component | Path | Relevance |
|-----------|------|-----------|
| <name> | <path> | <why relevant> |

### Existing Patterns
| Pattern | Location | Applicability |
|---------|----------|---------------|
| <name> | <file:line> | <how it applies> |

## Microservice Analysis (if root repo)

| Microservice | Doc Path | Integration Points |
|--------------|----------|-------------------|
| <name> | <vault_path> | <how it connects> |

## Conventions to Follow

Reference: `$VAULT_BASE/<repo_name>/knowledge/conventions/main.md`

Key conventions for this task:
- <convention 1>
- <convention 2>

## Risks and Concerns

| Risk | Impact | Mitigation |
|------|--------|------------|
| <risk> | High/Med/Low | <approach> |

## Open Questions

- [ ] <question needing clarification>
- [ ] <decision point for planning>

## Knowledge Artifacts Created/Updated

- `<vault_path_1>` - <description>
- `<vault_path_2>` - <description>

## Recommended Next Steps

1. <specific next step>
2. <specific next step>
```

### Step 6: Update Session Index

**CRITICAL: The index MUST track ALL artifacts. Follow this logic precisely:**

#### 6.1: Update Progress Table

**Determine if this is first research or an iteration:**

```
IF $NEXT_VERSION == "10_research.md":
    # First research - UPDATE the existing "Research | pending" row:
    REPLACE: | Research | pending | - | - |
    WITH:    | Research | complete | [10_research.md](./10_research.md) | <timestamp> |

ELSE (iteration - 11, 12, 13...):
    # Iteration - ADD a new row AFTER the last Research-related row:
    ITERATION_NUM = $NEXT_VERSION[1]  # second digit (11 -> 1, 12 -> 2)
    ITERATION_LABEL = "Research (deep dive)" if ITERATION_NUM == 1 else "Research (iteration $ITERATION_NUM)"

    ADD NEW ROW after last Research row:
    | $ITERATION_LABEL | complete | [$NEXT_VERSION](./$NEXT_VERSION) | <timestamp> |
```

**Example Progress table after iterations:**
```markdown
| Research | complete | [10_research.md](./10_research.md) | 2026-01-13T11:20:00Z |
| Research (deep dive) | complete | [11_research.md](./11_research.md) | 2026-01-13T14:00:00Z |
```

#### 6.2: Update Artifacts Section

**ALWAYS append new artifact to the Artifacts list:**
```markdown
- [10_research.md](./10_research.md) - Research findings
- [11_research.md](./11_research.md) - Deep dive research   <-- ADD
```

#### 6.3: Update Timeline

**ALWAYS append new entry at the END of the Timeline table:**
```markdown
| <timestamp> | Research completed ($NEXT_VERSION) |
```

### Step 7: Determine Next Step

Based on research findings:

```
IF "Open Questions" section has items:
    SUGGEST: /rpiv_discuss --topic "approach"
    REASON: "Research identified <N> open questions that should be
             discussed before planning."

ELSE IF high-risk items identified:
    SUGGEST: /rpiv_discuss --topic "approach"
    REASON: "Research identified high-risk items. Recommend discussing
             approach before planning."

ELSE:
    SUGGEST: /rpiv_plan
    REASON: "Research complete with no blocking questions."
```

### Step 8: Report

```
## RPIV Research Complete

Research Tier: <micro|focused|full>

Created/Updated:
- $VAULT_BASE/<repo_name>/sessions/<session_id>/$NEXT_VERSION
- $VAULT_BASE/<repo_name>/knowledge/microservices/*.md (if root, full tier only)
- $VAULT_BASE/<repo_name>/knowledge/conventions/main.md (if extracted)

Key Findings:
- <finding 1>
- <finding 2>
- <finding 3>

Open Questions: <N>
Risks Identified: <N>

Next: <suggested command with reasoning>

*(To re-run with more depth: /rpiv_research --full)*
```

