---
name: vault-maintenance
description: Validate and fix vault structure, file naming, links, and frontmatter. Use when vault structure becomes inconsistent after framework changes, or to audit vault health. Never deletes or modifies without explicit approval.
---

# Vault Maintenance Skill

Validate and repair Obsidian vault structure for RPIV framework. Identifies inconsistencies in file structure, naming conventions, internal links, and frontmatter. All fixes require explicit user approval.

## Usage

```
/vault-maintenance                      # Full audit (dry-run, report only)
/vault-maintenance --check              # Quick check (structure only, no link validation)
/vault-maintenance --fix                # Interactive fix mode (asks before each change)
/vault-maintenance --session <id>       # Validate specific session only
/vault-maintenance --repo <name>        # Validate specific repo vault
```

## Modes

### Dry-Run (Default)
Reports all issues found without making any changes. Safe to run anytime.

### Check (`--check`)
Quick structure validation only. Skips link validation and frontmatter analysis.

### Fix (`--fix`)
Interactive repair mode. For each issue found, presents:
- What the issue is
- What the fix would be
- Asks for explicit approval before applying

**NEVER** deletes files or modifies content without explicit user approval.

## Validation Rules

### 1. Directory Structure

**Required directories:**
```
$VAULT_BASE/<repo_name>/
├── sessions/           # Session artifacts (required)
├── knowledge/          # Persistent knowledge (required)
│   ├── microservices/  # Black-box service docs
│   ├── services/       # Internal service docs
│   ├── conventions/    # Code conventions
│   └── patterns/       # Implementation patterns
├── handoffs/           # Session handoffs (optional)
└── research/           # Ad-hoc research (optional)
```

**Issues detected:**
- MISSING_DIR: Required directory doesn't exist
- EXTRA_DIR: Unexpected directory in vault root
- WRONG_LOCATION: File in wrong directory

### 2. Session Naming Convention

**Session folder format:** `YYYYMMDD-HHMMSS-description`
- Date: 8 digits
- Time: 6 digits
- Description: lowercase, hyphens only

**Regex:** `^\d{8}-\d{6}-[a-z0-9-]+$`

**Issues detected:**
- INVALID_SESSION_NAME: Session folder doesn't match pattern
- ORPHAN_SESSION: Session folder with no index.md

### 3. Artifact Naming (Decade-Based Versioning)

**Session artifacts:**
| Pattern | Type | Example |
|---------|------|---------|
| `00_context.md` | Context | `00_context.md` (never versioned) |
| `D\d{2}_*.md` | Discussion | `D01_scope.md`, `D02_approach.md` |
| `1\d_research.md` | Research | `10_research.md`, `11_research.md` |
| `2\d_plan.md` | Plan | `20_plan.md`, `21_plan.md` |
| `3\d_implementation.md` | Implementation | `30_implementation.md` |
| `4\d_validation.md` | Validation | `40_validation.md`, `41_validation.md` |
| `50_session_summary.md` | Summary | `50_session_summary.md` |
| `index.md` | Index | Always `index.md` |

**Issues detected:**
- INVALID_ARTIFACT_NAME: File doesn't match expected patterns
- WRONG_SEQUENCE: Artifact skips version numbers (e.g., 40 then 42)
- DUPLICATE_ARTIFACT: Same version exists twice

### 4. Knowledge File Naming

**Knowledge files:**
- Lowercase, hyphens only
- Must have `.md` extension
- No spaces or special characters

**Regex:** `^[a-z0-9-]+\.md$`

**Issues detected:**
- INVALID_KNOWLEDGE_NAME: File doesn't match naming convention
- MISSING_INDEX: Directory missing index.md

### 5. YAML Frontmatter

**Required fields for all artifacts:**
```yaml
---
repo: <repo_name>
scope: root|microservice|service
session: <session_id>  # For session artifacts
type: <artifact_type>
created: <iso8601>
updated: <iso8601>
---
```

**Discussion artifacts additional fields:**
```yaml
topic: scope|approach|design|review|retrospective
phase_after: context|research|plan|implement|validate
```

**Issues detected:**
- MISSING_FRONTMATTER: No YAML frontmatter found
- MISSING_FIELD: Required field missing
- INVALID_FIELD: Field has invalid value
- STALE_FIELD: Field doesn't match current location (e.g., wrong repo name)

### 6. Internal Links

**Link format:** `[text](./relative/path.md)` or `[text](../path.md)`

**Issues detected:**
- BROKEN_LINK: Link target doesn't exist
- ABSOLUTE_LINK: Uses absolute path instead of relative
- WRONG_EXTENSION: Links to non-markdown file incorrectly

### 7. Index Consistency

**Session index.md must track:**
- All artifacts in the session folder
- Correct artifact links
- Consistent status (pending/complete)

**Issues detected:**
- MISSING_ARTIFACT_LINK: Artifact exists but not in index
- DEAD_ARTIFACT_LINK: Index links to non-existent artifact
- STALE_STATUS: Status doesn't match artifact existence

## Process

### Step 1: Determine Vault Location

```bash
REPO_NAME=$(basename $(git rev-parse --show-toplevel))
VAULT_BASE=${VAULT_BASE:-$HOME/context_vault}
VAULT_PATH="$VAULT_BASE/$REPO_NAME"
```

If `--repo` specified, use that instead of auto-detection.

### Step 2: Structure Validation

Use `obsidian` MCP to list directories:

```
1. List vault root: obsidian.list_directory(path="<repo_name>")
2. Check required directories exist:
   - sessions/
   - knowledge/
   - knowledge/microservices/
   - knowledge/services/
   - knowledge/conventions/
   - knowledge/patterns/
3. Flag unexpected items in root
```

### Step 3: Session Validation

For each session in `sessions/`:

```
1. Validate session folder name against pattern
2. List session contents
3. Validate each artifact:
   - Name matches expected pattern
   - Frontmatter is valid
   - Links are valid (unless --check)
4. Check index.md completeness
```

If `--session` specified, only validate that session.

### Step 4: Knowledge Validation

For each directory in `knowledge/`:

```
1. List files in directory
2. Validate file naming
3. Check for index.md
4. Validate frontmatter
5. Check internal links (unless --check)
```

### Step 5: Collect Issues

Group issues by severity:

**CRITICAL (blocks workflow):**
- Missing required directories
- Invalid session folder names
- Missing frontmatter
- Broken index links

**WARNING (should fix):**
- Missing optional frontmatter fields
- Stale field values
- Wrong file locations
- Broken internal links

**INFO (suggestions):**
- Missing index.md in knowledge subdirs
- Outdated timestamps
- Non-standard file names

### Step 6: Report Issues

```markdown
## Vault Audit Report

**Vault**: $VAULT_PATH
**Date**: <iso8601>
**Mode**: <dry-run|check|fix>

### Summary

| Severity | Count |
|----------|-------|
| CRITICAL | N |
| WARNING | N |
| INFO | N |

### Issues by Category

#### Structure Issues (N)

| Severity | Issue | Path | Description |
|----------|-------|------|-------------|
| CRITICAL | MISSING_DIR | knowledge/conventions/ | Required directory missing |

#### Session Issues (N)

| Severity | Issue | Session | File | Description |
|----------|-------|---------|------|-------------|
| WARNING | INVALID_ARTIFACT_NAME | 20260101-120000-test | foo.md | Doesn't match artifact pattern |

#### Frontmatter Issues (N)

| Severity | Issue | File | Field | Description |
|----------|-------|------|-------|-------------|
| WARNING | MISSING_FIELD | sessions/.../10_research.md | scope | Required field missing |

#### Link Issues (N)

| Severity | Issue | File | Link | Description |
|----------|-------|------|------|-------------|
| WARNING | BROKEN_LINK | sessions/.../index.md | ./20_plan.md | Target doesn't exist |

### Recommended Actions

1. <action 1>
2. <action 2>
```

### Step 7: Fix Mode (if --fix)

For each issue, present fix and ask approval:

```
## Fix Required: MISSING_DIR

**Issue**: Required directory `knowledge/conventions/` doesn't exist
**Fix**: Create directory `knowledge/conventions/`

Apply this fix?
- Yes, create the directory
- No, skip this fix
- Skip all remaining fixes
```

Use `AskUserQuestion` for each fix.

**Fix actions by issue type:**

| Issue | Fix Action |
|-------|------------|
| MISSING_DIR | Create directory via MCP |
| INVALID_SESSION_NAME | Suggest rename, move via MCP |
| WRONG_LOCATION | Move file to correct location via MCP |
| MISSING_FRONTMATTER | Add frontmatter template |
| MISSING_FIELD | Add field with default/inferred value |
| STALE_FIELD | Update field to match current state |
| MISSING_ARTIFACT_LINK | Add link to index |
| DEAD_ARTIFACT_LINK | Remove or update link in index |

**NEVER perform these without asking:**
- Delete any file or directory
- Modify file content beyond frontmatter
- Rename files (always ask first)
- Move files between sessions

### Step 8: Apply Fixes

For each approved fix:

```
1. Execute fix via obsidian MCP
2. Log change
3. Verify fix succeeded
```

### Step 9: Final Report

```markdown
## Vault Maintenance Complete

**Mode**: <dry-run|check|fix>
**Duration**: <time>

### Changes Applied (if --fix)

| Action | Path | Result |
|--------|------|--------|
| CREATE_DIR | knowledge/conventions/ | SUCCESS |
| MOVE_FILE | sessions/.../foo.md -> bar.md | SUCCESS |

### Remaining Issues

| Severity | Count | Note |
|----------|-------|------|
| CRITICAL | N | <note if any remain> |
| WARNING | N | |
| INFO | N | |

### Health Score

**Before**: X/100
**After**: Y/100 (if --fix)

Scoring:
- Base: 100 points
- CRITICAL: -20 points each
- WARNING: -5 points each
- INFO: -1 point each

Next: <suggested action if issues remain>
```

## Error Handling

**If MCP unavailable:**
```
Error: Obsidian MCP not available

Cannot access vault. Ensure:
1. Obsidian MCP server is running
2. VAULT_BASE is correctly configured
3. Vault exists at: $VAULT_PATH

Run with --debug for more details.
```

**If vault doesn't exist:**
```
Warning: Vault not found at $VAULT_PATH

This appears to be a new repo. Would you like to:
- Initialize vault structure for this repo
- Specify a different vault path
- Cancel
```

**If fix fails:**
```
Error: Failed to apply fix

Action: CREATE_DIR knowledge/conventions/
Error: <mcp error message>

Continuing with next fix...
```

## Examples

### Example 1: Quick Health Check

```
> /vault-maintenance --check

## Vault Audit Report (Quick Check)

**Vault**: /Users/user/context_vault/my-project
**Mode**: check (structure only)

### Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| WARNING | 2 |
| INFO | 3 |

### Issues

1. [WARNING] MISSING_DIR: knowledge/patterns/ doesn't exist
2. [WARNING] INVALID_SESSION_NAME: sessions/test-session/ doesn't match pattern
3. [INFO] MISSING_INDEX: knowledge/conventions/ has no index.md
4. [INFO] MISSING_INDEX: knowledge/services/ has no index.md
5. [INFO] OUTDATED_TIMESTAMP: sessions/20260101-120000-auth/index.md hasn't been updated in 30 days

### Health Score: 85/100

Run `/vault-maintenance --fix` to repair issues interactively.
```

### Example 2: Interactive Fix

```
> /vault-maintenance --fix

## Vault Audit Complete - Starting Fix Mode

Found 3 issues to address.

---

### Fix 1/3: MISSING_DIR

**Issue**: Required directory `knowledge/patterns/` doesn't exist
**Fix**: Create directory via MCP

[User selects: "Yes, create the directory"]

Created: knowledge/patterns/

---

### Fix 2/3: INVALID_SESSION_NAME

**Issue**: Session folder `test-session` doesn't match naming pattern
**Current**: sessions/test-session/
**Suggested**: sessions/20260115-000000-test-session/

Note: Timestamp will use earliest artifact creation date if available.

[User selects: "No, skip this fix"]

Skipped.

---

### Fix 3/3: MISSING_INDEX

**Issue**: Directory `knowledge/conventions/` has no index.md
**Fix**: Create index.md with template

[User selects: "Yes, create index"]

Created: knowledge/conventions/index.md

---

## Fix Summary

| Action | Path | Result |
|--------|------|--------|
| CREATE_DIR | knowledge/patterns/ | SUCCESS |
| RENAME | sessions/test-session/ | SKIPPED |
| CREATE_FILE | knowledge/conventions/index.md | SUCCESS |

**Health Score**: 85/100 -> 92/100
```

## Safety Guarantees

1. **No automatic deletion** - Will NEVER delete files without explicit approval per file
2. **No content modification** - Only modifies YAML frontmatter, never file body
3. **No silent changes** - Every change is logged and reported
4. **Reversible operations** - Moves are tracked, can be undone
5. **Dry-run default** - Must explicitly request --fix mode
6. **Per-fix approval** - Each fix requires separate approval in --fix mode

## Best Practices

- Run `/vault-maintenance` before starting new sessions to ensure clean state
- Run `/vault-maintenance --check` after framework updates to detect incompatibilities
- Run `/vault-maintenance --fix` periodically to maintain vault health
- Review the health score trend over time

## Troubleshooting

**"Vault not found"**
- Check VAULT_BASE environment variable
- Ensure vault directory exists
- Verify MCP server has read access

**"Many broken links"**
- Common after renaming artifacts
- Use --fix mode to update links interactively
- Check if session was created with older framework version

**"Invalid session names"**
- Older sessions may use different naming
- Choose to rename or keep legacy names
- New sessions will use correct format
