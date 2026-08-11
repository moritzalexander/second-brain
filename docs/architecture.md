# Architecture

Second Brain 2.0 is a file-based knowledge system with independent ingestion, synthesis, planning, indexing, and health modules. Markdown is the durable interface. Connectors and agents may change without forcing a migration of the knowledge itself.

## Processing model

```text
Authorized source adapters
  meeting transcripts | email | chat | Drive/files | manual notes
                         |
                         v
                 Intake and deduplication
                 stable source IDs first
                         |
              +----------+-----------+
              |                      |
              v                      v
       canonical raw record    processed intelligence
       intelligence/_raw/      intelligence/YYYY/MM/
                                      |
                    +-----------------+-----------------+
                    |                 |                 |
                    v                 v                 v
                projects/          teams/          competitors/
                    |                 |                 |
                    +-----------------+-----------------+
                                      |
                         daily digest and weekly Kanban
                                      |
                                 QMD retrieval
```

## Modules

### Intelligence sync

Reads only new, finalized, authorized source items. For each eligible item it:

1. resolves a stable source identifier
2. checks source-specific and cross-source deduplication keys
3. stores one canonical raw record
4. creates a dated, structured intelligence record
5. links known people, projects, and competitors
6. propagates material changes into durable hubs
7. records processed, deferred, failed, and capped items separately

Meeting adapters should ingest full finalized transcripts, not the source tool's generated summary. If two tools captured the same meeting, use the calendar event ID when available, then date, normalized title, and overlapping participants. Keep all available source IDs on the canonical record.

### Document radar

Detects recently changed reusable files and creates Markdown records under `documents/`. It records the source file identity and current modification timestamp, extracts usable content, and links the artifact to relevant projects and people. Documents are not treated as current merely because an older record exists.

### Daily wrap-up

Runs on a reduced cadence and synthesizes new intelligence by project. It highlights decisions, escalations, and open work. It also flags stale projects, missing hubs, and scope drift. It does not replace dated source records.

### Weekly Kanban

Creates a two-file planning surface for the next ISO week. The task source stores cards as normal Markdown checkboxes with a project tag and weekday tag. The board configuration groups project tags into rows and weekday tags into columns.

The deterministic baseline:

- carries every unresolved card and unresolved subtask from the preceding week
- resets carried work to Monday
- drops completed and cancelled root cards
- preserves links and `#weekly-starred`
- merges into an existing target week without changing user placement
- archives daily and weekly planning files older than the previous ISO week

Calendar and vault context may add a small number of high-confidence cards after the baseline. Meeting preparation belongs on the previous working day.

### QMD reindex

QMD is a local retrieval backstop for conceptual queries, renamed topics, and orphaned content. The safe refresh sequence is:

```text
status -> update -> embed -> status
```

The index is derived state. Keep it outside the public repository and rebuild it from the vault.

### Sync health check

Health has two independent dimensions:

- **execution:** expected automations ran, completed, and wrote valid state
- **coverage:** all eligible source items are processed or remain explicitly pending

A green execution log with missing source coverage is not healthy. Capped and failed source IDs must remain in a persistent backlog until processed or intentionally dismissed.

## Durable records

### Intelligence frontmatter

```yaml
---
date: 2026-04-03
source: meeting_adapter
type: meeting
source_ids:
  meeting_id: source-stable-id
  calendar_event_id: optional-event-id
projects: [program/project]
people: [Jane Doe]
tags: [customer-feedback, q2-planning]
confidentiality: private
---
```

Source adapters may add their stable IDs. Avoid encoding source identity only in filenames.

### Project frontmatter

```yaml
---
status: active
owner: Jane Doe
stakeholders: [John Smith]
started: 2026-01-15
target: 2026-06-30
---
```

### File naming

| Record | Pattern |
|---|---|
| Intelligence | `intelligence/YYYY/MM/YYYY-MM-DD-source-description.md` |
| Raw evidence | `intelligence/_raw/YYYY/MM/YYYY-MM-DD-source-description-raw.md` |
| Document | `documents/{kind}/YYYY/MM/YYYY-MM-DD-description.md` |
| Daily digest | `daily/YYYY-MM-DD.md` |
| Weekly board | `daily/YYYY-Www-kanban.md` |
| Weekly tasks | `daily/YYYY-Www-kanban-tasks.md` |
| Project | `projects/{program}/{project}.md` |
| Person | `teams/firstname-lastname.md` |
| Competitor | `competitors/company-name.md` |

## Retrieval

Use the cheapest reliable method:

1. **Direct hub read** for a known person, project, competitor, or context topic.
2. **Flat search** for names, dates, IDs, exact phrases, or known filenames.
3. **Graph traversal** for broad context: start from the hub, read first-degree links, follow up to ten relevant second-degree links, then run a flat orphan check.
4. **QMD** for conceptual, paraphrased, or cross-cutting questions without an obvious hub.

Every answer should distinguish source-backed facts, derived hub summaries, and agent inference.

## Propagation

| Evidence indicates | Derived update |
|---|---|
| material project decision | append to the project decision log with a source link |
| new responsibility for a known person | update the person profile with a source link |
| durable strategy or org change | update the relevant context hub |
| material competitor development | update the competitor profile |
| possible new project | flag it for confirmation before creating a hub |

Propagation never replaces the dated intelligence record. Conflicts remain visible and are resolved through explicit supersession, not silent overwrite.

## Scheduling

The template intentionally does not impose one universal cadence. Start low and increase only if the value justifies the cost. A practical default is:

| Module | Suggested cadence |
|---|---|
| Intelligence sync | weekdays, once or twice daily |
| Document radar | shortly after intelligence sync |
| Daily wrap-up | Monday, Wednesday, Friday |
| Weekly Kanban | Friday before the planning session |
| QMD reindex | every two days |
| Sync health | weekly, after at least one normal sync window |

Use non-overlapping times so source ingestion finishes before synthesis begins.

## Failure handling

- Never advance a source cursor past an unreadable item.
- Never interpret an authorization error as an empty inbox.
- Store transient failures in a retryable backlog.
- Never delete raw records during deduplication; choose one canonical record and link alternates.
- Never overwrite user-authored weekly cards or archive collisions.
- Treat screen captures as orientation, not as evidence that a source action completed.

## Public template boundary

This repository defines structure and reusable logic. An operational vault contains confidential data and derived state. The two must remain separate. Run the public-template validator before every commit or pull request.
