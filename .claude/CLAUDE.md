# Claude Code Harness

Controlled development pipeline: Planner → Generator → Evaluator.

## Pipeline

```
/dev "task"
    ↓
Planner (reads codebase context)
    → writes .harness/sessions/{id}/plan.md
    ↓
[USER GATE — review and edit plan.md]
    ↓
Evaluator phase 1          Generator
(plan.md[What]             (plan.md[How]
→ eval_criteria.md)        → writes code)
    ↓ wait for generator
Evaluator phase 2
(eval_criteria.md + diff + tests + code-reviewer)
    ↓
PASS → done
FAIL → fix loop (max 2) → USER GATE if still failing
BLOCKED → USER GATE immediately
```

## Session Files

All session state lives in `.harness/sessions/{YYYYMMDD-HHMMSS-slug}/`:

| File | Written by | Purpose |
|------|-----------|---------|
| `plan.md` | Planner | What to build + technical direction |
| `eval_criteria.md` | Evaluator | Verification criteria (from plan[What]) |
| `planner_1.md` | Planner | Handoff on completion/block |
| `generator_N.md` | Generator | Handoff on completion/block |
| `evaluator_N.md` | Evaluator | Handoff if needed |

## Knowledge Files

Maintain these in `.harness/`:

| File | Purpose |
|------|---------|
| `PATTERNS.md` | Reusable code patterns with examples |
| `CONVENTIONS.md` | Hard naming/style rules |
| `git.md` | Commit strategy for this project |

## Core Rules

1. **Planner** — business + technical direction only. Never specifies implementation details.
2. **Generator** — implements ONLY what plan.md[How] says. No scope creep.
3. **Evaluator** — derives eval_criteria.md from plan.md[What] independently. Never from generator output.
4. **Handoffs** — every main agent writes `{agent}_N.md` on completion or block. Orchestrator passes them.
5. **USER GATEs** — mandatory after plan.md. Mandatory on BLOCKED. Mandatory on FAIL×2.
6. **Sub-agents** — each main agent manages its own. Results logged in handoff.

## Commands

| Command | What it does |
|---------|-------------|
| `/dev "task"` | Full pipeline |
| `/plan "task"` | Planning only, stops at USER GATE |
| `/evaluate` | Run evaluator on current git state |
| `/status` | Show current session state |

## Prohibited

- Running `/dev` without letting user review plan.md
- Generator writing eval_criteria.md
- Proceeding past a BLOCKED status without user input
- Pasting >50 lines of code in chat
- Accessing .env files (enforced by hook)
