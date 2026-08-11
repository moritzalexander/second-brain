---
name: daily-wrapup
description: Synthesize new Second Brain intelligence into a concise project-organized daily digest and flag project-health issues.
---

# Daily wrap-up

Work in `{VAULT_ROOT}`. Read `AGENTS.md`, today's processed intelligence, and relevant active project hubs.

## Method

1. Gather every processed intelligence record whose event date is today.
2. Verify that the intelligence sync completed or clearly mark partial coverage.
3. Group evidence by existing project or durable topic.
4. Lead with decisions, changes, escalations, owners, and dates.
5. Add source wiki-links close to the claims they support.
6. Flag stale projects, missing hubs, conflicting status, or scope drift.
7. Write `daily/YYYY-MM-DD.md` without replacing existing manual content.

## Output

```markdown
# YYYY-MM-DD

## Summary
Two or three sentences on what changed and what matters.

## By Project

### Project name
- Decision or development
- Source: [[intelligence/...]]

## Cross-Cutting
- ...

## Project Health
- ...

## Open Items
- [ ] Task -> Owner
```

Keep it readable in three to five minutes. Do not turn every source detail into a task.
