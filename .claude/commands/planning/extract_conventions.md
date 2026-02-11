---
description: Extract code conventions, patterns, architecture, and dependencies from codebase
model: opus
---

# Extract Conventions

Analyze codebase to extract and document conventions, patterns, architecture, and dependencies. Creates persistent knowledge base for consistent development.

## Output Location

Use `obsidian` MCP. Repo name: `basename $(git rev-parse --show-toplevel)`

```
{repo_name}/knowledge/
├── conventions/main.md    # Code style, naming, file structure
├── patterns/main.md       # Common implementation patterns
├── architecture.md        # Service boundaries, data flow
└── dependencies.md        # Inter-repo deps, shared libs, external services
```

## Process

### Phase 1: Initial Scan

1. **Stack**: Languages, frameworks, build system, package manager, CI/CD
2. **Docs**: README, CONTRIBUTING, ADRs, OpenAPI/Swagger, proto/GraphQL schemas
3. **Config**: Linter, formatter, editor, compiler configs

### Phase 2: Deep Analysis (Parallel Agents)

**Agent 1: Code Style** (codebase-analyzer)
- Variable/function/class naming, file/directory naming, import organization, comment styles, error handling, logging conventions
- Extract 3-5 concrete examples per pattern

**Agent 2: Architecture** (codebase-analyzer)
- Project structure, layer separation, DI patterns, config management, service boundaries
- Map component relationships

**Agent 3: Patterns** (codebase-pattern-finder)
- API endpoints, DB access, auth/authz, caching, async/messaging, testing
- Extract reusable code snippets as templates

**Agent 4: Dependencies** (codebase-analyzer)
- Internal shared libs, external service integrations, inter-repo deps, deployment deps, version constraints

### Phase 3: Synthesis

1. Consolidate findings, resolve conflicts (document variations with context)
2. Identify gaps, create actionable "do this, not that" guidelines

### Phase 4: Write Documentation

Use `obsidian` MCP to create/update each file in `{repo_name}/knowledge/`.

**conventions/main.md**: Language & Stack, Naming Conventions (files + code tables), Code Style (imports, error handling, logging), DO/DON'T quick reference table.

**patterns/main.md**: API endpoint templates, error response format, data access patterns, testing patterns, common utilities.

**architecture.md**: System overview (ASCII diagram), module structure, data flow, service boundaries, configuration.

**dependencies.md**: Internal deps table (library, version, purpose, owner), external services table (service, purpose, config key), inter-repo deps, version constraints.

**Incremental updates**: If knowledge already exists, read first, compare, highlight changes, preserve `<!-- manual -->` sections.

### Phase 5: Tooling Configuration

Generate project-specific tooling skill.

1. **Detect tooling**: Check Makefile targets, package.json scripts, pyproject.toml tools
2. **Determine commands**: Poetry/Pipenv prefix for Python, npm scripts for Node.js, make targets for Makefile projects
3. **Present to user** (MANDATORY — use `AskUserQuestion`):
   - Show detected check/test/format commands with detection basis
   - Options: Accept (recommended), Customize, Skip (use auto-detection)
   - **NEVER fabricate the user's choice. Wait for actual response before proceeding.**
4. **If user chose Accept/Customize**: Write `.claude/skills/tooling/SKILL.md` with configured commands
5. **If user chose Skip**: No project-specific tooling skill created

## Final Output

```
## Extraction Complete

Created/Updated:
- {repo_name}/knowledge/conventions/main.md
- {repo_name}/knowledge/patterns/main.md
- {repo_name}/knowledge/architecture.md
- {repo_name}/knowledge/dependencies.md
- .claude/skills/tooling/SKILL.md (if approved)

Tooling: check: `<cmd>` | test: `<cmd>` | format: `<cmd>`

Key Findings:
- <notable pattern or convention>
- <potential inconsistency found>

Next: /rpiv:start to begin implementation with these conventions
```
