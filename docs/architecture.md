# RPIV Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Claude Code CLI                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │    RPIV      │    │   Workflow   │    │    Utility   │      │
│  │   Commands   │    │   Commands   │    │   Commands   │      │
│  │              │    │              │    │              │      │
│  │ /rpiv:start  │    │ /debug       │    │ /commit      │      │
│  │ /rpiv:research│   │ /pr_ready    │    │ /describe_pr │      │
│  │ /rpiv:plan   │    │ /session_sum │    │ /docs        │      │
│  │ /rpiv:impl   │    │ /create_hand │    │ /review      │      │
│  │ /rpiv:valid  │    │ /resume_hand │    │ /simplify    │      │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘      │
│         │                   │                   │               │
│         └───────────────────┼───────────────────┘               │
│                             │                                   │
│                             ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Agent Layer                            │  │
│  │                                                           │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │  │
│  │  │  Reviewers  │  │  Distillers │  │  Analyzers  │       │  │
│  │  │             │  │             │  │             │       │  │
│  │  │ code-review │  │ microserv   │  │ codebase-   │       │  │
│  │  │ defensive   │  │ repo-doc    │  │ analyzer    │       │  │
│  │  │ security    │  │ pattern-    │  │ locator     │       │  │
│  │  │ logic       │  │ finder      │  │ web-search  │       │  │
│  │  │ integration │  │ simplifier  │  │             │       │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │  │
│  └──────────────────────────┬───────────────────────────────┘  │
│                             │                                   │
└─────────────────────────────┼───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Obsidian MCP Server                        │
│                                                                 │
│   read_note │ write_note │ search_notes │ get_frontmatter      │
│                                                                 │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Obsidian Vault                          │
│                        ($VAULT_BASE)                            │
│                                                                 │
│   /<repo>/sessions/     Session artifacts (ephemeral)          │
│   /<repo>/knowledge/    Stable knowledge (persistent)          │
│   /<repo>/handoffs/     Session handoffs                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Artifact Versioning System

Artifacts within a session are **never overwritten**. Instead, they are versioned using a decade-based numbering scheme:

```
Pattern │ Artifact Type    │ Examples
────────┼──────────────────┼─────────────────
  00    │ Context          │ 00 (never versioned)
  DXX   │ Discussion       │ D01, D02, D03...
  1X    │ Research         │ 10, 11, 12...
  2X    │ Plan             │ 20, 21, 22...
  3X    │ Implementation   │ 30, 31, 32...
  4X    │ Validation       │ 40, 41, 42...
  50    │ Session Summary  │ 50 (written once)
```

**Discussion artifacts** use `DXX_<topic>.md` naming:
- `D01_scope.md` - Initial scoping discussion
- `D02_approach.md` - Approach discussion after research
- `D03_design.md` - Design review before implementation
- Sequential numbering (D01, D02, D03...) maintains chronological order

### Example: Multi-Iteration Session

```
sessions/20260115-143022-add-auth/
├── 00_context.md           # Initial context (enhanced with clarifications)
├── 10_research.md          # First research
├── D01_approach.md         # Discussion: chose JWT over sessions
├── 20_plan.md              # First plan
├── 30_implementation.md    # First implementation
├── 40_validation.md        # First validation (FAIL)
├── D02_retrospective.md    # Discussion: what went wrong
├── 21_plan.md              # Plan fixes
├── 31_implementation.md    # Implementation fixes
├── 41_validation.md        # Second validation (PASS)
├── 50_session_summary.md   # Final summary
└── index.md                # Tracks all artifacts
```

### Finding Latest Artifacts

```bash
# Find latest research
ls -1 $SESSION_PATH/1?_research.md | sort -V | tail -1

# Find latest plan
ls -1 $SESSION_PATH/2?_plan.md | sort -V | tail -1

# Find latest implementation
ls -1 $SESSION_PATH/3?_implementation.md | sort -V | tail -1

# Find latest validation
ls -1 $SESSION_PATH/4?_validation.md | sort -V | tail -1
```

## Two-Pass Validation System

The validation phase uses a two-pass approach to balance speed with thoroughness:

```
┌─────────────────────────────────────────────────────────────┐
│                    PASS 1: Fast Surface Scan                │
│                        (~5 minutes)                         │
│                                                             │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│   │ /tooling    │  │ /tooling    │  │ code-       │        │
│   │ check       │  │ test        │  │ reviewer    │        │
│   │             │  │             │  │             │        │
│   │ format      │  │ unit tests  │  │ general     │        │
│   │ lint        │  │             │  │ review      │        │
│   │ type check  │  │             │  │             │        │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│          │                │                │                │
│          └────────────────┼────────────────┘                │
│                           │                                 │
│                           ▼                                 │
│                  ┌─────────────────┐                        │
│                  │ CRITICAL issues │                        │
│                  │    found?       │                        │
│                  └────────┬────────┘                        │
│                           │                                 │
│              ┌────────────┼────────────┐                    │
│              │ YES        │            │ NO                 │
│              ▼            │            ▼                    │
└──────────────┼────────────┼────────────┼────────────────────┘
               │            │            │
               ▼            │            ▼
┌──────────────────────┐    │    ┌──────────────────────┐
│   PASS 2: Deep       │    │    │   SKIP PASS 2        │
│   Multi-Agent        │    │    │                      │
│   (~15-20 min)       │    │    │   Write report       │
│                      │    │    │   All good!          │
│ ┌──────────────────┐ │    │    └──────────────────────┘
│ │ Run 4 agents     │ │    │
│ │ IN PARALLEL:     │ │    │
│ │                  │ │    │
│ │ • defensive-     │ │    │
│ │   reviewer       │ │    │
│ │ • integration-   │ │    │
│ │   reviewer       │ │    │
│ │ • security-      │ │    │
│ │   reviewer       │ │    │
│ │ • logic-         │ │    │
│ │   reviewer       │ │    │
│ └──────────────────┘ │    │
└──────────────────────┘    │
                            │
                            ▼
                  ┌─────────────────┐
                  │  --fast flag?   │
                  │  Skip Pass 2    │
                  └─────────────────┘
```

### Pass 1: Fast Surface Scan
- **Duration**: ~5 minutes
- **Always runs**
- **Components**:
  - `/tooling check` - formatting, linting, type checking
  - `/tooling test` - unit tests
  - `code-reviewer` - general code review
- **Key feature**: Fail-all-at-once (collects ALL issues, never exits early)

### Pass 2: Deep Multi-Agent Analysis
- **Duration**: ~15-20 minutes
- **Triggers**: Only when Pass 1 finds CRITICAL issues
- **Components** (run in parallel):
  - `defensive-reviewer` - Edge cases, null safety, error handling
  - `integration-reviewer` - API contracts, breaking changes
  - `security-reviewer` - Injection, auth bypasses, data leaks
  - `logic-reviewer` - Requirements vs implementation

### Skip Pass 2
Use `--fast` flag for quick iterations:
```
/rpiv:validate --fast
```

## Context Compression Architecture

The framework prevents context overflow through distiller agents:

```
┌─────────────────────────────────────────────────────────────┐
│                      Main Agent                             │
│                                                             │
│   NEVER receives:                                           │
│   • Full file contents (>50 lines)                         │
│   • Raw agent outputs                                       │
│   • Large code dumps                                        │
│                                                             │
│   ONLY receives:                                            │
│   • Vault paths                                             │
│   • 10-line max summaries                                   │
│   • File:line references                                    │
│                                                             │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Distiller Agents                         │
│                                                             │
│   • Read files directly                                     │
│   • Analyze and compress                                    │
│   • Write to vault (200-400 lines max)                     │
│   • Return only path + brief summary                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Distiller Budget Constraints

| Agent | Max Output | Purpose |
|-------|------------|---------|
| `microservice-distiller` | 200-400 lines | Black-box service docs |
| `repo-doc-distiller` | 200-400 lines | Internal repo docs |
| `codebase-analyzer` | 200-600 lines | Implementation analysis |
| `codebase-locator` | 100-300 lines | File location maps |
| `codebase-pattern-finder` | 200-600 lines | Pattern catalogs |
| `code-simplifier` | 200-600 lines | Simplification suggestions |

## MCP Integration

All artifact operations use the Obsidian MCP server:

### Available Operations
```
read_note          # Read note content
write_note         # Write/create notes (overwrite, append, prepend)
delete_note        # Delete notes
move_note          # Move/rename notes
list_directory     # List vault directories
read_multiple_notes # Batch read
search_notes       # Search across vault
get_frontmatter    # Read YAML frontmatter
update_frontmatter # Update YAML frontmatter
get_notes_info     # Get metadata
manage_tags        # Add, remove, list tags
```

### Vault Structure
```
$VAULT_BASE/                          # Default: $HOME/context_vault
└── <repo_name>/
    ├── sessions/
    │   └── <session_id>/
    │       ├── 00_context.md         # Enhanced with clarifications
    │       ├── DXX_<topic>.md        # Discussion artifacts (D01, D02...)
    │       ├── 1X_research.md
    │       ├── 2X_plan.md
    │       ├── 3X_implementation.md
    │       ├── 4X_validation.md
    │       ├── 50_session_summary.md
    │       └── index.md
    ├── knowledge/
    │   ├── microservices/
    │   │   └── <service>.md
    │   ├── services/
    │   │   └── <service>.md
    │   ├── conventions/
    │   │   └── main.md
    │   └── patterns/
    │       └── <pattern>.md
    ├── handoffs/
    │   └── YYYY-MM-DD_HH-MM-SS_description.md
    └── research/
        └── YYYY-MM-DD-description.md
```

## Black Box Rule (Monorepo Context)

When working in a root monorepo with nested microservices:

```
┌─────────────────────────────────────────────────────────────┐
│                     Root Monorepo                           │
│                                                             │
│   From root perspective:                                    │
│   Microservices are BLACK BOXES                            │
│                                                             │
│   Document only:                                            │
│   • Purpose/role                                            │
│   • Public interfaces (APIs, ports)                         │
│   • Integration points                                      │
│   • Deploy surface                                          │
│                                                             │
│   Store in:                                                 │
│   $VAULT_BASE/<root_repo>/knowledge/microservices/         │
│                                                             │
│   ┌─────────────────┐  ┌─────────────────┐                 │
│   │  microservice-a │  │  microservice-b │                 │
│   │    (black box)  │  │    (black box)  │                 │
│   │       .git      │  │       .git      │                 │
│   └─────────────────┘  └─────────────────┘                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

When working **inside** a microservice:
- Document comprehensively (internal details)
- Store in: `$VAULT_BASE/<microservice_repo>/knowledge/`

## Artifact Header Template

All artifacts include YAML frontmatter:

```yaml
---
repo: <repo_name>
scope: root|microservice|service
microservice: <name_or_null>
session: <session_id_or_null>
type: context|discussion|research|plan|implementation|validation|doc|index
created: <iso8601>
updated: <iso8601>
sources:
  - <paths_or_commands_used>
---
```

**Discussion artifacts** also include:
```yaml
topic: scope|approach|design|review|retrospective
phase_after: context|research|plan|implement|validate
```
