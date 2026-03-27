# Claude Code Harness

Controlled development pipeline: Planner → Generator → Evaluator.

## Storage

All harness data lives outside the repo in `CONTEXT_VAULT/{repo_name}/`:

```
CONTEXT_VAULT/{repo_name}/
├── PATTERNS.md        ← reusable code patterns (fill in once)
├── CONVENTIONS.md     ← hard naming/style rules (fill in once)
├── git.md             ← commit strategy (fill in once)
└── sessions/
    └── {YYYYMMDD-HHMMSS-slug}/
        ├── plan.md
        ├── eval_criteria.md
        ├── planner_1.md
        ├── generator_N.md
        └── evaluator_N.md
```

Env var: `CONTEXT_VAULT=$HOME/context_vault` (set in settings.json).

## Pipeline

```
/dev "task"
    ↓
Planner (reads codebase + vault knowledge)
    → writes sessions/{id}/plan.md
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

| File | Written by | Purpose |
|------|-----------|---------|
| `plan.md` | Planner | What to build + technical direction |
| `eval_criteria.md` | Evaluator | Verification criteria from plan[What] |
| `planner_1.md` | Planner | Handoff on completion |
| `generator_N.md` | Generator | Handoff on completion/block |
| `evaluator_N.md` | Evaluator | Verdict + issues |

## Core Rules

1. **Planner** — direction only. Never specifies implementation details.
2. **Generator** — implements ONLY what plan.md[How] says. No scope creep.
3. **Evaluator** — derives eval_criteria.md from plan.md[What] independently.
4. **Handoffs** — every main agent writes `{agent}_N.md` on completion or block.
5. **USER GATEs** — mandatory after plan.md, on BLOCKED, on FAIL×2.
6. **Sub-agents** — each main agent manages its own.

## Commands

| Command | What it does |
|---------|-------------|
| `/dev "task"` | Full pipeline |
| `/plan "task"` | Planning only |
| `/evaluate` | Run evaluator on current git state |
| `/status` | Show current session state |

## Prohibited

- Running generator before user reviews plan.md
- Generator writing eval_criteria.md
- Proceeding past BLOCKED without user input
- Accessing .env files (enforced by hook)
