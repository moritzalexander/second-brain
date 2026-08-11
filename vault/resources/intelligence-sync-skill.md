---
name: intelligence-sync
description: Ingest new authorized meetings, email, and chat into raw and processed Second Brain records with stable-ID deduplication, backlogs, and source-coverage reporting.
---

# Intelligence sync

Work in `{VAULT_ROOT}`. Read `AGENTS.md` before processing data.

## Configuration

Define enabled sources in the automation prompt or a private local config. For each source specify:

- adapter or connector name
- authorized account or mailbox identity
- strict scan window and wider backstop window
- stable source ID field
- maximum items per run
- raw-content retrieval method
- cursor and pending-backlog location

Do not put credentials or operational IDs in this file.

For Wispr Flow on macOS, the public template includes the optional read-only adapter at `adapters/wispr-flow/wispr_flow_meetings.py`. Copy it into the private vault or invoke it from a separately cloned template repository; do not make the operational vault public.

## Run order

1. Read persistent cursor and backlog state.
2. Process oldest pending items before new discovery.
3. Run a strict recent scan, then the configured wider backstop.
4. Deduplicate by stable source ID before fetching large bodies.
5. Fetch and write one large transcript or thread at a time.
6. Write its canonical raw record and processed record before fetching the next.
7. Propagate material updates into existing hubs.
8. Save cursors only through the last successfully processed item.
9. Report discovery, coverage, processing, skip, failure, cap, and pending counts per source.

## Meetings

- Ingest only finalized meetings with a complete non-empty transcript.
- Store the full authorized transcript as raw evidence. Do not substitute notes or a generated summary.
- Deduplicate within each source by meeting ID.
- Match across sources by calendar event ID first, then date, normalized title, and participant overlap.
- When two sources captured one meeting, create one canonical record and preserve all source IDs.
- Keep unfinished and transcript-retrieval failures pending.
- Skip clearly personal meetings unless the user explicitly requests them or they map to an authorized project.

## Email

- Verify the connected mailbox identity before reading content.
- If the profile is wrong or unavailable, skip email without advancing its cursor.
- Discover broadly, then shortlist substantive threads using known projects and stakeholders.
- Deduplicate by thread ID and retain deferred thread IDs.
- Store the complete relevant thread when authorized, not only a search-result snippet.

## Chat

- Process direct conversations and channels in which the user actively participates.
- Skip broadcast-only traffic and low-signal notifications.
- Preserve thread identity, timestamps, speakers, and permalinks when available.

## Processing format

```markdown
---
date: YYYY-MM-DD
source: source_adapter
type: meeting | email | thread
source_ids: {}
projects: [none]
people: []
tags: []
confidentiality: private
---

# Descriptive title - YYYY-MM-DD

## Key Topics
- ...

## Decisions
- ...

## Action Items
- [ ] Task -> Owner

## Notable Details
- ...

## Raw Source
See: [[_raw/YYYY/MM/YYYY-MM-DD-source-description-raw]]
```

## Relevance and propagation

Read relevant project, people, context, and competitor hubs before synthesizing. Update an existing hub only for a durable, material change and link to the dated intelligence record. Flag a possible new project for user confirmation.

## Failure contract

- Authorization failure is not an empty source.
- A capped item remains pending.
- A failed item remains pending with an error reason.
- Never create a meeting record from notes alone when the required transcript is unavailable.
- Never advance a cursor past an unresolved item unless the source supports an independent per-item cursor.
- Never delete or overwrite source evidence.
