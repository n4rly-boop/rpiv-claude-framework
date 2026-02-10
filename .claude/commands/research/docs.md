---
description: Generate or update documentation for code, APIs, or features
model: sonnet
---

# Generate Documentation

You are tasked with generating or updating technical documentation based on the codebase.

## Output Locations

Use the `obsidian` MCP server to save artifacts. Determine repo name with: `basename $(git rev-parse --show-toplevel)`

All documentation goes to `{repo_name}/knowledge/`:
```
{repo_name}/knowledge/
├── microservices/       # Black-box docs (from root - /service_docs)
├── services/            # Internal service docs (from inside repo)
├── conventions/         # Code conventions (from /extract_conventions)
├── patterns/            # Code patterns
└── api/                 # API reference docs
```

Legacy path `{repo_name}/docs/` is still supported for backwards compatibility.

## Process

### For Code Documentation (`/docs path/to/file`)

1. **Read the target file(s)**

2. **Analyze**:
   - Public interfaces (exported functions, classes, types)
   - Function signatures and return types
   - Dependencies and imports
   - Error handling patterns

3. **Generate documentation**:
   - For TypeScript/JavaScript: JSDoc comments
   - For Python: Docstrings (Google or NumPy style, match existing)
   - For Go: GoDoc comments
   - For Java: Javadoc

4. **Output options**:
   - **Inline**: Add/update comments in the file itself
   - **External**: Use `obsidian` MCP to create `{repo_name}/docs/api/[module-name].md`

   Ask user preference if unclear.

### For API Documentation (`/docs api`)

1. **Find API definitions**:
   - OpenAPI/Swagger specs
   - Route definitions
   - Controller/handler files
   - GraphQL schemas

2. **Generate reference docs**:
   ```markdown
   # API Reference

   ## Authentication
   All endpoints require `Authorization: Bearer <token>` header.

   ## Endpoints

   ### POST /api/users
   Create a new user.

   **Request Body**:
   ```json
   {
     "email": "string (required)",
     "name": "string (required)",
     "role": "string (optional, default: 'user')"
   }
   ```

   **Response**: `201 Created`
   ```json
   {
     "id": "string",
     "email": "string",
     "name": "string",
     "createdAt": "ISO 8601 date"
   }
   ```

   **Errors**:
   - `400 Bad Request` - Invalid input
   - `409 Conflict` - Email already exists
   ```

3. **Save to**: `{repo_name}/docs/api/reference.md` via `obsidian` MCP or update existing

### For README (`/docs readme`)

1. **Analyze project**:
   - Package.json / pyproject.toml / go.mod
   - Existing README content
   - Directory structure
   - Available scripts/commands

2. **Generate/update sections**:
   ```markdown
   # Project Name

   Brief description from package metadata.

   ## Quick Start

   ```bash
   # Installation
   [detected from package manager]

   # Run
   [detected from scripts]
   ```

   ## Development

   ### Prerequisites
   - [Runtime] version X.Y
   - [Dependencies]

   ### Setup
   [Step by step]

   ### Commands
   | Command | Description |
   |---------|-------------|
   | `npm run dev` | Start dev server |
   | `npm test` | Run tests |

   ## Project Structure
   ```
   src/
   ├── api/        # HTTP handlers
   ├── services/   # Business logic
   └── ...
   ```

   ## Contributing
   [Link to CONTRIBUTING.md or brief guidelines]
   ```

3. **Preserve existing content**: Don't overwrite custom sections

### For Feature Documentation (`/docs feature "description"`)

1. **Research the feature in codebase**:
   - Find all related files
   - Trace the flow (entry point to completion)
   - Identify configuration options

2. **Generate guide**:
   ```markdown
   # Feature: [Name]

   ## Overview
   [What it does, why it exists]

   ## How It Works
   [High-level flow with diagram if helpful]

   ## Usage

   ### Basic Usage
   ```[language]
   [Code example]
   ```

   ### Configuration
   | Option | Type | Default | Description |
   |--------|------|---------|-------------|
   | ... | ... | ... | ... |

   ### Advanced Usage
   [More complex scenarios]

   ## Related
   - [Link to related features]
   - [Link to API docs]
   ```

3. **Save to**: `{repo_name}/docs/guides/[feature-name].md` via `obsidian` MCP

## Validation

After generating docs:

1. **Check for broken links**
2. **Verify code examples compile/run**
3. **Ensure all public APIs are documented**

## Output

```
## Documentation Updated

Created/Modified:
- {repo_name}/docs/api/reference.md (15 endpoints documented)
- {repo_name}/docs/guides/authentication.md (new)

Coverage:
- API endpoints: 15/15 (100%)
- Public functions: 42/50 (84%)

Suggestions:
- 8 public functions in src/utils/ lack documentation
- Consider adding sequence diagram for auth flow
```
