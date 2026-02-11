---
description: Generate comprehensive PR description from local git changes (no external services)
---

# Generate PR Description

Analyze local commits and changes to produce a PR description.

## Process

1. **Determine scope**: `git log --oneline main..HEAD`, `git diff --stat main..HEAD`, `git diff main..HEAD`
2. **Analyze thoroughly**: Read full diff + modified files for context. Identify user-facing vs internal changes, breaking changes.
3. **Check template**: Look for `{repo_name}/templates/pr_description.md` in vault via obsidian MCP. Use if found, otherwise default structure.
4. **Generate**: Summary (1-3 bullets), what changed and why, breaking changes (if any), test plan.
5. **Present** to user for review. Make requested changes.
