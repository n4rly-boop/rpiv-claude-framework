# Claude Code Harness

Controlled development pipeline for everyday feature work with Claude Code.
Planner → Generator → Evaluator, with one mandatory user review gate.

## Architecture

```
/dev "task"
    ↓
Planner (codebase-distiller)
    → plan.md: What (observable behavior) + How (technical direction)
    ↓
[YOU REVIEW + EDIT plan.md]
    ↓
Evaluator phase 1          Generator (web-researcher, deep-codebase-probe)
plan.md[What]              plan.md[How]
→ eval_criteria.md         → code commits
    ↓
Evaluator phase 2 (code-reviewer)
eval_criteria.md + git diff + tests
    ↓
PASS → done
FAIL → fix loop (max ×2) → escalate to you
BLOCKED → escalate to you immediately
```

## Quick Start

### 1. Copy `.claude/` to your project

```bash
cp -r .claude/ /your/project/.claude/
```

### 2. Initialize vault for your repo

```bash
REPO=$(basename $(git rev-parse --show-toplevel))
mkdir -p ~/context_vault/$REPO/sessions
touch ~/context_vault/$REPO/PATTERNS.md
touch ~/context_vault/$REPO/CONVENTIONS.md
touch ~/context_vault/$REPO/git.md
touch ~/context_vault/$REPO/decisions.md
```

### 3. Fill in knowledge files

`~/context_vault/$REPO/PATTERNS.md` — recurring code patterns with file:line examples  
`~/context_vault/$REPO/CONVENTIONS.md` — naming, error handling, import order rules  
`~/context_vault/$REPO/git.md` — commit strategy (types, message format, branch rules)  
`~/context_vault/$REPO/decisions.md` — non-derivable knowledge (why decisions were made, rejected alternatives, landmines, external constraints)

### 4. Set env var

Add to your shell profile or `settings.json`:
```bash
export CONTEXT_VAULT=$HOME/context_vault
```

### 5. Run

```bash
# Full pipeline
claude /dev "add endpoint to update user profile"

# Plan only (review before generating)
claude /plan "refactor auth middleware"

# Check current code against last session criteria
claude /evaluate

# Session status
claude /status
```

## Vault Structure

All harness artifacts live outside the repo — no noise in git history:

```
~/context_vault/{repo}/
├── PATTERNS.md       ← recurring code patterns
├── CONVENTIONS.md    ← naming and style rules
├── git.md            ← commit strategy
├── decisions.md      ← why decisions were made, landmines, constraints
└── sessions/
    └── {YYYYMMDD-HHMMSS-slug}/
        ├── plan.md
        ├── eval_criteria.md
        ├── planner_1.md
        ├── generator_N.md
        └── evaluator_N.md
```

### decisions.md format

```markdown
## {topic or module} — {YYYY-MM-DD}

**Decision:** what was chosen and why
**Rejected:** alternatives considered and why they were dropped
**Constraints:** external constraints — clients, compliance, SLAs
**Landmines:** don't touch X without reading Y — subtle bugs, race conditions
```

## Agent Tree

| Agent | Model | Role |
|-------|-------|------|
| planner | opus | Reads task + codebase context → writes plan.md |
| generator | opus | Reads plan → implements code, commits |
| evaluator | opus | Phase 1: writes eval criteria. Phase 2: verifies |
| codebase-distiller | sonnet | Spawned by planner. Finds relevant files + patterns |
| code-reviewer | sonnet | Spawned by evaluator. Strict pattern/convention check |
| web-researcher | sonnet | Spawned by generator. External docs/API lookup |
| deep-codebase-probe | sonnet | Spawned by generator. Deep module analysis |

## Commands

| Command | Description |
|---------|-------------|
| `/dev "task"` | Full pipeline |
| `/dev "task" --fast` | Skip evaluator phase 2 |
| `/dev "task" --plan-only` | Stop after plan review |
| `/dev --resume` | Continue most recent session |
| `/plan "task"` | Planning only |
| `/evaluate` | Evaluate current git state |
| `/status` | Show session state |

## Design Principles

1. **One USER GATE** — after plan.md. Everything else runs autonomously.
2. **Evaluator is independent** — derives criteria from plan.md[What], never from generator. Eliminates self-evaluation bias.
3. **plan.md has two sections** — What (observable behavior, no implementation details) + How (technical direction, no code).
4. **Flat files + git** — sufficient memory for everyday dev. No database, no vector store.
5. **Each component = an explicit assumption about model weakness** — remove what no longer applies.
6. **decisions.md** — captures what code can't tell you: the why, the rejected paths, the traps.
