---
description: Create handoff document for transferring work to another session
---

# Create Handoff

Write a concise handoff document to transfer work context to another session. Goal: compact and summarize without losing key details.

## Process

### 1. Gather Metadata

Repo name: `basename $(git rev-parse --show-toplevel)`. File path: `{repo_name}/handoffs/YYYY-MM-DD_HH-MM-SS_description.md` (kebab-case description, 24h time).

### 2. Write Handoff

Write via `obsidian` MCP with this structure:

**Frontmatter**: date (ISO), git_commit, branch, repository, topic, tags, status, last_updated, type: implementation_strategy.

**Body sections:**
- **Task(s)**: Description + status (completed/WIP/planned). Reference plan/research documents if applicable. Note current phase.
- **Critical References**: 2-3 most important spec/design docs (file paths). Leave blank if none.
- **Recent Changes**: Code changes in `file:line` syntax.
- **Learnings**: Patterns, root causes, important context for the next agent. Include explicit file paths.
- **Artifacts**: Exhaustive list of produced/updated artifacts as file paths.
- **Action Items & Next Steps**: Prioritized list based on task statuses.
- **Other Notes**: Relevant codebase locations, documents, or other useful context.

### 3. Report

Respond to user:
```
Handoff created and synced! You can resume from this handoff in a new session with the following command:

/resume_handoff {repo_name}/handoffs/YYYY-MM-DD_HH-MM-SS_description.md
```
(Path relative to vault root)
