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

### Step 1: Load Context & Determine Tier

1. Find active session, read `00_context.md` for task, context type, relevant files, recommended tier
2. Determine tier: explicit flag (`--micro/--focused/--full`) → recommended from context → `full` (default)
3. If using recommended tier, inform user with override instructions
4. If `00_context.md` has "Relevant Files" entries, skip codebase-locator (inform user)

### Step 2: Execute Research by Tier

#### Micro (No Agents)
Direct synthesis only — NO agent spawning.
1. Read `00_context.md`, referenced patterns/conventions
2. If `--focus` provided, Grep for specific references
3. Synthesize into research artifact

**Output budget**: 100-200 lines

#### Focused (Single Agent)
Spawn `codebase-analyzer` on specific paths from context:
- Prompt: task description + relevant files + focus area
- Request: implementation details, dependencies, patterns used
- Also spawn convention-extractor if conventions not found

**Output budget**: 200-300 lines

#### Full (All Agents)

**Root repo agents** (parallel):
1. `microservice-distiller` per detected microservice → `knowledge/microservices/<name>.md`
2. `codebase-locator` (skip if files already in context)
3. `codebase-pattern-finder` → pattern catalog

**Inside microservice agents** (parallel):
1. `repo-doc-distiller` → `knowledge/services/<repo_name>.md`
2. `codebase-analyzer` → implementation analysis
3. `codebase-pattern-finder` → reusable templates

**Always**: `convention-extractor` if `conventions/main.md` doesn't exist

### Step 3: Synthesize Findings

Wait for all agents. Read outputs. Synthesize into research digest:
- Key findings (max 50 lines), file references (paths only), patterns, risks, open questions

### Step 4: Write Research Artifact

Version: find existing `1?_research.md`, increment (start at `10`). Write via `obsidian` MCP.

**Frontmatter**: `repo`, `scope`, `session`, `type: research`, `tier`, `created`, `updated`, `sources`.

**Body structure:**

```markdown
# Research: <task_description>

**Research Tier:** <tier> *(override with --micro/--focused/--full)*

## Summary
[3-5 sentences]

## Context Analysis

### Repository Structure
- Type, key directories with purposes

### Related Components
| Component | Path | Relevance |

### Existing Patterns
| Pattern | Location | Applicability |

## Microservice Analysis (if root repo)
| Microservice | Doc Path | Integration Points |

## Conventions to Follow
Reference: `knowledge/conventions/main.md`
Key conventions for this task: <list>

## Risks and Concerns
| Risk | Impact | Mitigation |

## Open Questions
- [ ] <questions needing clarification>

## Knowledge Artifacts Created/Updated
- <vault_path> - <description>

## Recommended Next Steps
1. <specific steps>
```

### Step 5: Update Session Index

Follow standard index update protocol:
- **Progress table**: Update "Research | pending" row (first time) or add iteration row ("Research (deep dive)")
- **Artifacts section**: Append new artifact link
- **Timeline**: Append timestamped entry

### Step 6: Determine Next Step

- Open questions or high-risk items → Suggest `/rpiv:discuss --topic "approach"`
- Otherwise → Suggest `/rpiv:plan`

### Step 7: Report

```
## RPIV Research Complete

Research Tier: <tier>

Created/Updated:
- <vault_paths>

Key Findings:
- <finding 1-3>

Open Questions: N | Risks Identified: N

Next: <suggested command with reasoning>
*(To re-run with more depth: /rpiv:research --full)*
```
