---
description: Validate and fix vault structure, naming, links, and frontmatter. Safe audit by default, interactive fixes with --fix flag.
model: sonnet
---

# Vault Maintenance

Validate and repair Obsidian vault structure for RPIV framework.

## Process

### Step 1: Determine Vault Path

Repo: `basename $(git rev-parse --show-toplevel)`. Vault: `$VAULT_BASE/$REPO_NAME`. Report mode: audit|check|fix.

### Step 2: Validate Structure

**Required dirs**: `sessions/`, `knowledge/`, `knowledge/microservices/`, `knowledge/services/`, `knowledge/conventions/`, `knowledge/patterns/`.
**Optional dirs**: `handoffs/`, `research/`.

Missing required → `CRITICAL | MISSING_DIR`.

### Step 3: Validate Sessions

For each session in `sessions/`:

**3.1 Name**: Must match `^\d{8}-\d{6}-[a-z0-9-]+$` → else `WARNING | INVALID_SESSION_NAME`

**3.2 Artifacts**: Valid patterns:

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

Non-matching → `WARNING | INVALID_ARTIFACT_NAME`

**3.3 Frontmatter**: Required fields: `repo` (match current), `scope`, `session` (match folder), `type`, `created`, `updated`. Missing frontmatter → `CRITICAL`. Missing/stale fields → `WARNING`.

**3.4 Index consistency**: All artifacts linked, all links exist, status matches reality. Issues: `MISSING_ARTIFACT_LINK`, `DEAD_ARTIFACT_LINK`, `STALE_STATUS`.

### Step 4: Validate Knowledge (skip if --check)

Check naming (`^[a-z0-9-]+\.md$`), index.md presence, frontmatter.

### Step 5: Validate Links (skip if --check)

Extract relative links, resolve targets, check existence. → `BROKEN_LINK` or `ABSOLUTE_LINK`.

### Step 6: Health Score

Base 100. CRITICAL: -20, WARNING: -5, INFO: -1. Min: 0.

### Step 7: Generate Report

Summary table (severity × count), health score, critical issues table, warnings table (max 20), recommended actions.

### Step 8: Fix Mode (if --fix)

For each issue (CRITICAL first), present fix proposal via `AskUserQuestion`: "Yes" / "No, skip" / "Skip all remaining".

| Issue | Fix |
|-------|-----|
| MISSING_DIR | Write empty index.md to create dir |
| MISSING_FRONTMATTER | Add template |
| MISSING/STALE_FIELD | Add/update field |
| MISSING_ARTIFACT_LINK | Append to index |
| DEAD_ARTIFACT_LINK | Ask: remove or update? |
| INVALID_NAME | Ask: rename? |
| BROKEN_LINK | Ask: remove or update? |

**Never auto-apply**: deletions, content modifications (beyond frontmatter), renames.

### Step 9: Final Report

Changes applied table, before/after issue counts, health score change. Without `--fix`, never modify anything.
