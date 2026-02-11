# RPIV Framework Documentation

> **Research → Plan → Implement → Validate**

A structured workflow framework for Claude Code that emphasizes artifact persistence, context compression, and comprehensive validation.

## Quick Start

```bash
# Start a new RPIV session (enhanced context gathering)
/rpiv:start "Add user authentication to API"

# Research the codebase
/rpiv:research

# Discuss approach if open questions (optional, auto-suggested)
/rpiv:discuss --topic "approach"

# Create implementation plan
/rpiv:plan

# Execute the plan
/rpiv:implement

# Validate the implementation
/rpiv:validate

# Create session summary
/session_summary
```

## Documentation Index

| Document | Description |
|----------|-------------|
| [Architecture](./architecture.md) | System design, artifact layout, MCP integration |
| [Workflow Guide](./workflow-guide.md) | Step-by-step RPIV workflow |
| [Commands Reference](./commands-reference.md) | All available slash commands |
| [Agents Reference](./agents-reference.md) | Distiller and reviewer agents |
| [Best Practices](./best-practices.md) | Tips, patterns, and anti-patterns |

## Core Principles

### 1. Artifacts Are Authoritative; Chat Is Ephemeral
All persistent knowledge is written to the Obsidian vault. Chat context is temporary and will be lost.

### 2. MCP-Only Artifact Policy
All artifacts are written via the `obsidian` MCP server to `$VAULT_BASE/<repo_name>/...`

### 3. Context Compression Via Distillers
Large files and code dumps are never pasted into chat. Distiller agents compress context and write to vault.

### 4. File Pointers Over Code Dumps
Reference files as `path/to/file.py:line_number`. Full code belongs in vault artifacts.

## Environment Setup

### Required
- Claude Code CLI
- Obsidian MCP server (`@mauricio.wolff/mcp-obsidian`)

### Configuration
```json
// .claude/settings.json
{
  "env": {
    "VAULT_BASE": "$HOME/context_vault"
  }
}
```

## Framework Components

```
.claude/
├── agents/           # 12 specialized agents
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
├── commands/         # Slash commands
│   ├── rpiv/         # Core workflow
│   ├── workflow/     # Session management
│   ├── code/         # Code operations
│   ├── git/          # Git operations
│   ├── research/     # Research tools
│   └── planning/     # Convention extraction
└── settings.json     # Environment config
```

## Artifact Layout

```
$VAULT_BASE/<repo_name>/
├── sessions/<session_id>/
│   ├── 00_context.md         # Enhanced context (with clarifications)
│   ├── DXX_<topic>.md        # Discussion artifacts (D01, D02...)
│   ├── 1X_research.md        # Research (10, 11, 12...)
│   ├── 2X_plan.md            # Plans (20, 21, 22...)
│   ├── 3X_implementation.md  # Implementation (30, 31...)
│   ├── 4X_validation.md      # Validation (40, 41...)
│   ├── 50_session_summary.md # Final summary
│   └── index.md              # Session index
├── knowledge/
│   ├── microservices/        # Black-box docs
│   ├── services/             # Internal docs
│   ├── conventions/          # Code style
│   └── patterns/             # Implementation patterns
└── handoffs/                 # Session handoffs
```

## License

MIT
