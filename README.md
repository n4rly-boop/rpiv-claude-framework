# Claude Code Harness

Controlled development pipeline for everyday feature work with Claude Code.

## Architecture

```
/dev "task"
    ↓
Planner → plan.md
    ↓
[YOU REVIEW plan.md]
    ↓
Generator + Evaluator(criteria) → code + eval_criteria.md
    ↓
Evaluator → verify + code-review
    ↓
PASS or fix loop (×2) or escalate to you
```

## Quick Start

### 1. Copy `.claude/` to your project

```bash
cp -r .claude/ /your/project/.claude/
cp -r .harness/ /your/project/.harness/
```

### 2. Fill in knowledge files

Edit `.harness/PATTERNS.md` — add your project's recurring code patterns.
Edit `.harness/CONVENTIONS.md` — add your naming and style rules.
Edit `.harness/git.md` — define your commit strategy.

### 3. Run

```bash
# Full pipeline
claude /dev "add endpoint to update user profile"

# Plan only (review before generating)
claude /plan "refactor auth middleware"

# Check current code
claude /evaluate

# Session status
claude /status
```

## Agent Tree

| Agent | Model | Role |
|-------|-------|------|
| planner | opus | Reads task + codebase → writes plan.md |
| generator | opus | Reads plan → writes code |
| evaluator | opus | Phase 1: writes criteria. Phase 2: verifies code |
| codebase-distiller | sonnet | Spawned by planner. Finds relevant files + patterns |
| code-reviewer | sonnet | Spawned by evaluator. Strict pattern/convention check |
| web-researcher | sonnet | Spawned by generator. External docs/API lookup |
| deep-codebase-probe | sonnet | Spawned by generator. Deep module analysis |

## Session Files

Each session creates `.harness/sessions/{YYYYMMDD-HHMMSS-slug}/`:

| File | Written by |
|------|-----------|
| `plan.md` | Planner |
| `eval_criteria.md` | Evaluator phase 1 |
| `planner_1.md` | Planner handoff |
| `generator_N.md` | Generator handoff |
| `evaluator_N.md` | Evaluator handoff |

## Commands

| Command | Description |
|---------|-------------|
| `/dev "task"` | Full pipeline |
| `/dev "task" --fast` | Skip code review |
| `/dev "task" --plan-only` | Plan only, stop at review |
| `/dev --resume` | Continue most recent session |
| `/plan "task"` | Plan only |
| `/evaluate` | Evaluate current git state |
| `/status` | Show session state |

## Design Principles

1. Every harness component = an explicit assumption about model weakness
2. Flat files + git = sufficient memory for everyday dev
3. One USER GATE — after plan.md. Everything else runs autonomously
4. Evaluator derives criteria independently (eliminates self-evaluation bias)
5. Each main agent manages its own sub-agents (generator spawns web-researcher directly)
6. Handoffs are the only cross-session memory — orchestrator passes them explicitly
