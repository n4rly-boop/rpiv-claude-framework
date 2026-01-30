# Agents Reference

Complete reference for all RPIV framework agents.

---

## Agent Categories

| Category | Agents | Purpose |
|----------|--------|---------|
| **Reviewers** | 5 | Code review and validation |
| **Distillers** | 7 | Context compression and analysis |

---

## Reviewer Agents

Reviewers are used during the `/rpiv_validate` phase to find issues in changed code.

### `code-reviewer`

**Description**: Reviews code changes for bugs, security issues, and pattern conformance.

**Model**: `sonnet`

**Tools**: `Read`, `Grep`, `Glob`

**Scope**: Changed files only (from git diff)

**Budget**: 200-400 lines

**What It Looks For**:
- Logic errors (off-by-one, null access, wrong conditions)
- Security issues (SQL injection, XSS, command injection)
- Error handling (unhandled exceptions, swallowed errors)
- Breaking changes (changed signatures, removed exports)
- Pattern violations (inconsistent naming, wrong file location)

**Output Format**:
```markdown
## Code Review: [files reviewed]

### Critical Issues (N)
#### 1. [Issue Type] - `file.py:123`
**Problem**: [description]
**Risk**: [what could go wrong]
**Fix**: [how to fix]

### Warnings (N)
### Suggestions (N)
### Pattern Conformance
### Summary
- Critical: N | Warnings: N | Suggestions: N
- Recommendation: APPROVE | REQUEST_CHANGES | NEEDS_DISCUSSION
```

---

### `defensive-reviewer`

**Description**: Deep defensive code review - finds edge cases, null safety issues, error handling gaps. Part of Pass 2 validation.

**Model**: `sonnet`

**Tools**: `Read`, `Grep`, `Glob`

**Scope**: Changed files only

**Budget**: 200-400 lines

**Mindset**: Think like a paranoid developer who has been burned by production incidents.

**What It Looks For**:
- **Null/Undefined Safety**: Missing null checks, unhandled Optional types
- **Boundary Conditions**: Off-by-one, empty collections, zero handling
- **Error Handling Gaps**: Unhandled exceptions, swallowed errors, missing validation
- **Resource Management**: Unclosed files/connections, memory leaks, deadlocks
- **Concurrency Issues**: Race conditions, missing locks, async error handling
- **Data Integrity**: Type mismatches, float precision, encoding issues

**Example Issues**:
```python
# BAD: No null check
user = get_user(id)
print(user.name)  # Crashes if user is None

# BAD: No empty check
total = sum(values) / len(values)  # Divide by zero if empty

# BAD: Resource leak
f = open("file.txt")
data = process(f.read())  # If this raises, file never closes
f.close()
```

---

### `security-reviewer`

**Description**: Deep security review - finds injection vulnerabilities, auth bypasses, data leaks. Part of Pass 2 validation.

**Model**: `sonnet`

**Tools**: `Read`, `Grep`, `Glob`

**Scope**: Changed files only

**Budget**: 200-400 lines

**Mindset**: Think like an attacker.

**What It Looks For**:
- **Injection**: SQL, Command, Path traversal, NoSQL
- **Authentication**: Missing checks, weak tokens, hardcoded credentials
- **Authorization**: IDOR, broken access control, missing permission checks
- **Data Exposure**: Secrets in logs, password hashes in responses
- **Cryptography**: MD5/SHA1 for passwords, hardcoded keys
- **Input Validation**: No sanitization, no file type/size limits
- **XSS**: Unescaped user input in responses
- **Business Logic**: Race conditions, double-spend

**Example Issues**:
```python
# CRITICAL: SQL injection
query = f"SELECT * FROM users WHERE id = {user_id}"

# CRITICAL: Command injection
os.system(f"ls {user_path}")

# CRITICAL: Path traversal
file_path = f"/uploads/{filename}"
# Attacker: filename = "../../etc/passwd"
```

---

### `logic-reviewer`

**Description**: Deep logic review - validates implementation against plan requirements, checks business logic correctness. Part of Pass 2 validation.

**Model**: `sonnet`

**Tools**: `Read`, `Grep`, `Glob`

**Scope**: Changed files + plan artifact (`2X_plan.md`)

**Budget**: 200-400 lines

**Mindset**: Think like a QA engineer and product manager combined.

**What It Looks For**:
- **Requirements Fulfillment**: Are all phases implemented? Success criteria met?
- **Business Logic**: Calculations correct? Conditions correct?
- **Edge Cases**: Boundary values? Empty/null handling?
- **Data Validation**: Rules complete? Errors meaningful?
- **Test Coverage**: New functions tested? Edge cases covered?
- **Feature Completeness**: All CRUD operations? Success and error paths?
- **Logic Errors**: Infinite loops? Unreachable code? Wrong variable?
- **Plan Deviations**: Documented? Justified?

**Example Issues**:
```python
# BAD: Wrong condition
if user.age > 18:  # Should be >= for "18 or older"
    allow_access()

# BAD: Incomplete feature
# Plan says: "Add user management"
# Implementation provides: POST /users only
# MISSING: GET, PUT, DELETE
```

---

### `integration-reviewer`

**Description**: Deep integration review - finds breaking changes, API contract violations, dependency issues. Part of Pass 2 validation.

**Model**: `sonnet`

**Tools**: `Read`, `Grep`, `Glob`

**Scope**: Changed files only

**Budget**: 200-400 lines

**Mindset**: Think like a system architect who understands the entire system.

**What It Looks For**:
- **API Contract Breaking Changes**: Field renames, added required fields, changed types
- **Database Schema Assumptions**: Queries on removed columns, changed relationships
- **Service Dependencies**: Missing fallbacks, hardcoded URLs, undocumented env vars
- **Event/Message Contracts**: Changed payloads, removed events, renamed topics
- **Shared State & Caching**: Cache key changes, invalidation missing
- **Auth Changes**: Made public endpoint require auth, changed permissions
- **Backwards Compatibility**: Removed functions, changed signatures

**Example Issues**:
```python
# BAD: Breaking change - field renamed
class UserResponse(BaseModel):
    user_id: str  # Was: id
    # Clients expecting "id" will break

# BAD: Added required field
class CreateUserRequest(BaseModel):
    phone: str  # NEW REQUIRED - breaks existing clients
```

---

## Distiller Agents

Distillers are used to compress context and analyze codebases without pasting large outputs into chat.

### `microservice-distiller`

**Description**: Documents a microservice as a black-box from root monorepo perspective.

**Model**: `sonnet`

**Tools**: `Grep`, `Glob`, `Read`, `LS`

**Budget**: 200-400 lines

**Purpose**: Create external reference card for a nested repo.

**Output Sections**:
- Purpose (1-2 sentences)
- Public Interfaces (APIs, ports, CLI)
- Integration Points (depends on, consumed by)
- Deploy Surface (Dockerfile, Helm, CI/CD)
- Configuration (required/optional env vars)
- Unknowns

**What NOT to Include**:
- Internal function implementations
- Private class methods
- Test internals
- Algorithm details

---

### `repo-doc-distiller`

**Description**: Produces comprehensive documentation for a repository when invoked from inside that repo.

**Model**: `sonnet`

**Tools**: `Grep`, `Glob`, `Read`, `LS`

**Budget**: 200-400 lines

**Purpose**: Create developer onboarding guide.

**Output Sections**:
- Architecture Overview (diagram, module structure, data flow)
- Entrypoints (startup, routes, jobs, CLI)
- Conventions (code style, naming, file organization)
- Golden Paths (how to add endpoint, service, etc.)
- Test Strategy (structure, running, coverage, mocking)
- Key Risks/Gotchas
- Dependencies (internal, external)

**Focus**: "How do I get things done in this repo?"

---

### `codebase-analyzer`

**Description**: Analyzes codebase implementation details.

**Model**: `sonnet`

**Tools**: `Read`, `Grep`, `Glob`, `LS`

**Budget**: 200-600 lines

**Purpose**: Explain HOW code works with file:line references.

**Process**:
1. Read entry points
2. Follow code paths step by step
3. Document key logic

**Output Format**:
```markdown
## Analysis: [Feature/Component]

### Overview
### Entry Points
### Core Implementation
#### 1. Request Validation (`file.py:15-32`)
### Data Flow
### Key Patterns
### Configuration
### Error Handling
```

**CRITICAL**: Document only - never critique, suggest improvements, or identify problems.

---

### `codebase-locator`

**Description**: Locates files, directories, and components relevant to a feature or task.

**Model**: `sonnet`

**Tools**: `Grep`, `Glob`, `LS`

**Budget**: 100-300 lines

**Purpose**: Find WHERE code lives, not what it does.

**Output Format**:
```markdown
## File Locations for [Feature]

### Implementation Files
- `src/services/feature.js` - Main service logic

### Test Files
- `tests/feature.test.js` - Service tests

### Configuration
- `config/feature.json` - Feature config

### Related Directories
- `src/services/feature/` - Contains 5 related files
```

**Do NOT**: Read file contents, analyze implementation, make recommendations.

---

### `codebase-pattern-finder`

**Description**: Finds similar implementations, usage examples, or existing patterns.

**Model**: `sonnet`

**Tools**: `Grep`, `Glob`, `Read`, `LS`

**Budget**: 200-600 lines

**Purpose**: Catalog existing patterns with code snippets.

**Output Format**:
```markdown
## Pattern Examples: [Pattern Type]

### Pattern 1: [Descriptive Name]
**Found in**: `src/api/users.js:45-67`
**Used for**: User listing with pagination

```javascript
// Actual code from codebase
```

**Key aspects**:
- Uses query parameters for page/limit
- Returns pagination metadata

### Testing Patterns
### Related Utilities
```

**Show 2-3 examples per pattern, not exhaustive lists.**

---

### `code-simplifier`

**Description**: Reviews edited code to make it cleaner without breaking functionality.

**Model**: `sonnet`

**Tools**: `Read`, `Grep`, `Glob`, `Edit`

**Budget**: 200-600 lines

**Scope**: Changed files only

**What It Simplifies**:
- Verbose conditionals → concise expressions
- Unnecessary intermediate variables
- Loops → comprehensions (when clearer)
- Nested ifs → early returns
- String concat → f-strings
- Dictionary operations

**What It Protects**:
- Error handling
- Type annotations
- Public APIs
- Performance-critical code
- Intentionally verbose code

**Output Format**:
```markdown
## Code Simplification Review

### File: `path/to/file.py`

#### 1. Lines 45-52: Simplify conditional
**Current**: [code]
**Suggested**: [code]
**Why**: Reduces 8 lines to 1
**Risk**: None - pure refactor

### Summary
- Simplifications: N
- Line reduction: X lines
- Risk level: Low
```

---

### `web-search-researcher`

**Description**: Web research specialist for finding up-to-date information.

**Model**: `sonnet`

**Tools**: `WebSearch`, `WebFetch`, `TodoWrite`, `Read`, `Grep`, `Glob`, `LS`

**Purpose**: Research external documentation, best practices, solutions.

**Search Strategies**:
- **API/Library Docs**: Official docs first, changelog for versions
- **Best Practices**: Recent articles, recognized experts
- **Technical Solutions**: Error messages in quotes, Stack Overflow, GitHub issues
- **Comparisons**: "X vs Y", migration guides, benchmarks

**Output Format**:
```markdown
## Summary
[Brief overview]

## Detailed Findings

### [Source 1]
**Source**: [Name with link]
**Relevance**: [Why authoritative]
**Key Information**: [findings]

## Additional Resources
## Gaps or Limitations
```

---

## Agent Usage in RPIV

### Research Phase (`/rpiv_research`)
- `microservice-distiller` - Black-box docs for nested repos
- `codebase-locator` - Find relevant files
- `codebase-pattern-finder` - Find similar implementations
- `repo-doc-distiller` - Internal docs (if inside microservice)
- `codebase-analyzer` - Analyze specific components

### Validation Phase (`/rpiv_validate`)

**Pass 1** (always):
- `code-reviewer` - General code review

**Pass 2** (on critical issues, run in parallel):
- `defensive-reviewer` - Edge cases, null safety
- `integration-reviewer` - API contracts, breaking changes
- `security-reviewer` - Vulnerabilities, exploits
- `logic-reviewer` - Requirements vs implementation

### Other Commands
- `/simplify` → `code-simplifier`
- `/review` → `codebase-analyzer` + `codebase-pattern-finder`
- `/research_codebase` → `codebase-locator` + `codebase-analyzer` + `codebase-pattern-finder`
