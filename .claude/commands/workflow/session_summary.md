---
description: Summarize RPIV session artifacts and produce an empirical verification playbook (manual checks, routes, curl)
model: opus
---

# Session Summary + Empirical Verification Playbook

Create a durable summary artifact answering: What was done? What changed? How to verify empirically?

**"How to test" means MANUAL/EMPIRICAL verification** — API routes, curl commands, expected responses, observable side effects (logs, DB, cache, metrics). Not CI.

## Process

### Step 1: Resolve Session

Repo: `basename $(git rev-parse --show-toplevel)`. Session: `--session` arg or most recent in `$VAULT_BASE/$REPO_NAME/sessions/`. Baseline commit: from `00_context.md`, fallback `HEAD~1`, override via `--since`.

### Step 2: Load Artifacts (best-effort)

Read latest versioned artifacts: `00_context.md`, `index.md`, latest `1?_research.md`, `2?_plan.md`, `3?_implementation.md`, `4?_validation.md`. List extra files including previous versions.

### Step 3: Summarize Code Changes

```bash
git diff --name-only <BASE>..HEAD
git diff --stat <BASE>..HEAD
git log --oneline <BASE>..HEAD
git status --porcelain
```

### Step 4: Build Verification Playbook

Priority order for deriving manual verification steps:

**A) Explicit acceptance criteria** (highest) — reuse verbatim from plan/impl/validation artifacts
**B) Infer from code** — scan changed files for route definitions (FastAPI, Express, etc.), extract METHOD + PATH + request model + auth deps
**C) OpenAPI discovery** — fetch `/openapi.json` if service runs locally, match changed routes
**D) Construct manual script** — per feature: route, curl command, expected response, negative case, side effects + how to observe

### Step 5: Build Future Work Section

Analyze implementation for: integration guidance, key files/patterns to reference, known limitations, recommended next steps, stable knowledge updates.

### Step 6: Write Summary Artifact

Write `50_session_summary.md` via `obsidian` MCP.

**Frontmatter**: `repo`, `session`, `baseline_ref`, `target_ref: HEAD`, `type: session_summary`, `created`.

**Body sections:**
- **Task**: from context
- **Status**: Research/Plan/Implementation/Validation status + verdict
- **What changed**: commits, files, stats
- **Key decisions**: from plan/implementation
- **Empirical verification playbook**: Preconditions (env vars, auth), service start command, per-feature verification (route, curl, expected response, side effects, negative case)
- **Future Work & Integration**: context for next session, integration points, known limitations/TODOs, recommended next steps, stable knowledge updates
- **Validation notes**: from latest validation
- **Links**: to all session artifacts (note versioning scheme)

### Step 7: Update Index & Report

Add link to `50_session_summary.md` in index. Print path + short digest (max 15 lines).
