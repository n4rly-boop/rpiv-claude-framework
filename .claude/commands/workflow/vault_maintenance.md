---
description: Validate and fix vault structure, naming, links, and frontmatter. Safe audit by default, interactive fixes with --fix flag.
model: sonnet
---

# Vault Maintenance

Validate and repair Obsidian vault structure for RPIV framework.

## Usage

```
/vault_maintenance                      # Full audit (dry-run)
/vault_maintenance --check              # Quick structure check
/vault_maintenance --fix                # Interactive fix mode
/vault_maintenance --session <id>       # Validate specific session
```

## Process

### Step 1: Determine Vault Path

```bash
REPO_NAME=$(basename $(git rev-parse --show-toplevel))
VAULT_BASE=${VAULT_BASE:-$HOME/context_vault}
VAULT_PATH="$VAULT_BASE/$REPO_NAME"
```

Report:
```
Vault Maintenance Starting
==========================
Repo: $REPO_NAME
Vault: $VAULT_PATH
Mode: <audit|check|fix>
```

### Step 2: Validate Structure

Use `obsidian` MCP to check directory structure:

**Required directories:**
- `sessions/`
- `knowledge/`
- `knowledge/microservices/`
- `knowledge/services/`
- `knowledge/conventions/`
- `knowledge/patterns/`

**Optional directories:**
- `handoffs/`
- `research/`

For each missing required directory, record issue:
```
CRITICAL | MISSING_DIR | <path> | Required directory missing
```

### Step 3: Validate Sessions

For each session folder in `sessions/`:

#### 3.1 Session Name Validation
Pattern: `^\d{8}-\d{6}-[a-z0-9-]+$`

If invalid:
```
WARNING | INVALID_SESSION_NAME | <session> | Doesn't match YYYYMMDD-HHMMSS-description pattern
```

#### 3.2 Artifact Validation

**Valid patterns:**
| Regex | Type |
|-------|------|
| `^00_context\.md$` | Context |
| `^D\d{2}_[a-z0-9-]+\.md$` | Discussion |
| `^1\d_research\.md$` | Research |
| `^2\d_plan\.md$` | Plan |
| `^3\d_implementation\.md$` | Implementation |
| `^4\d_validation\.md$` | Validation |
| `^50_session_summary\.md$` | Summary |
| `^index\.md$` | Index |

For non-matching files:
```
WARNING | INVALID_ARTIFACT_NAME | <session>/<file> | Doesn't match artifact patterns
```

#### 3.3 Frontmatter Validation

Read each artifact and check frontmatter:

**Required fields:**
- `repo` (must match current repo)
- `scope` (root|microservice|service)
- `session` (must match session folder)
- `type` (context|discussion|research|plan|implementation|validation|index)
- `created` (ISO8601)
- `updated` (ISO8601)

For missing frontmatter:
```
CRITICAL | MISSING_FRONTMATTER | <path> | No YAML frontmatter found
```

For missing fields:
```
WARNING | MISSING_FIELD | <path> | Missing: <field>
```

For mismatched values:
```
WARNING | STALE_FIELD | <path> | <field> is '<value>' but should be '<expected>'
```

#### 3.4 Index Consistency

Read `index.md` and check:
1. All artifacts in folder are linked
2. All linked artifacts exist
3. Status matches (pending vs exists)

Issues:
```
WARNING | MISSING_ARTIFACT_LINK | <session>/index.md | <artifact> not in index
WARNING | DEAD_ARTIFACT_LINK | <session>/index.md | Links to non-existent <artifact>
WARNING | STALE_STATUS | <session>/index.md | <artifact> status is 'pending' but file exists
```

### Step 4: Validate Knowledge (skip if --check)

For each subdirectory in `knowledge/`:

1. Check file naming: `^[a-z0-9-]+\.md$`
2. Check for index.md
3. Validate frontmatter

Issues:
```
INFO | INVALID_KNOWLEDGE_NAME | <path> | Name should be lowercase-with-hyphens.md
INFO | MISSING_INDEX | <path>/ | No index.md in directory
WARNING | MISSING_FRONTMATTER | <path> | No YAML frontmatter
```

### Step 5: Validate Links (skip if --check)

For each markdown file, extract links with pattern: `\[.*?\]\((\.{1,2}/[^)]+)\)`

For each relative link:
1. Resolve target path
2. Check if target exists

Issues:
```
WARNING | BROKEN_LINK | <file> | Link to <target> - file doesn't exist
INFO | ABSOLUTE_LINK | <file> | Uses absolute path, should be relative
```

### Step 6: Calculate Health Score

```
Base: 100 points
CRITICAL: -20 points each
WARNING: -5 points each
INFO: -1 point each

Minimum: 0
```

### Step 7: Generate Report

```markdown
## Vault Audit Report

**Vault**: $VAULT_PATH
**Date**: <iso8601>
**Mode**: <audit|check|fix>

### Summary

| Severity | Count |
|----------|-------|
| CRITICAL | N |
| WARNING | N |
| INFO | N |

**Health Score**: X/100

### Critical Issues

| Issue | Path | Description |
|-------|------|-------------|
<list all CRITICAL issues>

### Warnings

| Issue | Path | Description |
|-------|------|-------------|
<list all WARNING issues, max 20>

### Info

<count only, or list if --verbose>

### Recommended Actions

<prioritized list of fixes>
```

### Step 8: Fix Mode (if --fix)

For each issue in priority order (CRITICAL first):

```
## Fix: <ISSUE_TYPE>

**Path**: <path>
**Issue**: <description>
**Proposed Fix**: <what will be done>

Apply this fix?
```

Use `AskUserQuestion` with options:
- "Yes, apply this fix"
- "No, skip this fix"
- "Skip all remaining fixes"

**Fix implementations:**

| Issue | Fix |
|-------|-----|
| MISSING_DIR | `obsidian.write_note` to create directory (write empty index.md) |
| MISSING_FRONTMATTER | Add frontmatter template to file |
| MISSING_FIELD | Add field with inferred/default value |
| STALE_FIELD | Update field to correct value |
| MISSING_ARTIFACT_LINK | Append link to index.md Artifacts section |
| DEAD_ARTIFACT_LINK | Ask: remove link or update target? |
| INVALID_SESSION_NAME | Ask: rename folder? (use MCP move) |
| INVALID_ARTIFACT_NAME | Ask: rename file or ignore? |
| BROKEN_LINK | Ask: remove link or update target? |

**Never auto-apply:**
- File/folder deletions
- Content modifications (beyond frontmatter)
- Renames (always ask first)

### Step 9: Final Report

```markdown
## Vault Maintenance Complete

**Mode**: <mode>
**Duration**: <time>

### Changes Applied

| Action | Path | Result |
|--------|------|--------|
<list of changes made>

### Remaining Issues

| Severity | Before | After |
|----------|--------|-------|
| CRITICAL | N | N |
| WARNING | N | N |
| INFO | N | N |

**Health Score**: X/100 -> Y/100

<next steps if issues remain>
```

## Safety Rules

1. **Default is read-only** - Without `--fix`, never modify anything
2. **No deletions** - NEVER delete files or folders without explicit per-item approval
3. **No content changes** - Only modify YAML frontmatter, never body content
4. **Ask before rename** - Always confirm file/folder renames
5. **Atomic operations** - Each fix is independent, failure doesn't affect others
6. **Full logging** - Every change is reported

## Error Handling

**MCP unavailable:**
```
Error: Cannot access vault - Obsidian MCP not responding

Check:
1. MCP server is running
2. VAULT_BASE is set correctly: $VAULT_BASE
3. Vault exists at: $VAULT_PATH
```

**Vault not found:**
```
Warning: No vault found at $VAULT_PATH

Options:
- Initialize new vault structure for this repo
- Specify different path with --vault <path>
- Cancel
```

**Fix failed:**
```
Warning: Fix failed for <path>
Error: <mcp error>

Continuing with next fix...
```

## Output Format

Always end with:

```
Vault Maintenance Complete
==========================
Health Score: X/100
Issues: N critical, N warnings, N info
<recommendation>
```
