---
description: RPIV Discussion phase - facilitate decision-making and record outcomes to vault
model: opus
---

# RPIV Discussion Phase

Facilitate structured discussion and record decisions to vault. Focus on capturing WHY, not what.

## Process

### Step 1: Load Context

1. Find active session
2. Determine discussion context: `--after` flag → specified phase; else auto-detect from latest artifact (check 4X→3X→2X→1X→00)
3. Read: latest artifact from detected phase, `00_context.md`, any previous discussions (`DXX_*.md`)

### Step 2: Present Summary (max 20 lines)

```markdown
## Current State
**Task**: <from context> | **Phase**: <detected> | **Latest Artifact**: <name>

### Key Points from <Latest Artifact>
- <3 bullet points>

### Decision Points / Open Questions
- <from research/plan>
```

### Step 3: Facilitate Discussion

Use `AskUserQuestion` to:
1. Present options (if applicable): labeled approaches with 1-line descriptions
2. Ask clarifying questions: constraints, priorities, preferences
3. Confirm understanding: summarize decisions, check for gaps

### Step 4: Write Discussion Artifact

Version: find existing `D??_*.md`, increment (start at `D01`). Topic from `--topic` flag or auto-detect (after context→"scope", research→"approach", plan→"design", implement→"review", validation→"retrospective"). Write via `obsidian` MCP.

**Frontmatter**: `repo`, `session`, `type: discussion`, `topic`, `phase_after`, `created`, `sources`.

**Body structure:**

```markdown
# Discussion: <Topic Title>

## Context
**Task**: <description> | **Trigger**: <what prompted this> | **Preceding**: [<artifact>](./<artifact>)

## Summary
[2-3 sentences: what was discussed and decided]

## Options Considered
### Option A: <Name>
**Description**: [1-2 sentences]
**Pros**: <list> | **Cons**: <list>
**Effort**: Low/Med/High | **Risk**: Low/Med/High

### Option B/C: ...

## Decision
**Chosen**: <Option X>
**Reasoning**: <WHY — most valuable part. What trade-offs accepted?>

## Impact on Next Phase
- For Planning/Implementation/Validation: <specific constraints>

## Action Items
- [ ] <next steps>

## Open Items (Deferred)
- [ ] <things to revisit later>
```

**Budget**: 300-500 lines max.

### Step 5: Re-Research Check

If user requests deeper investigation during discussion:
- Suggest `/rpiv_research --focus "<topic>"`
- Note in artifact: "Research requested on <topic>"
- End discussion, suggest research command

### Step 6: Update Session Index

Follow standard index update protocol:
- **Progress table**: Add discussion row
- **Artifacts section**: Append new artifact link
- **Timeline**: Append timestamped entry with key decision

### Step 7: Report

```
## RPIV Discussion Complete

Created:
- <vault_path>

Key Decisions:
- <decisions>

Impact: <how this affects next phase>

Next: <suggested command>
  After scope → /rpiv_research
  After approach → /rpiv_plan
  After design → /rpiv_implement
  After retrospective → /rpiv_plan (new iteration)
```
