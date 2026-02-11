---
description: Resume work from handoff document with context analysis and validation
---

# Resume Handoff

Resume work from a handoff document through interactive analysis and validation.

## Initial Response

Use `obsidian` MCP. Repo name: `basename $(git rev-parse --show-toplevel)`

**If path provided**: Read handoff FULLY, read linked research/plan documents directly (not via sub-agent), then analyze and propose course of action.

**If no path**: List `{repo_name}/handoffs/` contents and ask which to resume.

## Process

### Step 1: Read & Analyze Handoff

1. Read handoff completely. Extract: tasks + statuses, recent changes, learnings, artifacts, action items.
2. Spawn parallel research tasks to verify current state:
   - Read all artifacts mentioned in handoff (feature docs, plans, research)
   - Extract key requirements and decisions
3. Read critical files from "Learnings" and "Recent changes" sections

### Step 2: Present Analysis

```
**Original Tasks**: [task]: [handoff status] → [current verification]
**Key Learnings Validated**: [learning] - [still valid/changed]
**Recent Changes Status**: [change] - [verified/missing/modified]
**Artifacts Reviewed**: [doc]: [key takeaway]

**Recommended Next Actions** (from handoff + current state):
1. [most logical next step]
2. [second priority]

**Potential Issues**: [conflicts, regressions, missing deps]

Shall I proceed with [action 1], or adjust the approach?
```

Get user confirmation before proceeding.

### Step 3: Create Action Plan

Convert action items to TodoWrite task list. Prioritize by dependencies and handoff guidance. Present and confirm.

### Step 4: Begin Implementation

Start first approved task. Reference learnings throughout. Apply documented patterns. Update progress as tasks complete.
