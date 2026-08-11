# Second Brain 2.0

A private, source-backed knowledge vault for AI agents and Obsidian.

Second Brain 2.0 turns meetings, email, chat, and documents into durable Markdown records. It keeps raw evidence separate from synthesis, links intelligence to people and projects, prepares a compact weekly Kanban, and checks that scheduled ingestion is both running and complete.

The repository contains a public template only. Your vault content, credentials, source IDs, and automation state stay outside Git.

## What changed in 2.0

The original template used one hourly ingestion job, a daily digest, and a classic weekly note. The current architecture is modular and deliberately lower cadence:

- source adapters for finalized meeting transcripts, email, chat, and documents
- stable-ID deduplication and cross-source meeting matching
- separate raw evidence and processed intelligence records
- document radar for reusable Docs, Slides, PDFs, and spreadsheets
- QMD semantic indexing as a local retrieval backstop
- an editable Monday-to-Friday Task List Kanban
- deterministic carry-forward of unresolved work into Monday
- sync-health checks that verify execution and source coverage
- optional competitive-radar modules

## System at a glance

```text
Sources                         Durable vault                     Work surfaces
Calls, email, chat, docs  ->    raw evidence + intelligence  ->   project and people hubs
                                      |                           daily digests
                                      |                           weekly Kanban
                                      +-> local QMD index          agent skills

Scheduled modules
  intelligence sync  ->  document radar  ->  daily wrap-up
  weekly Kanban      ->  QMD reindex      ->  sync health check
```

## Vault structure

```text
vault/
├── AGENTS.md                 # agent navigation and operating rules
├── CLAUDE.md                 # compatibility pointer to AGENTS.md
├── competitors/              # durable competitor profiles
├── context/                  # identity, company, strategy, preferences
├── daily/                    # daily digests and current weekly planning
│   └── Archive/              # older daily and weekly planning files
├── documents/                # reusable records derived from files
├── intelligence/             # processed meetings, email, and chat
│   └── _raw/                 # canonical source evidence
├── projects/                 # active project hubs
├── resources/                # local runbooks and templates
└── teams/                    # people profiles
```

## Design principles

1. **Evidence before synthesis.** Store the full authorized source separately, then derive a concise record with links back to it.
2. **Stable identity before fuzzy matching.** Deduplicate by source IDs first. Use title, date, attendees, and calendar IDs only for cross-source matching.
3. **Hubs are derived views.** Project, person, context, and competitor files summarize the latest state; dated intelligence remains the evidence trail.
4. **Human planning stays editable.** Automation may add missing cards but must preserve user-created cards, placement, links, colors, completion state, and stars.
5. **Minimal generation.** A planning board should surface real commitments, not fill empty space.
6. **Health means coverage.** A successful run is not healthy if eligible source items were skipped or capped without remaining in a backlog.
7. **Private by default.** The template is public; operational data and generated knowledge are not.

## Prerequisites

- an AI coding agent that can read and write local files and run scheduled automations
- [Obsidian](https://obsidian.md/)
- [Tasks](https://github.com/obsidian-tasks-group/obsidian-tasks) and [Task List Kanban](https://github.com/dsebastien/obsidian-task-list-kanban) for the weekly board
- optional [QMD](https://github.com/tobi/qmd) for local hybrid and semantic search
- connectors or local read-only adapters for the sources you explicitly authorize

Pin plugin versions in your operational vault. Task List Kanban UI extensions are described in [docs/obsidian-kanban.md](docs/obsidian-kanban.md); this repository does not redistribute a compiled community-plugin bundle.

## Quick start

1. Clone this repository and copy `vault/` to a private location.
2. Replace the placeholders in `vault/AGENTS.md` and the context templates.
3. Read `vault/resources/setup-skill.md` with your agent and configure only the sources you approve.
4. Install the optional reusable skills from `skills/` into your agent's skill directory.
5. Create scheduled automations from `automations/templates/`, using your vault path, timezone, and chosen cadence.
6. Run every module once in dry-run or on-demand mode, then inspect the created files before enabling recurrence.
7. Run `python3 scripts/validate_public_template.py` before publishing changes.

See [docs/architecture.md](docs/architecture.md) for the data flow and [docs/migration-v1-to-v2.md](docs/migration-v1-to-v2.md) for an upgrade checklist.

The optional local Wispr Flow adapter is documented under [adapters/wispr-flow](adapters/wispr-flow/README.md). Connector-backed sources remain configuration, not hard-coded dependencies.

## Weekly planning

Each ISO week uses two files:

- `daily/YYYY-Www-kanban.md`: board configuration
- `daily/YYYY-Www-kanban-tasks.md`: editable task source

The Friday automation prepares the next workweek. Every unresolved root task and unresolved child task from the preceding board is carried into Monday as a planning inbox. Calendar-derived meeting preparation is placed on the previous working day. Already existing target-week files are merged, never replaced.

## Security boundary

Never commit:

- raw transcripts, email threads, chat exports, or customer files
- personal names, company-confidential context, or account data
- tokens, cookies, database files, local source IDs, or automation state
- local absolute paths or generated QMD indexes
- a private vault copied into this template repository

The multiplayer/team pattern requires an additional publishing boundary. Do not point a shared team graph directly at personal email, WhatsApp, or private meeting stores. See [docs/privacy-and-security.md](docs/privacy-and-security.md).

## Validation

```bash
python3 -m unittest discover -s skills/weekly-kanban-overview/tests
python3 scripts/validate_public_template.py
```

## License

MIT. See [LICENSE](LICENSE).
