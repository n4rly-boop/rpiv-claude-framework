---
description: Full pre-PR checklist - format, check, test, simplify
---

# PR Ready Check

Run complete pre-PR checklist to ensure code is ready for review.

## Process

Execute in order:

1. **Format**: `/tooling format`
2. **Check**: `/tooling check` — if fails, fix type/lint errors, re-run format + check
3. **Test**: `/tooling test` — if fails, analyze and fix without breaking other tests, re-run
4. **Simplify**: Launch `code-simplifier` agent on changed files (`git diff --name-only HEAD~1`)
5. **Final verification**: `/tooling format` → `/tooling check` → `/tooling test`

## Output

```
## PR Readiness Report

### Format: pass/fail
### Lint & Types: pass/fail
### Tests: pass/fail (Passed: N, Failed: N)
### Code Quality: Simplifications applied: N, Lines changed: +X/-Y

### Status: READY / NEEDS WORK

[If ready] Run `/commit` or `/describe_pr`
[If needs work] Fix: <issues>
```
