# Second Brain -- CLAUDE.md

This is {USER_FULL_NAME}'s Second Brain -- a persistent knowledge vault that gives AI agents full context across conversations. Read this file at the start of every session.

---

## Vault Structure

```
{VAULT_FOLDER_NAME}/
├── CLAUDE.md              ← You are here. Navigation & operating rules.
├── context/               ← Foundational, slow-changing context
├── daily/                 ← Synthesized daily digests
├── intelligence/          ← All external info, processed & tagged
│   └── _raw/              ← Full raw transcripts, email threads, etc.
├── projects/              ← Active projects, status, decisions
├── resources/             ← Templates, frameworks, reusable artifacts
└── teams/                 ← People profiles (team + key stakeholders)
```

### Folder Purposes

| Folder | Purpose | Read when... | Write when... |
|--------|---------|-------------|---------------|
| `context/` | Who {USER_FIRST_NAME} is, their role, company, strategy, preferences | Starting any task; need background on user, company, or strategy | User says "remember this" or updates a preference/fact about themselves |
| `daily/` | Daily digests and weekly plans | User asks "what happened today/yesterday/this week?" | Daily wrap-up (5 PM) and weekly sync (5:25 PM) |
| `intelligence/` | Processed, tagged chunks from meetings, emails, Slack | Need detail on a specific meeting, conversation, or decision | Intelligence sync processes new data (every ~1 hour) |
| `intelligence/_raw/` | Full unprocessed transcripts and email threads | Need verbatim quotes or full context beyond the processed summary | Intelligence sync stores raw source alongside processed version |
| `projects/` | Active projects -- goals, status, decisions, open questions | User asks about a project, or need to understand current priorities | Project status changes, new decisions logged, daily wrap-up review |
| `resources/` | Reusable templates, frameworks, prompts, reference docs | Building a deliverable that could use an existing template | User creates or identifies a reusable artifact |
| `teams/` | One file per person -- role, responsibilities, working style | Need to understand who someone is, or drafting comms for/about them | New person identified, or existing profile needs updating |

---

## File Naming Conventions

| Folder | Pattern | Example |
|--------|---------|---------|
| `context/` | `topic.md` | `me.md`, `company.md`, `strategy.md` |
| `daily/` | `YYYY-MM-DD.md` (daily) / `YYYY-Www.md` (weekly) | `2026-04-03.md` / `2026-W15.md` |
| `intelligence/` | `YYYY/MM/YYYY-MM-DD-source-description.md` | `2026/04/2026-04-03-meeting-team-weekly.md` |
| `intelligence/_raw/` | `YYYY/MM/YYYY-MM-DD-source-description-raw.md` | `2026/04/2026-04-03-meeting-team-weekly-raw.md` |
| `projects/` | Folder per major initiative, file per sub-project | `product-launch/go-to-market.md` |
| `resources/` | Descriptive name | `weekly-plan-template.md`, `qbr-framework.md` |
| `teams/` | `firstname-lastname.md` | `jane-doe.md` |

---

## Frontmatter / Tagging Conventions

Every file in `intelligence/` MUST have YAML frontmatter with these fields:

```yaml
---
date: 2026-04-03
source: granola | gmail | slack | manual
type: meeting | email | thread | decision | research
projects: [project-folder/sub-project]
people: [Jane Doe, John Smith]
tags: [topic-tag, another-tag]
---
```

| Field | Required | Description |
|-------|----------|-------------|
| `date` | Yes | Date of the event (not when it was processed) |
| `source` | Yes | Where the information came from |
| `type` | Yes | What kind of information it is |
| `projects` | Yes (if applicable) | Which projects this relates to (always a list). Use `[none]` if general. |
| `people` | Yes | People involved or mentioned |
| `tags` | Yes | Flexible topic tags for cross-cutting queries |

Project files in `projects/` use:

```yaml
---
status: active | paused | completed
owner: {USER_FULL_NAME}
stakeholders: [Stakeholder Name]
started: 2026-01-15
target: 2026-06-30
---
```

---

## Routing Rules -- Where to Look

| User asks about... | Look in... |
|--------------------|-----------|
| Themselves, their role, company, strategy, preferences | `context/` |
| What happened today, yesterday, this week | `daily/` first, then `intelligence/` for detail |
| A specific meeting, email, or conversation | `intelligence/` (search by date, source, people, or tags) |
| Verbatim quotes or full transcript | `intelligence/_raw/` |
| A specific project -- status, decisions, next steps | `projects/` first, then follow links to `intelligence/` |
| A person -- who they are, what they do | `teams/` |
| How to format or structure a deliverable | `resources/` |
| "What do you know about X?" (broad) | Start with `context/`, then `projects/`, then `intelligence/` |

### Query Strategy -- Flat Search vs. Graph Traversal

The vault uses `[[wiki-links]]` to connect files. When answering questions, choose the right search strategy:

**Flat search** (grep/glob only) -- use for **narrow, targeted lookups**:
- "What did Alice say in last Friday's meeting?"
- "Find the pricing decision from March 18"
- "Which meetings mentioned Acme Corp?"

**Graph traversal** (follow wiki-links) -- use for **broad, contextual questions**:
- "Tell me about Jane Doe" / "What's the full picture on X?"
- "Prepare me for a meeting with Bob"
- "What's the current state of the product launch?"
- Any question where relationships, patterns, or strategic context matter

**Graph traversal procedure:**
1. **Start node** -- Read the entry-point file (`teams/`, `projects/`, or `context/`)
2. **First-degree links** -- Extract all `[[wiki-links]]` from that file. Read each linked file.
3. **Second-degree links** -- From first-degree files, follow links that are relevant to the query (up to 10 additional files)
4. **Cross-reference** -- Run a flat grep to catch any files that mention the topic but are NOT connected by links (orphaned references)
5. **Synthesize** -- Combine linked context + grep results. Note any patterns from the graph structure (clusters, bridge nodes, recurring co-occurrences)

Graph traversal reads more files but produces qualitatively better answers: second-degree relationships, strategic context, and structural patterns that flat search misses entirely.

---

## Writing Rules -- Where to Store

| Information type | Store in... | How |
|-----------------|------------|-----|
| User says "remember this" about themselves | `context/` -- update the relevant file | Append or edit the specific section |
| User says "remember this" about a person | `teams/` -- update that person's file | Append or edit the specific section |
| New preference or rule (e.g., "never use em dashes") | `context/writing-preferences.md` | Append to the rules list |
| Decision made about a project | `projects/` -- update that project file's Decisions section | Prepend with date |
| New meeting/email/thread from sync | `intelligence/` + `intelligence/_raw/` | Create new tagged file |
| Reusable template or framework identified | `resources/` | Create new file |

### Automatic Propagation During Intelligence Sync

When processing new intelligence, the AI should also detect and propagate updates to other folders:

| Detected in intelligence... | Propagate to... |
|----------------------------|----------------|
| New responsibility, project, or task for a person | `teams/` -- update that person's file |
| A decision that affects a project | `projects/` -- append to that project's Decisions section |
| A change in strategy, priorities, or org structure | `context/` -- update the relevant file |
| A new project or initiative mentioned for the first time | Flag for user confirmation before creating a new project file |

The intelligence file remains the source record. Propagation adds a summary to the relevant file with a link back to the intelligence entry.

---

## Intelligence Sync Rules (Every ~1 Hour)

### Sources
1. **Granola** -- All meetings. Pull raw transcripts via `get_meeting_transcript`.
2. **Gmail** -- Full inbox. AI decides relevance based on vault context.
3. **Slack** -- DMs and channels where {USER_FIRST_NAME} actively participates. Skip broadcast/update-only channels.

### Processing Steps
For each new piece of information:

1. **Read** the raw content from the source
2. **Store raw** content in `intelligence/_raw/` with proper naming
3. **Contextualize** -- read relevant `context/` and `projects/` files to understand significance
4. **Extract** key topics, decisions, action items, and notable information
5. **Tag** with proper frontmatter (date, source, type, projects, people, tags)
6. **Write** the processed file to `intelligence/`
7. **Propagate** updates to `teams/`, `projects/`, or `context/` as applicable
8. **Skip** if the content is not relevant to any known project, topic, or stakeholder

### Deduplication
Before processing, check existing filenames in `intelligence/` for the current date. If a meeting, email, or thread already has a file, skip it unless the source content has been updated or extended.

### Processing Format for Intelligence Files

```markdown
---
[frontmatter]
---

# [Descriptive Title] -- YYYY-MM-DD

## Key Topics
- ...

## Decisions
- ...

## Action Items
- [ ] Task --> Owner

## Notable Quotes or Details
- ...

## Links
**Projects:** [[projects/path|Display Name]]
**People:** [[teams/firstname-lastname|Person Name]]

## Raw Source
See: [[_raw/YYYY/MM/YYYY-MM-DD-source-description-raw]]
```

---

## Daily Wrap-up Rules (Every Evening at 5 PM)

The daily wrap-up reads everything that landed in `intelligence/` that day and produces a synthesized digest.

### Steps
1. **Gather** all `intelligence/` files from today
2. **Read** current `projects/` files for status context
3. **Summarize** the day organized by project/topic
4. **Flag** any significant decisions, escalations, or open items
5. **Review project health** -- do any project files need status updates, tag changes, or restructuring?
6. **Write** to `daily/YYYY-MM-DD.md`

### Daily File Format

```markdown
# YYYY-MM-DD

## Summary
[2-3 sentence overview of the day]

## By Project

### [Project Name]
- [Key updates, decisions, developments]
- Sources: [[intelligence links]]

### [Project Name]
- ...

## Cross-Cutting
- [Items that span multiple projects or don't fit one project]

## Project Health
- [Any recommended changes to project structure, tags, or status]

## Open Items
- [ ] ...
```

---

## Weekly Sync Rules (Every Weekday at 5:25 PM)

The weekly sync creates and maintains a weekly planning file at `daily/YYYY-Www.md`.

### Structure
Weekly files have two zones separated by a `<!-- MANUAL SECTION -->` HTML comment:

1. **Auto section** (top): Open items aggregated from each day's `daily/YYYY-MM-DD.md` digest. Rebuilt every sync. User can check items off or distribute them into their day plan, but edits above the marker may be overwritten.
2. **Manual section** (bottom, below `<!-- MANUAL SECTION -->`): "My Week" with day-by-day checkboxes (Mon-Fri). Only the user edits this. Automation MUST preserve it byte-for-byte.

### Checkbox Merge Rule
Before rebuilding the auto section, extract all `[x]` items from the existing weekly file. When rebuilding, if an item was checked in the weekly file, it stays `[x]` regardless of the daily source. User triage always wins.

---

## Project Maintenance Rules

- Project files are the **source of truth** for what is being worked on
- The daily wrap-up checks project health and flags when:
  - A project has had no intelligence updates in 2+ weeks (may be stale)
  - Intelligence is being tagged to a project that doesn't exist yet (may need a new project file)
  - Two projects are converging (may need merging)
  - A project's scope has clearly shifted from its original description
- Project changes (new projects, merges, closures) should be confirmed with the user before executing

---

## General Rules

1. **Always read this file first** when starting a new session
2. **Never delete files** -- archive or mark as deprecated instead
3. **Never overwrite** -- append, prepend, or edit specific sections
4. **Raw transcripts over AI summaries** -- always store the full raw transcript, not another tool's summary. This vault has more context for better summarization.
5. **Ask before restructuring** -- if the vault structure needs changes (new folders, renamed projects, etc.), propose to the user first
6. **Link liberally** -- when a processed intelligence file relates to a project, link it. When a person is mentioned, link to their `teams/` file.
7. **When in doubt about where something goes, use `intelligence/`** -- it's the catch-all. The daily wrap-up will sort it out.
