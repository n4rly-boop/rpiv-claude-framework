---
description: Summarize RPIV session artifacts and produce an empirical verification playbook (manual checks, routes, curl)
model: opus
---

# Session Summary + Empirical Verification Playbook

Create a single durable summary artifact for an RPIV session that answers:
- What was done?
- What changed?
- How can the change be verified empirically (not tests/linting)?

## Definition of "How to test"
This command MUST produce **manual / empirical verification steps**, not CI.
Examples:
- which API route to call
- curl/httpie commands
- expected response
- observable side effects (logs, DB, cache, metrics)

## Process

### Step 1: Resolve repo + session

```bash
REPO_ROOT=$(git rev-parse --show-toplevel)
REPO_NAME=$(basename "$REPO_ROOT")
```

Session resolution:

* If `--session` provided → use it
* Else → use most recently modified folder under:
  `$VAULT_BASE/$REPO_NAME/sessions/`

Baseline commit:

* Prefer commit recorded in `00_context.md`
* Else fallback to `HEAD~1`
* Overrideable via `--since`

### Step 2: Load session artifacts (best-effort)

Find and read latest versioned artifacts:
```bash
# Artifacts are versioned: 1X_research, 2X_plan, 3X_implementation, 4X_validation
LATEST_RESEARCH=$(ls -1 $SESSION_PATH/1?_research.md 2>/dev/null | sort -V | tail -1)
LATEST_PLAN=$(ls -1 $SESSION_PATH/2?_plan.md 2>/dev/null | sort -V | tail -1)
LATEST_IMPL=$(ls -1 $SESSION_PATH/3?_implementation.md 2>/dev/null | sort -V | tail -1)
LATEST_VALID=$(ls -1 $SESSION_PATH/4?_validation.md 2>/dev/null | sort -V | tail -1)
```

Attempt to read:
* `00_context.md` (not versioned)
* `index.md`
* `$LATEST_RESEARCH`
* `$LATEST_PLAN`
* `$LATEST_IMPL`
* `$LATEST_VALID`

Also list any extra files in the session directory (including previous artifact versions).

### Step 3: Summarize code changes

Compute:

```bash
git diff --name-only <BASE_REF>..HEAD
git diff --stat <BASE_REF>..HEAD
git log --oneline <BASE_REF>..HEAD
git status --porcelain
```

### Step 4: Build empirical verification playbook

Derive manual verification steps using this priority:

#### A) Explicit acceptance criteria (highest priority)

Extract from:

* `$LATEST_PLAN` → "Acceptance Criteria", "Manual verification"
* `$LATEST_IMPL` → routes, flags, handlers
* `$LATEST_VALID` → manual checks

Reuse verbatim if present.

#### B) Infer from FastAPI code (if A insufficient)

If Python/FastAPI:

* Find changed files containing:

  * `FastAPI(`, `APIRouter(`, `@router.`, `add_api_route`
* Extract:

  * METHOD + PATH
  * request model (if named)
  * auth dependencies (best-effort)

#### C) OpenAPI discovery (best-effort)

If service can run locally:

* Fetch `/openapi.json`
* Match changed routes

#### D) Construct manual script

For each feature/endpoint:

* route
* example curl
* expected response
* negative case
* side effects + how to observe

### E) Build Future Work section

Analyze the implementation to identify:

* **Integration guidance**: How future work can build upon this
* **Key files and patterns**: What files/functions to reference
* **Known limitations**: What wasn't implemented and why
* **Recommended next steps**: Logical extensions or improvements
* **Stable knowledge updates**: What was added to `knowledge/` directory

This section helps future sessions (or other developers) understand:
- How to extend the feature
- What patterns to follow
- What technical debt exists
- What the natural next steps are

### Step 5: Write summary artifact

Write:
`$VAULT_BASE/$REPO_NAME/sessions/<session_id>/50_session_summary.md`

Template:

```markdown
---
repo: <repo_name>
session: <session_id>
baseline_ref: <BASE_REF>
target_ref: HEAD
type: session_summary
created: <iso8601>
---

# Session Summary: <session_id>

## Task
<from 00_context.md>

## Status
- Research: <done/partial/unknown>
- Plan: <done/partial/unknown>
- Implementation: <done/partial/unknown>
- Validation: <done/partial/unknown>
- Verdict: <ready / needs work>

## What changed
**Commits**
- <git log>

**Files**
- <git diff --name-only>

**Stats**
- <git diff --stat>

## Key decisions
- <from plan / implementation>

## Empirical verification playbook

### Preconditions
- Environment: <local/dev>
- Required env vars:
  - <KEY>=<value or placeholder>
- Auth:
  - <how to obtain token or placeholder>

### Start the service
```bash
<command or "not specified">
```

### Verify behavior

#### 1) <Feature or endpoint name>

**Route**

* <METHOD> <PATH>

**Request**

```bash
curl -i -X <METHOD> "http://localhost:<port><PATH>" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '<JSON>'
```

**Expected**

* Status: <code>
* Response: <key fields>
* Side effects: <what should change>

**Observe side effects**

* Logs: <pattern or unknown>
* DB: <query or unknown>
* Cache / events / metrics: <if applicable>

**Negative case**

```bash
<curl with invalid input or missing auth>
```

Expected: <status + error>

## Future Work & Integration

### How to Build Upon This Work

**Context for Next Session**:
* What was implemented: <brief summary>
* Key files modified: <list>
* Patterns established: <any new patterns to follow>

**Integration Points**:
* To extend this feature:
  - Relevant files: <paths>
  - Key functions/classes: <names>
  - Convention to follow: <pattern reference>

* To integrate with other services:
  - API contract: <reference to endpoint/schema>
  - Data models: <relevant models>
  - Shared utilities: <if any>

**Known Limitations & TODOs**:
- [ ] <limitation 1 - e.g., "No pagination support yet">
- [ ] <limitation 2 - e.g., "Error handling for edge case X">
- [ ] <improvement idea>

**Recommended Next Steps**:
1. <logical next feature or improvement>
2. <technical debt to address>
3. <optimization opportunity>

### Stable Knowledge Updates

**Created/Updated**:
* `knowledge/patterns/<pattern>.md` - <if new pattern established>
* `knowledge/conventions/<area>.md` - <if convention added>
* `knowledge/services/<service>.md` - <if service documented>

## Validation notes

* <summary from $LATEST_VALID>

## Links

* [00_context.md](./00_context.md)
* [$LATEST_RESEARCH](./$LATEST_RESEARCH)
* [$LATEST_PLAN](./$LATEST_PLAN)
* [$LATEST_IMPL](./$LATEST_IMPL)
* [$LATEST_VALID](./$LATEST_VALID)

**Note**: Artifacts are versioned (10, 11, 12... for research; 20, 21, 22... for plan; etc.). Links above point to latest versions. Previous iterations are preserved in the session folder.

```

### Step 6: Update index.md
Add link to `50_session_summary.md`.

### Step 7: Output
Print:
- path to summary
- short digest (≤15 lines)