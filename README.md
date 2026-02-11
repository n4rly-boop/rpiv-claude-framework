# RPIV Framework for Claude Code

> **Research → Plan → Implement → Validate**

A structured workflow framework for Claude Code that enforces artifact persistence, context compression, and comprehensive multi-agent validation.

## Overview

RPIV provides a disciplined approach to software engineering tasks with Claude Code by:

- **Persisting all knowledge** to an Obsidian vault (chat is ephemeral)
- **Compressing context** through specialized distiller agents
- **Enforcing workflow** with required artifacts at each phase
- **Validating comprehensively** with a two-pass multi-agent system

---

## Installation Guide

### Prerequisites

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed and authenticated
- [Node.js](https://nodejs.org/) v18+ (for MCP servers)
- Git

### Step 1: Install MCP Servers (User Scope)

RPIV requires MCP servers to be configured at the user scope in Claude Code.

#### 1.1 Add Obsidian MCP Server

The Obsidian MCP server enables artifact persistence to your vault.

```bash
# Add Obsidian MCP server (user scope)
claude mcp add obsidian --scope user -- npx -y @mauricio.wolff/mcp-obsidian@latest
```

#### 1.2 Add Context7 MCP Server (Optional but Recommended)

Context7 provides up-to-date documentation for external libraries.

```bash
# Add Context7 MCP server (user scope)
claude mcp add context7 --scope user -- npx -y @upstash/context7-mcp
```

#### 1.3 Verify MCP Installation

```bash
# List configured MCP servers
claude mcp list

# Start Claude Code and verify servers are connected
claude

# In Claude Code, check MCP status
> /mcp
# Should show obsidian and context7 servers as connected
```

#### 1.4 MCP Troubleshooting

```bash
# Remove and re-add if having issues
claude mcp remove obsidian --scope user

# Check MCP configuration
claude mcp list
```

### Step 2: Initialize Vault Structure

Create the base vault directory structure:

```bash
# Create vault base directory
mkdir -p ~/context_vault

# The framework will auto-create repo-specific directories
# when you run /rpiv:start
```

**Vault structure** (created automatically per-repo):
```
~/context_vault/
└── <repo_name>/
    ├── sessions/           # RPIV session artifacts
    ├── knowledge/          # Persistent knowledge
    │   ├── microservices/  # Black-box service docs
    │   ├── services/       # Internal service docs
    │   ├── conventions/    # Code conventions
    │   └── patterns/       # Implementation patterns
    ├── handoffs/           # Session handoff documents
    └── research/           # Ad-hoc research artifacts
```

### Step 3: Clone and Configure RPIV Framework

```bash
# Clone the framework into your project
git clone https://github.com/your-org/rpiv-claude-framework.git
cd rpiv-claude-framework

# Or copy .claude directory to an existing project
cp -r rpiv-claude-framework/.claude /path/to/your/project/
```

### Step 4: Configure Project Settings (Optional)

Edit `.claude/settings.json` if needed:

```json
{
  "env": {
    "VAULT_BASE": "$HOME/context_vault",
    "MAX_THINKING_TOKENS": "32000"
  }
}
```

### Step 5: Verify Installation

```bash
# Navigate to your project
cd /path/to/your/project

# Start Claude Code
claude

# Verify RPIV commands are available
> /rpiv:start --help

# Run vault health check
> /vault_maintenance --check
```

---

## Quick Start: Your First RPIV Session

```bash
# 1. Start a session with enhanced context gathering
/rpiv:start "Add user authentication to API"

# 2. Research the codebase (spawns distiller agents)
/rpiv:research

# 3. [Optional] Discuss approach if research raises questions
/rpiv:discuss --topic approach

# 4. Create implementation plan (requires research artifact)
/rpiv:plan

# 5. Execute the plan (requires plan artifact)
/rpiv:implement

# 6. Validate implementation (two-pass system)
/rpiv:validate

# 7. Create session summary with manual testing playbook
/session_summary
```

---

## RPIV Workflow

### Workflow Diagram

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌───────────┐    ┌──────────┐
│  Start  │───▶│ Research │───▶│   Plan   │───▶│ Implement │───▶│ Validate │
└─────────┘    └──────────┘    └──────────┘    └───────────┘    └──────────┘
     │              │               │                                  │
     │              ▼               ▼                                  │
     │         [Discuss]       [Discuss]                               │
     │         (optional)      (optional)                              │
     │                                                                 │
     │                              ┌──────────────────────────────────┘
     │                              │
     │                              ▼
     │                         FAIL? ──▶ Back to Plan (iteration)
     │                              │
     │                              ▼
     │                         PASS? ──▶ /session_summary
     │
     └─────────────────────────────────▶ Artifacts in vault
```

### Phase Details

| Phase | Command | Artifact | Purpose |
|-------|---------|----------|---------|
| **Start** | `/rpiv:start` | `00_context.md` | Initialize session, gather context |
| **Discuss** | `/rpiv:discuss` | `DXX_<topic>.md` | Record decisions (optional) |
| **Research** | `/rpiv:research` | `1X_research.md` | Analyze codebase via distillers |
| **Plan** | `/rpiv:plan` | `2X_plan.md` | Create implementation plan |
| **Implement** | `/rpiv:implement` | `3X_implementation.md` | Execute plan |
| **Validate** | `/rpiv:validate` | `4X_validation.md` | Two-pass validation |
| **Summary** | `/session_summary` | `50_session_summary.md` | Final summary |

### Artifact Versioning

Artifacts are **never overwritten** - they increment on iteration:

```
First iteration:   10_research → 20_plan → 30_implementation → 40_validation (FAIL)
Second iteration:  11_research → 21_plan → 31_implementation → 41_validation (PASS)
```

---

## Two-Pass Validation

### Pass 1: Fast Surface Scan (~5 min)

Always runs. Collects ALL issues (fail-all-at-once):

| Check | What It Does |
|-------|--------------|
| `/tooling check` | Linting, formatting, type checking |
| `/tooling test` | Unit tests |
| `code-reviewer` | General code review |

### Pass 2: Deep Multi-Agent Analysis (~15-20 min)

Auto-triggers when Pass 1 finds **critical issues**. Runs 4 specialists **in parallel**:

| Agent | Focus Area |
|-------|------------|
| `defensive-reviewer` | Edge cases, null safety, error handling |
| `integration-reviewer` | API contracts, breaking changes |
| `security-reviewer` | Injection, auth bypasses, data leaks |
| `logic-reviewer` | Requirements vs implementation |

**Skip Pass 2** for quick iterations:
```bash
/rpiv:validate --fast
```

---

## Utility Commands

| Command | Purpose |
|---------|---------|
| `/vault_maintenance` | Audit and fix vault structure |
| `/tooling check` | Run project linters/type checkers |
| `/tooling test` | Run test suite |
| `/tooling format` | Format code |
| `/commit` | Create git commit with approval |
| `/pr_ready` | Full pre-PR checklist |
| `/create_handoff` | Create handoff for session transfer |
| `/resume_handoff` | Resume from handoff document |

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/README.md](./docs/README.md) | Documentation index |
| [docs/architecture.md](./docs/architecture.md) | System design and artifact layout |
| [docs/workflow-guide.md](./docs/workflow-guide.md) | Step-by-step RPIV workflow |
| [docs/commands-reference.md](./docs/commands-reference.md) | All slash commands |
| [docs/agents-reference.md](./docs/agents-reference.md) | Distiller and reviewer agents |
| [docs/best-practices.md](./docs/best-practices.md) | Tips and anti-patterns |
| [CLAUDE.md](./CLAUDE.md) | Workspace contract and rules |

---

## Framework Components

```
.claude/
├── agents/              # 12 specialized agents
│   ├── code-reviewer.md
│   ├── defensive-reviewer.md
│   ├── security-reviewer.md
│   ├── logic-reviewer.md
│   ├── integration-reviewer.md
│   ├── microservice-distiller.md
│   ├── repo-doc-distiller.md
│   ├── codebase-analyzer.md
│   ├── codebase-locator.md
│   ├── codebase-pattern-finder.md
│   ├── code-simplifier.md
│   └── web-search-researcher.md
├── commands/            # Slash commands
│   ├── rpiv/            # Core RPIV workflow
│   ├── workflow/        # Session management
│   ├── code/            # Code operations
│   ├── git/             # Git operations
│   ├── research/        # Research tools
│   └── planning/        # Convention extraction
├── skills/              # Reusable agent skills
│   ├── tooling/         # Code quality tools
│   ├── vault-maintenance/  # Vault health
│   └── ...
└── settings.json        # Environment config
```

---

## Troubleshooting

### MCP Server Not Connecting

```bash
# List configured MCP servers
claude mcp list --scope user

# Remove and re-add the server
claude mcp remove obsidian --scope user
claude mcp add obsidian --scope user \
  -e OBSIDIAN_VAULT_PATH="$HOME/context_vault" \
  -- npx -y @mauricio.wolff/mcp-obsidian@latest

# Check Claude Code logs
claude --debug
```

### Vault Not Found

```bash
# Verify vault path
ls -la ~/context_vault

# Check VAULT_BASE environment variable
echo $VAULT_BASE

# Initialize vault structure
mkdir -p ~/context_vault
```

### Commands Not Available

```bash
# Ensure .claude directory is in your project root
ls -la .claude/commands/

# Verify CLAUDE.md exists
cat CLAUDE.md | head -20
```

### Validation Always Failing

```bash
# Run vault maintenance to check artifact integrity
/vault_maintenance

# Check if tooling is configured for your project
/tooling check

# Extract conventions if tooling not detected
/extract_conventions
```

---

## License

MIT
