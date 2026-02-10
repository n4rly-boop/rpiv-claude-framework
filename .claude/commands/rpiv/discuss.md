---
description: RPIV Discussion phase - facilitate decision-making and record outcomes to vault
model: opus
---

# RPIV Discussion Phase

Facilitate structured discussion and record decisions to vault.

## Process

### Step 1: Load Session Context

1. **Find active session** from `$VAULT_BASE/<repo_name>/sessions/`

2. **Determine discussion context**:
   ```
   IF --after provided:
       CONTEXT = specified phase
   ELSE:
       # Auto-detect from latest artifact
       CHECK for artifacts in order: 4X, 3X, 2X, 1X, 00
       CONTEXT = phase of latest artifact found
   ```

3. **Read relevant artifacts**:
   - Latest artifact from detected phase
   - 00_context.md for task description
   - Any previous discussion artifacts (DXX_*.md)

### Step 2: Present Summary to User

Present a concise summary (max 20 lines) of current state:

```markdown
## Current State

**Task**: <from 00_context.md>
**Phase**: <detected phase>
**Latest Artifact**: <artifact name>

### Key Points from <Latest Artifact>
- <point 1>
- <point 2>
- <point 3>

### Decision Points Identified
- <decision 1>
- <decision 2>

### Open Questions (if any)
- <question from research/plan>
```

### Step 3: Facilitate Discussion

Use `AskUserQuestion` tool to gather input:

1. **Present options** if applicable:
   ```
   Based on the research, there are N approaches:

   A) <Approach A> - <1-line description>
   B) <Approach B> - <1-line description>

   Which approach should we pursue?
   ```

2. **Ask clarifying questions**:
   - What constraints should I consider?
   - What's the priority: speed, maintainability, performance?
   - Any preferences on technology/patterns?

3. **Confirm understanding**:
   - Summarize what was decided
   - Ask if anything was missed

### Step 4: Determine Next Artifact Version

```bash
# Find existing discussion artifacts
EXISTING=$(ls -1 $SESSION_PATH/D??_*.md 2>/dev/null | sort -V | tail -1)
if [ -z "$EXISTING" ]; then
    NEXT_NUM="01"
else
    CURRENT_NUM=$(basename "$EXISTING" | grep -o 'D[0-9]*' | tr -d 'D')
    NEXT_NUM=$(printf "%02d" $((10#$CURRENT_NUM + 1)))
fi

# Determine topic name
IF --topic provided:
    TOPIC = sanitize(--topic)  # lowercase, hyphens
ELSE:
    TOPIC = default based on context:
        after context → "scope"
        after research → "approach"
        after plan → "design"
        after implement → "review"
        after validation → "retrospective"

NEXT_VERSION="D${NEXT_NUM}_${TOPIC}.md"
```

### Step 5: Write Discussion Artifact

Use `obsidian` MCP to write `$NEXT_VERSION`:

```markdown
---
repo: <repo_name>
session: <session_id>
type: discussion
topic: <topic>
phase_after: <context|research|plan|implement|validate>
created: <iso8601>
sources:
  - <preceding_artifact>
  - <other_artifacts_referenced>
---

# Discussion: <Topic Title>

## Context

**Task**: <task description>
**Trigger**: <what prompted this discussion>
**Preceding Artifact**: [<artifact>](./<artifact>)

## Summary

[2-3 sentences: what was discussed and decided]

## Options Considered

### Option A: <Name>

**Description**: [1-2 sentences]

**Pros**:
- <pro 1>
- <pro 2>

**Cons**:
- <con 1>
- <con 2>

**Effort**: Low | Medium | High
**Risk**: Low | Medium | High

### Option B: <Name>

[Same structure]

### Option C: <Name> (if applicable)

[Same structure]

## Decision

**Chosen**: <Option X>

**Reasoning**:
<User's reasoning captured from discussion. This is the most valuable part -
WHY was this decision made? What trade-offs were accepted?>

**Trade-offs Accepted**:
- <What we're giving up by choosing this option>
- <Risks we're accepting>

## Impact on Next Phase

<How this decision affects the upcoming work>

- **For Planning**: <constraints, patterns to follow, scope changes>
- **For Implementation**: <specific approaches, libraries, patterns>
- **For Validation**: <what to test, success criteria>

## Action Items

- [ ] <Specific next step>
- [ ] <Specific next step>

## Open Items (Deferred)

- [ ] <Things to revisit later>
- [ ] <Questions that don't block progress>
```

**Budget**: 300-500 lines max. Focus on decisions and reasoning, not exhaustive details.

### Step 6: Check for Re-Research Trigger

If during discussion, user requests deeper investigation:

```
IF user says "I want to explore X more" or "Can you research Y":
    SUGGEST: "Would you like me to run `/rpiv_research --focus \"<topic>\"`
              to gather more information before we continue?"

    IF user confirms:
        NOTE in discussion artifact: "Research requested on <topic>"
        END discussion
        SUGGEST: /rpiv_research --focus "<topic>"
```

### Step 7: Update Session Index

**Add to Progress table** (discussions get their own row):

```markdown
| Discussion | complete | [D01_scope.md](./D01_scope.md) | <timestamp> |
```

**Add to Artifacts section**:

```markdown
- [D01_scope.md](./D01_scope.md) - Scoping discussion
```

**Add to Timeline**:

```markdown
| <timestamp> | Discussion completed (D01_scope.md) - decided on <key decision> |
```

### Step 8: Report

```
## RPIV Discussion Complete

Created:
- $VAULT_BASE/<repo>/sessions/<session_id>/$NEXT_VERSION

Key Decisions:
- <decision 1>
- <decision 2>

Impact:
- <how this affects next phase>

Next: <suggested next command based on context>
  - After scope discussion → /rpiv_research
  - After approach discussion → /rpiv_plan
  - After design discussion → /rpiv_implement
  - After retrospective → /rpiv_plan (new iteration)
```

