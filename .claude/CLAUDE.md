# Claude Code Workspace Contract

Non-negotiable rules for Claude agents in this repository.

## Core Principles

1. **Artifacts Are Authoritative** - All persistent knowledge MUST go to the Obsidian vault. Chat is ephemeral.
2. **MCP-Only Artifacts** - Write via `obsidian` MCP server. NEVER create `.claude/artifacts` or use symlinks.
3. **Context Compression** - Use distiller agents (200-400 lines max). Return vault path + summary (max 10 lines).
4. **File Pointers Over Code Dumps** - Reference as `path/to/file.py:line_number`. No large code in chat.

## Artifact Layout

```
$VAULT_BASE/<repo_name>/sessions/<session_id>/
├── 00_context.md         # Initial context (never versioned)
├── DXX_<topic>.md        # Discussions (D01, D02, D03...)
├── 1X_research.md        # Research (10, 11, 12...)
├── 2X_plan.md            # Plans (20, 21, 22...)
├── 3X_implementation.md  # Implementation (30, 31, 32...)
├── 4X_validation.md      # Validation (40, 41, 42...)
├── 50_session_summary.md # Final summary
└── index.md              # Session index

$VAULT_BASE/<repo_name>/knowledge/
├── microservices/<name>.md   # Black-box docs (external view)
├── services/<name>.md        # Internal service docs
├── conventions/<name>.md     # Code conventions
└── patterns/<name>.md        # Implementation patterns
```

### Versioning Rules
- Artifacts are **NEVER overwritten** between iterations
- Pattern: `<decade><iteration>_<type>.md` (decade: 1=research, 2=plan, 3=impl, 4=valid)
- Find latest: `ls -1 session_path/2?_plan.md | sort -V | tail -1`
- Write new: check existing prefix, increment (if `20_plan.md` exists → write `21_plan.md`)

### Frontmatter Template
```yaml
---
repo: <repo_name>
scope: root|microservice|service
session: <session_id_or_null>
type: context|discussion|research|plan|implementation|validation|doc|index
created: <iso8601>
updated: <iso8601>
sources: [<paths_or_commands>]
---
```
Discussion artifacts add: `topic: scope|approach|design|review|retrospective`

## RPIV Workflow

**Flow:** Start → [Discuss] → Research → [Discuss] → Plan → Implement → Validate → Summarize

| Phase | Command | Artifacts | Key Rules |
|-------|---------|-----------|-----------|
| Start | `/rpiv_start` | `00_context.md`, `index.md` | Scans vault + codebase, recommends research tier. `--minimal` skips scan |
| Discuss | `/rpiv_discuss` | `DXX_<topic>.md` | Optional. Record decisions (WHY not what). 300-500 lines max |
| Research | `/rpiv_research` | `1X_research.md` | Tiered: `--micro` (5-10K), `--focused` (15-25K), `--full` (40-60K). Auto-detects from start |
| Plan | `/rpiv_plan` | `2X_plan.md` | Requires research (or `--no-research`). MUST include manual test plan |
| Implement | `/rpiv_implement` | `3X_implementation.md` | Requires plan artifact |
| Validate | `/rpiv_validate` | `4X_validation.md` | Two-pass system (see below). `--fast` skips Pass 2 |
| Summarize | `/session_summary` | `50_session_summary.md` | Verification playbook, future work, limitations |

### Tiered Research
| Tier | Tokens | When | Agents |
|------|--------|------|--------|
| `--micro` | 5-10K | Bug fix, ≤3 files, clear scope | None (synthesis only) |
| `--focused` | 15-25K | Single component, 3-10 files | codebase-analyzer only |
| `--full` | 40-60K | Multi-component, architectural | All distillers |

Auto-detected from `/rpiv_start` context. Override with explicit flag.

### Two-Pass Validation (Scoped)
- **Pass 1** (always): `/tooling check`, `/tooling test`, code-reviewer. Collects ALL issues.
- **Pass 2** (scoped, on critical issues): Selected agents on files with issues only.

| Change Type | Pass 2 Agents | Tokens |
|-------------|---------------|--------|
| Docs/config only | None (skip) | 0 |
| Localized fix (≤3 files) | defensive + logic | ~30K |
| API/schema change | integration + security | ~30K |
| Security-sensitive | security + defensive | ~30K |
| Multi-file feature | All 4 (on issue files) | ~40-60K |

Use `--full` to force all 4 agents on all files. Use `--fast` to skip Pass 2.

## Black Box Rule (Monorepo)

From root repo: nested git repos are black boxes. Document only external interfaces (APIs, ports, integration points).
Store in `knowledge/microservices/`. From inside microservice: document comprehensively in its own vault.

## Output Format

Every RPIV command ends with:
```
Created/Updated:
- <vault_path>

Next: <suggested_command>

<digest: max 10 lines>
```

## Prohibited Actions

1. Creating `.claude/artifacts` directory
2. Using symlinks for artifact storage
3. Pasting >50 lines of code in chat
4. `/rpiv_implement` without plan artifact
5. `/rpiv_plan` without research artifact (unless `--no-research`)
6. Distiller outputs >400 lines
7. Raw agent outputs without vault persistence
8. Running linters directly (`ruff`, `black`, `mypy`, `pytest`, `make check`) - use `/tooling` skill
9. Plans without manual testing steps
10. Skipping Pass 2 when critical issues exist (unless `--fast`)
11. Accessing `.env` files in ANY way

## Security: .env Protection

**.env files are OFF-LIMITS.** Enforced by `.claude/hooks/protect-env-files.py`.

**Blocked:** Read, cat, head, tail, grep, cp, tar, source - any access vector to `.env`, `.env.*`, `**/.env`

**If you need env vars:** Ask user, reference `.env.example`, or use documented defaults.

## Tooling Policy

Use `/tooling` skill for ALL code quality:
- `/tooling check` - lint, type check, format verify
- `/tooling test` - run tests
- `/tooling format` - auto-fix formatting

Auto-detects project type. Customize via `/extract_conventions`.

### Manual Testing in Plans
Every plan MUST include:
- Specific curl commands (copy-pasteable)
- Expected responses (status codes, JSON structure)
- Observable side effects (logs, DB changes)
- Negative test cases (invalid input, missing auth)

## Discovery Commands

```bash
git rev-parse --show-toplevel                 # Repo root
basename $(git rev-parse --show-toplevel)     # Repo name
git submodule status                          # List submodules
find . -maxdepth 3 -name .git -type d         # Find nested repos
```

## MCP Reference

### Obsidian MCP (`@mauricio.wolff/mcp-obsidian`)
`read_note`, `write_note`, `delete_note`, `move_note`, `list_directory`, `read_multiple_notes`, `search_notes`, `get_frontmatter`, `update_frontmatter`, `get_notes_info`, `manage_tags`

Always use MCP for vault operations, never direct file writes.

### Context7 MCP (`mcp-context7`)
For external library docs: `resolve-library-id` → `query-docs`

Use for unfamiliar libraries (FastAPI, Pydantic, etc.). Max 3 calls per question. Never include secrets.
