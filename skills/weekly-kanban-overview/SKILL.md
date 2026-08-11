---
name: weekly-kanban-overview
description: Create or refresh a next-week Obsidian Task List Kanban, carry every unresolved prior-week card and open subtask into Monday, add minimal high-confidence context, place meeting preparation one working day early, preserve user edits, and archive older planning files. Use for Friday weekly planning, Kanban rollover, carry-forward, or weekly archive maintenance.
---

# Weekly Kanban overview

Work in the user's private Second Brain vault.

## Create the baseline

1. Read `AGENTS.md`, the latest `daily/YYYY-Www-kanban-tasks.md`, its matching board, active project hubs, and current-week digests.
2. Run:

   `python3 {SKILL_DIR}/scripts/prepare_weekly_overview.py --vault "{VAULT_ROOT}"`

3. Treat the script output as the deterministic baseline. It safely creates or merges the next ISO week's pair, carries open task blocks, promotes unresolved children of resolved parents, resets carried cards to Monday, and archives older planning files.
4. Never overwrite an existing target-week file. Preserve user edits and explicit checkbox states. Add only missing items.

## Enrich sparingly

Inspect the next workweek's calendar when available and use recent vault evidence only when it changes what the user should prepare or follow up on.

- Add no more than eight context-generated cards in total and no more than two per day.
- Prefer the project rows already present in `weekly_project_order`.
- Do not create a project row without clear evidence.
- Put meeting preparation on the previous working day.
- For a Monday meeting, add preparation to the current Friday board when it exists.
- Keep every carried card on Monday. Calendar placement applies only to new context cards.
- If the target board already exists, preserve cards the user has moved.
- Use short actionable titles and preserve useful links.
- Preserve `#weekly-starred` on carried tasks.
- Treat `[ ]`, `[/]`, `[!]`, `[?]`, and `[>]` as unresolved.
- Do not carry `[x]` or `[-]` root tasks.

## File contract

Maintain:

- `daily/YYYY-Www-kanban.md`
- `daily/YYYY-Www-kanban-tasks.md`

The board filter and default task file must point to the matching task source. Every visible root card has exactly one `#plan/project/...` tag and one `#plan/day/...` tag.

Keep project order and stored colors from the latest task file. Add genuinely new project rows at the bottom.

## Archive rule

Keep the current ISO week, its immediately preceding week, and already prepared future weekly files in `daily/`. Move older dated daily notes and `daily/YYYY-Www*.md` files to `daily/Archive/`.

- Move; never delete.
- Never overwrite an archive collision.
- Include classic weekly notes, boards, task sources, and prototypes sharing the week prefix.

## Validate

Read the target files back and confirm:

1. week, dates, board filter, and default task file
2. all newly carried roots have one project tag and `#plan/day/mon`
3. completed and cancelled roots were not newly carried
4. archive moves and timestamps

Report created versus merged cards, context cards, archive moves, and unavailable sources.
