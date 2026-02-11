---
description: Document codebase as-is comprehensively
model: opus
---

# Research Codebase

Conduct comprehensive codebase research to answer user questions by spawning parallel agents and synthesizing findings.

## Constraint: Document Only

YOUR ONLY JOB IS TO DOCUMENT AND EXPLAIN THE CODEBASE AS IT EXISTS TODAY.
- DO NOT suggest improvements, critique implementation, or recommend changes
- DO NOT perform root cause analysis unless explicitly asked
- ONLY describe what exists, where, how it works, and how components interact
- You are creating a technical map of the existing system

## Initial Response

Respond: "I'm ready to research the codebase. Please provide your research question or area of interest."

Then wait for the user's query.

## Process

### Step 1: Read Mentioned Files
If user mentions specific files, read them FULLY in main context before decomposing research.

### Step 2: Decompose & Plan
Break query into composable research areas. Create research plan via TodoWrite. Identify relevant components, patterns, directories.

### Step 3: Spawn Parallel Agents

**Codebase research agents:**
- `codebase-locator` → find WHERE files/components live
- `codebase-analyzer` → understand HOW code works (document, don't critique)
- `codebase-pattern-finder` → find examples of existing patterns

**Web research** (only if user asks): `web-search-researcher` — include returned links in final report.

Strategy: Start with locator agents, then analyzer on promising findings. Run multiple in parallel when searching different areas. Remind agents they are documenting, not evaluating.

### Step 4: Synthesize

Wait for ALL agents. Compile results, connect cross-component findings, include `file:line` references, highlight patterns and architectural decisions.

### Step 5: Write Research Document

Via `obsidian` MCP:
- RPIV session: `{repo_name}/sessions/<session_id>/1X_research.md`
- Standalone: `{repo_name}/research/YYYY-MM-DD-description.md`

**Frontmatter**: date, git_commit, branch, repository, topic, tags, status, last_updated.

**Body**: Research Question, Summary, Detailed Findings (per component with `file:line` refs), Code References, Architecture Documentation, Related Research, Open Questions.

### Step 6: GitHub Permalinks (if applicable)
If on main/pushed branch, replace local refs with `https://github.com/{owner}/{repo}/blob/{commit}/{file}#L{line}`.

### Step 7: Present & Follow Up
Present concise summary with key file references. For follow-ups, append to same document with `## Follow-up Research [timestamp]` section.
