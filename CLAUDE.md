# Claude Code Workspace Contract

This document defines non-negotiable rules for Claude agents working in this repository.

## Core Principles

### 1. Artifacts Are Authoritative; Chat Is Ephemeral
- All persistent knowledge MUST be written to the Obsidian vault
- Chat context is temporary and will be lost
- Never rely on chat history for important decisions
- If information is valuable, write it to vault

### 2. MCP-Only Artifact Policy (No `.claude/artifacts`)
- **ALL artifacts MUST be written via `obsidian` MCP server**
- **NEVER create or use `.claude/artifacts` directory**
- **NEVER use symlinks to mirror artifacts**
- Vault base: `$VAULT_BASE` (default: `$HOME/context_vault`)
- Repo artifacts go to: `$VAULT_BASE/<repo_name>/...`

### 3. Context Compression Via Distillers
- **NEVER paste large files or code dumps into chat**
- Use distiller agents to compress context
- Main agent synthesizes ONLY from distillations
- Write to vault, return path + summary (max 10 lines)
- Distiller outputs: 200-400 lines max

### 4. File Pointers Over Code Dumps
- Reference files as `path/to/file.py:line_number`
- Include only minimal snippets when absolutely necessary
- Full code belongs in vault artifacts, not chat

## Artifact Layout

### Session Artifacts (ephemeral, per-session)
```
$VAULT_BASE/<repo_name>/sessions/<session_id>/
├── 00_context.md         # Initial context snapshot (never versioned)
├── 1X_research.md        # Research findings (10, 11, 12...)
├── 2X_plan.md            # Implementation plan (20, 21, 22...)
├── 3X_implementation.md  # Implementation summary (30, 31, 32...)
├── 4X_validation.md      # Validation results (40, 41, 42...)
├── 50_session_summary.md # Session summary (written once at end)
└── index.md              # Session index/summary
```

### Artifact Versioning (IMPORTANT)
Artifacts are **NEVER overwritten** between RPIV iterations:
- First iteration: `10_research.md` → `20_plan.md` → `30_implementation.md` → `40_validation.md`
- Second iteration: `11_research.md` → `21_plan.md` → `31_implementation.md` → `41_validation.md`
- Pattern: `<decade><iteration>_<type>.md` where decade = artifact type (1=research, 2=plan, 3=impl, 4=valid)

**Finding artifacts:**
```bash
# Find latest research: ls -1 session_path/1?_research.md | sort -V | tail -1
# Find latest plan: ls -1 session_path/2?_plan.md | sort -V | tail -1
# etc.
```

**Writing new artifacts:**
- Check existing files with same prefix (e.g., `2?_plan.md`)
- Increment: if `20_plan.md` exists, write `21_plan.md`

### Stable Knowledge (persistent, updated incrementally)
```
$VAULT_BASE/<repo_name>/knowledge/
├── microservices/
│   ├── <name>.md      # Black-box docs (from root repo perspective)
│   └── index.md       # Microservice index
├── services/
│   └── <name>.md      # Service docs (inside repo)
├── conventions/
│   └── <name>.md      # Code conventions
└── patterns/
    └── <name>.md      # Implementation patterns
```

## Artifact Header Template

All artifacts MUST include YAML frontmatter:

```yaml
---
repo: <repo_name>
scope: root|microservice|service
microservice: <name_or_null>
session: <session_id_or_null>
type: context|research|plan|implementation|validation|doc|index|conventions|patterns
created: <iso8601>
updated: <iso8601>
sources:
  - <paths_or_commands_used>
---
```

## RPIV Workflow

### Research -> Plan -> Implement -> Validate

1. **Research** (`/rpiv_research`)
   - Gather context via distiller agents
   - Write `10_research.md`
   - Update stable knowledge if applicable

2. **Plan** (`/rpiv_plan`)
   - Requires research artifact (unless `--no-research`)
   - Write `20_plan.md` with:
     - Phases and success criteria
     - **Manual Testing Plan (REQUIRED)** - specific curl commands, expected responses, side effects
   - Plans must include actionable verification steps

3. **Implement** (`/rpiv_implement`)
   - Requires plan artifact (enforced)
   - Execute changes
   - Write `30_implementation.md`

4. **Validate** (`/rpiv_validate`)
   - **Two-Pass Validation System**:
     - **Pass 1** (always, ~5 min): `make check`, `make test`, code-reviewer
       - Fail-all-at-once: collects ALL issues, never exits early
     - **Pass 2** (auto-triggers on critical issues, ~15-20 min):
       - Runs 4 specialist agents in parallel:
         - `defensive-reviewer` - Edge cases, null safety
         - `integration-reviewer` - Breaking changes, contracts
         - `security-reviewer` - Vulnerabilities, exploits
         - `logic-reviewer` - Requirements vs plan
     - Use `--fast` flag to skip Pass 2 for quick iterations
   - Write `40_validation.md`
   - **Purpose**: Find ALL issues in one run, not iteratively

5. **Summarize** (`/session_summary`)
   - Write `50_session_summary.md` with:
     - Empirical verification playbook (manual testing)
     - **Future Work & Integration** - how to build upon this work
     - Known limitations and recommended next steps

## Black Box Rule (Monorepo Context)

### From Root Monorepo
- Nested git repos (microservices) are **black boxes**
- Document externally visible aspects only:
  - Purpose/role
  - Public interfaces (APIs, ports)
  - Integration points
  - Deploy surface
- Store in: `$VAULT_BASE/<root_repo>/knowledge/microservices/`

### From Inside Microservice
- Document comprehensively
- Store in: `$VAULT_BASE/<microservice_repo>/knowledge/`

## Output Requirements

Every command MUST end with:
```
Created/Updated:
- <vault_path_1>
- <vault_path_2>

Next: <suggested_next_command>

<digest: max 10 lines>
```

## Prohibited Actions

1. Creating `.claude/artifacts` directory
2. Using symlinks for artifact storage
3. Pasting large code dumps (>50 lines) in chat
4. Running `/rpiv_implement` without plan artifact
5. Running `/rpiv_plan` without research artifact (unless `--no-research`)
6. Distiller outputs exceeding 400 lines
7. Returning raw agent outputs without vault persistence
8. **Running tools directly instead of make commands**:
   - ❌ NEVER: `ruff check .`, `black .`, `mypy .`, `pytest tests/`
   - ✅ ALWAYS: `make check`, `make test`, `make format`
9. Creating plans without manual testing steps
10. Skipping Pass 2 validation when critical issues exist (unless `--fast` flag)

## Validation Best Practices

### Two-Pass System Philosophy
- **Goal**: Find ALL issues in one validation run, not iteratively
- **Pass 1**: Fast feedback (5 min) - catches obvious issues
- **Pass 2**: Deep analysis (15-20 min) - catches subtle issues
- **Result**: 1-2 iterations instead of 7+ iterations

### When to Use --fast Flag
- ✅ Quick iterations during active development
- ✅ You know the issue and just want surface validation
- ✅ Time-constrained and will do full validation later
- ❌ Before creating PR (always use full validation)
- ❌ After major refactoring (need comprehensive analysis)

### Make Commands Policy
This repo uses Poetry + Make for consistency:
- `make check` → `poetry run black --check` + `poetry run ruff check` + `poetry run mypy`
- `make test` → `poetry run pytest`
- `make format` → `poetry run black` + `poetry run ruff check --fix`

**Why enforce make commands?**
1. Ensures correct Poetry environment
2. Runs all checks in correct order
3. Uses correct directories (CHECK_DIRS)
4. Consistent across all developers/agents

### Manual Testing Requirements
Every plan MUST include:
- **Specific curl commands** (copy-pasteable)
- **Expected responses** (exact status codes, JSON structure)
- **Observable side effects** (logs, DB changes, cache keys)
- **Negative test cases** (invalid input, missing auth)

This ensures features are verifiable by humans, not just automated tests.

## Discovery Commands (Safe Bash)

These commands are pre-approved for repo discovery:
```bash
git rev-parse --show-toplevel       # Get repo root
git rev-parse --show-prefix         # Get relative path
basename $(git rev-parse --show-toplevel)  # Get repo name
git submodule status                # List submodules
find . -maxdepth 3 -name .git -type d  # Find nested repos
```

## MCP Server Reference

### Obsidian MCP (`@mauricio.wolff/mcp-obsidian`)
Used for all vault operations:
- `read_note`: Read note content and metadata
- `write_note`: Write/create notes (modes: overwrite, append, prepend)
- `delete_note`: Delete notes from vault
- `move_note`: Move/rename notes
- `list_directory`: List vault directories
- `read_multiple_notes`: Batch read multiple notes
- `search_notes`: Search across vault
- `get_frontmatter`: Read YAML frontmatter
- `update_frontmatter`: Update YAML frontmatter
- `get_notes_info`: Get metadata for notes
- `manage_tags`: Add, remove, or list tags

Always use MCP for vault operations, never direct file writes.

### Context7 MCP (`mcp-context7`)
Used for external library documentation:
- `resolve-library-id`: Find Context7 library ID for a package name
- `query-docs`: Get up-to-date documentation and code examples

**When to use:**
- Learning unfamiliar libraries (FastAPI, Pydantic, SQLAlchemy, etc.)
- Checking latest API changes or best practices
- Finding code examples for specific use cases
- Verifying correct usage patterns

**Example workflow:**
1. Call `resolve-library-id` with library name (e.g., "fastapi")
2. Get library ID (e.g., "/tiangolo/fastapi")
3. Call `query-docs` with library ID + specific question
4. Receive relevant docs + code examples

**Important:**
- NEVER include secrets/credentials in queries
- Call at most 3 times per question (avoid excessive API usage)
- Use for external libraries only, not internal codebase
