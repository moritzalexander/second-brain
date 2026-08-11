# Migrating from 1.x to 2.0

The migration is additive. Preserve the existing vault and validate each module before retiring an older workflow.

## 1. Back up and inventory

- copy the private vault to a recoverable location
- list active scheduled automations and paused duplicates
- record current source cursors and backlog state
- run a targeted search for files outside the documented structure

Do not move source records until their links and IDs have been checked.

## 2. Add the new domains

Create `competitors/`, `documents/`, and `daily/Archive/`. Keep existing `context/`, `intelligence/`, `projects/`, `resources/`, and `teams/` paths unchanged.

Replace the operational guide with the v2 `AGENTS.md`. Keep `CLAUDE.md` as a compatibility pointer if another agent still expects it.

## 3. Upgrade ingestion

- replace filename-only deduplication with stable source IDs
- ingest finalized full meeting transcripts
- keep legacy meeting sources as historical coverage
- canonicalize cross-source duplicate meetings
- add persistent pending, failed, and capped queues
- add explicit source-coverage checks

Run the new sync against a small date window before expanding it.

## 4. Add document radar

Create Markdown records for recent reusable files and store their stable Drive or filesystem identity plus modification time. Keep document binaries outside the public template.

## 5. Replace the weekly note

Install Obsidian Tasks and Task List Kanban, then add the `weekly-kanban-overview` skill. Keep the old `YYYY-Www.md` files until the Kanban has been validated for a full week.

The new workflow carries all unresolved work into Monday. It does not retain stale weekday placement from the prior week.

## 6. Add indexing and health checks

- register the private vault as a QMD collection
- run `status`, `update`, `embed`, then `status`
- schedule the reindex on a reduced cadence
- add a weekly health check that validates both execution and source coverage

## 7. Remove duplicate schedules

After on-demand validation, keep exactly one active automation for each enabled module. Pause old jobs before enabling the corresponding v2 job. Do not delete their state until the new workflow has completed successfully.

## 8. Privacy check

Run:

```bash
python3 scripts/validate_public_template.py
```

Only the template repository is safe to publish. Never initialize Git inside the private vault as a shortcut.
