---
description: Create git commits with user approval and no Claude attribution
---

# Commit Changes

Create git commits for session changes. NEVER add co-author information, Claude attribution, or "Co-Authored-By" lines.

## Process

1. **Assess changes**: Review conversation history, run `git status` + `git diff`, determine if one or multiple logical commits
2. **Plan commits**: Group related files, draft clear imperative commit messages focusing on WHY. Match repo's existing commit message format. Ask user if unclear.
3. **Present plan**: List files per commit + messages. Ask: "I plan to create N commit(s). Shall I proceed?"
4. **Execute on confirmation**: `git add` specific files (never `-A` or `.`), create commits, show `git log --oneline -n N`
