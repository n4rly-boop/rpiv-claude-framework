---
description: Generate comprehensive PR description from local git changes (no external services)
---

# Generate PR Description

Analyze local commits and changes to produce a PR description.

## Process

1. **Determine scope**:
   ```bash
   git log --oneline main..HEAD
   git diff --stat main..HEAD
   git diff main..HEAD
   ```

2. **Analyze changes thoroughly**: Read the full diff, read modified files for context, identify user-facing vs internal changes, find breaking changes.

3. **Check for template** in vault at `{repo_name}/templates/pr_description.md` via obsidian MCP. Use it if found, otherwise use default structure.

4. **Generate description**:
   - Summary (1-3 bullet points)
   - What changed and why
   - Breaking changes (if any)
   - Test plan

5. **Present to user** for review. Make requested changes.
