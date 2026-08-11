# Second Brain operating guide

This is {USER_FULL_NAME}'s private Second Brain. Read this file before working in the vault.

## Vault structure

```text
{VAULT_FOLDER_NAME}/
├── AGENTS.md
├── competitors/
├── context/
├── daily/
│   └── Archive/
├── documents/
├── intelligence/
│   └── _raw/
├── projects/
├── resources/
└── teams/
```

| Folder | Purpose |
|---|---|
| `competitors/` | one durable profile per competitor, linked to dated evidence |
| `context/` | slow-changing identity, company, strategy, and preferences |
| `daily/` | daily digests and current weekly planning |
| `documents/` | source-backed records for reusable files and decks |
| `intelligence/` | processed meetings, email, chat, decisions, and research |
| `intelligence/_raw/` | canonical full source evidence |
| `projects/` | active project hubs with status, decisions, and questions |
| `resources/` | templates, runbooks, and local scripts |
| `teams/` | people profiles and working context |

## Routing

- A known project, person, competitor, or context topic: read its hub first, then follow relevant wiki-links.
- A specific date, phrase, source ID, meeting, or email: use a targeted flat search.
- A broad question: read the hub, first-degree links, up to ten relevant second-degree links, then search for orphan references.
- A conceptual or renamed topic without an obvious hub: use QMD as a backstop.
- Verbatim evidence: read the authorized file in `intelligence/_raw/`.

Distinguish verified source facts, derived hub summaries, and inference.

## Naming

| Record | Pattern |
|---|---|
| daily digest | `daily/YYYY-MM-DD.md` |
| weekly board | `daily/YYYY-Www-kanban.md` |
| weekly tasks | `daily/YYYY-Www-kanban-tasks.md` |
| intelligence | `intelligence/YYYY/MM/YYYY-MM-DD-source-description.md` |
| raw evidence | `intelligence/_raw/YYYY/MM/YYYY-MM-DD-source-description-raw.md` |
| document | `documents/{kind}/YYYY/MM/YYYY-MM-DD-description.md` |
| project | `projects/{program}/{project}.md` |
| person | `teams/firstname-lastname.md` |
| competitor | `competitors/company-name.md` |

## Intelligence frontmatter

```yaml
---
date: YYYY-MM-DD
source: source_adapter
type: meeting | email | thread | decision | research
source_ids: {}
projects: [none]
people: []
tags: []
confidentiality: private
---
```

Project files use `status`, `owner`, `stakeholders`, `started`, and `target`.

## Intelligence sync

The normal cadence is deliberately low. Change it only when the user asks.

For each new authorized item:

1. read the full finalized source
2. resolve its stable source ID and deduplicate before writing
3. store canonical raw evidence in `intelligence/_raw/`
4. read relevant context and hubs
5. create a processed intelligence record
6. link projects, people, and competitors
7. propagate material changes into existing hubs with source links
8. keep failed or capped items pending

Never ingest unfinished recordings or a meeting tool's summary as the raw transcript. If multiple tools captured one meeting, canonicalize by calendar event ID first, then date, normalized title, and participant overlap. Preserve all available source IDs.

Create a new project hub only after user confirmation.

## Daily wrap-up

Gather that day's new intelligence, synthesize it by project, flag decisions and escalation, review project health, and write `daily/YYYY-MM-DD.md`. The daily file is a briefing, not a replacement for evidence.

## Weekly Kanban

The Friday run prepares the following Monday-to-Friday workweek.

- carry every unresolved prior-week card and unresolved subtask into Monday
- do not carry completed `[x]` or cancelled `[-]` root tasks
- add only short, high-confidence context cues
- place meeting preparation on the previous working day
- preserve user-created cards, placement, order, colors, links, completion state, and stars
- merge missing items into an existing target week; never replace it
- keep the current and previous ISO week in `daily/`, plus prepared future weeks
- move older daily and weekly planning files to `daily/Archive/`
- never overwrite an archive collision

## Documents

Create a Markdown record only for a reusable or contextually relevant file. Store its stable source identity and current modification timestamp. Reopen the live source before treating an old record as current.

## Propagation

- project decision: update the project hub with a dated source link
- responsibility or durable context for a known person: update the person profile
- durable strategy or organization change: update the relevant context hub
- material competitor development: update the competitor profile
- new initiative: flag it for user confirmation

The dated intelligence file remains the source record.

## Health and failure handling

Sync health is healthy only when execution and source coverage pass. Do not advance a cursor past an inaccessible or unreadable item. Authorization errors are blockers, not empty inboxes. Keep failed, deferred, and capped source IDs in persistent state.

## Privacy and external actions

- This vault is private and must not be copied into a public repository.
- Never publish, send, submit, or write back to an external system without explicit user approval.
- Treat raw transcripts, email, chat, customer, people, and career information as confidential.
- Screen captures are orientation only, not proof that an external action completed.
- A shared team graph must receive data through an explicit publishing and confidentiality boundary; it must not read everyone's private sources directly.

## General rules

1. Never delete knowledge files; archive or deprecate them.
2. Never silently overwrite user-authored planning content.
3. Prefer stable source IDs and targeted verification over assumption.
4. Link derived summaries back to their source records.
5. Preserve ambiguity and conflicting evidence until explicitly resolved.
6. Keep generated planning content minimal.
