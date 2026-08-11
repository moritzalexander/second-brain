# Obsidian weekly Kanban

The weekly view uses the Tasks and Task List Kanban community plugins. Tasks remain plain Markdown, so completion state, links, and history survive outside the visual board.

## Data contract

Every root card has exactly one project tag and one weekday tag:

```markdown
- [ ] Prepare account review #plan/project/Account-Planning #plan/day/mon
  - [Account brief](../projects/account-planning.md)
```

The optional `#weekly-starred` tag marks a priority card. Completed or cancelled root cards are not carried into the next week. Open child tasks under a resolved parent are promoted and carried.

## Optional UI behavior

The current workflow benefits from these Task List Kanban extensions:

- responsive columns that use the available viewport width
- project-row colors instead of colored weekday headers
- project add, rename, reorder, and color controls
- click on unused cell space to create a card
- compact link pills inside cards
- a star action that darkens the card using its project color and switches text to white
- automatic removal of `#weekly-starred` when a task is completed
- completed cards remain visible with strikethrough rather than being deleted

These behaviors require plugin-version-specific code. This repository documents the contract but does not redistribute a compiled plugin. Pin the plugin version, maintain the customization as a reviewed patch or fork, and test it after every plugin upgrade.

## Planning behavior

The Friday run:

1. creates or merges the next ISO week's two files
2. carries every unresolved prior-week task into Monday
3. adds only a few high-confidence context cues
4. places meeting preparation one working day before the event
5. preserves user edits if the target week already exists
6. moves old planning files into `daily/Archive/` without deleting them
