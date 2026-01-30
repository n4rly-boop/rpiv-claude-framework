---
description: Full pre-PR checklist - format, check, test, simplify
---

# PR Ready Check

Run the complete pre-PR checklist to ensure code is ready for review.

## Process

Execute in order:

### 1. Format Code
```bash
make format
```

### 2. Run Checks
```bash
make check
```

If checks fail:
- Fix type errors
- Fix linting issues
- Re-run format and check

### 3. Run Tests
```bash
make tests
```

If tests fail:
- Analyze failures
- Fix without breaking other tests
- Re-run

### 4. Review for Simplification
Launch code-simplifier agent on changed files:
```bash
git diff --name-only HEAD~1
```

### 5. Final Verification
```bash
make format && make check && make tests
```

## Output

```markdown
## PR Readiness Report

### Format: ✓/✗
[Details if failed]

### Lint & Types: ✓/✗
[Details if failed]

### Tests: ✓/✗
- Passed: N
- Failed: N (with details)

### Code Quality
- Simplifications applied: N
- Lines changed: +X/-Y

### Status: READY / NEEDS WORK

[If ready]
You can now run `/commit` or `/describe_pr`

[If needs work]
Fix these issues:
1. ...
2. ...
```
