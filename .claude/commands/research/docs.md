---
description: Generate or update documentation for code, APIs, or features
model: sonnet
---

# Generate Documentation

Generate or update technical documentation based on codebase analysis.

## Output Location

Via `obsidian` MCP at `{repo_name}/knowledge/` (repo name: `basename $(git rev-parse --show-toplevel)`).

## Modes

### Code Documentation (`/docs path/to/file`)

1. Read target file(s)
2. Analyze: public interfaces, signatures, return types, dependencies, error handling
3. Generate language-appropriate docs (JSDoc, docstrings, GoDoc, Javadoc — match existing style)
4. Output: inline (in-file) or external (`{repo_name}/knowledge/api/[module].md`) — ask user preference if unclear

### API Documentation (`/docs api`)

1. Find API definitions (OpenAPI, routes, controllers, GraphQL schemas)
2. Generate per-endpoint reference: method, path, request body, response format, error codes
3. Save to `{repo_name}/knowledge/api/reference.md`

### README (`/docs readme`)

1. Analyze: package metadata, directory structure, available scripts
2. Generate/update: Quick Start, Prerequisites, Setup, Commands table, Project Structure
3. Preserve existing custom sections

### Feature Documentation (`/docs feature "description"`)

1. Research feature: find all related files, trace flow, identify config options
2. Generate guide: Overview, How It Works, Basic/Advanced Usage, Configuration table, Related links
3. Save to `{repo_name}/knowledge/guides/[feature-name].md`

## Validation

After generating: check broken links, verify code examples, ensure all public APIs documented.

## Output

```
## Documentation Updated

Created/Modified:
- <paths with details>

Coverage: API endpoints: X/Y | Public functions: X/Y

Suggestions:
- <gaps or improvements>
```
