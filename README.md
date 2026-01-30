# RPIV Framework for Claude Code

> **Research → Plan → Implement → Validate**

A structured workflow framework for Claude Code that enforces artifact persistence, context compression, and comprehensive multi-agent validation.

## Overview

RPIV provides a disciplined approach to software engineering tasks with Claude Code by:

- **Persisting all knowledge** to an Obsidian vault (chat is ephemeral)
- **Compressing context** through specialized distiller agents
- **Enforcing workflow** with required artifacts at each phase
- **Validating comprehensively** with a two-pass multi-agent system

## Quick Start

```bash
# 1. Start a session
/rpiv_start "Add user authentication to API"

# 2. Research the codebase
/rpiv_research

# 3. Create implementation plan
/rpiv_plan

# 4. Execute the plan
/rpiv_implement

# 5. Validate the implementation
/rpiv_validate

# 6. Create session summary
/session_summary
```

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
└── settings.json        # Environment config
```

## Key Features

### Two-Pass Validation

```
Pass 1 (Fast ~5min)          Pass 2 (Deep ~15-20min)
├── make check               ├── defensive-reviewer
├── make test                ├── integration-reviewer
└── code-reviewer            ├── security-reviewer
                             └── logic-reviewer
```

Pass 2 only triggers when Pass 1 finds critical issues.

### Artifact Versioning

Artifacts are never overwritten between iterations:

```
10_research.md → 20_plan.md → 30_implementation.md → 40_validation.md (FAIL)
11_research.md → 21_plan.md → 31_implementation.md → 41_validation.md (PASS)
```

### Context Compression

Distiller agents write to vault and return only paths + 10-line summaries.

## Requirements

- Claude Code CLI
- Obsidian MCP server (`@mauricio.wolff/mcp-obsidian`)
- Obsidian vault at `$VAULT_BASE` (default: `$HOME/context_vault`)

## Configuration

```json
// .claude/settings.json
{
  "env": {
    "VAULT_BASE": "$HOME/context_vault"
  }
}
```

## License

MIT
