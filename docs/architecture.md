# Architecture

How the Second Brain vault works as a system.

---

## The Three-Agent Pipeline

The vault is powered by three automated agents that run as scheduled tasks in Claude Code. Each agent builds on the output of the previous one.

```
Source Data                 Agent 1                  Agent 2                Agent 3
────────────               ──────────               ──────────             ──────────
Granola (meetings)  ───┐
Gmail (emails)      ───┼──▶ Intelligence Sync  ──▶  Daily Wrap-up  ──▶  Weekly Sync
Slack (messages)    ───┘    (hourly)                 (5 PM weekdays)      (5:25 PM weekdays)
                            │                        │                    │
                            ▼                        ▼                    ▼
                            intelligence/            daily/               daily/
                            intelligence/_raw/        YYYY-MM-DD.md        YYYY-Www.md
```

### Agent 1: Intelligence Sync (hourly)

**Input:** Raw data from Granola, Gmail, and Slack APIs via MCP servers.

**Output:** Two files per item:
- `intelligence/YYYY/MM/YYYY-MM-DD-source-description.md` -- processed, tagged, linked
- `intelligence/_raw/YYYY/MM/YYYY-MM-DD-source-description-raw.md` -- verbatim transcript or full email thread

**Processing logic:**
1. Check what's new since the last sync (compare against existing filenames)
2. Pull raw content from each source
3. Read vault context (CLAUDE.md, projects/, context/) to understand significance
4. Extract key topics, decisions, action items
5. Tag with YAML frontmatter (date, source, type, projects, people, tags)
6. Write both processed and raw files
7. Propagate updates to teams/, projects/, or context/ as needed

**Key design decision:** Raw transcripts are always stored separately from processed summaries. The vault's own context produces better summaries than any external tool, so we always keep the raw source for re-processing.

### Agent 2: Daily Wrap-up (5 PM weekdays)

**Input:** All intelligence files from today + current project files for context.

**Output:** `daily/YYYY-MM-DD.md` -- a synthesized daily digest.

**Processing logic:**
1. Gather all intelligence files matching today's date
2. Read project files for status context
3. Synthesize by project/topic (not just summarize -- add insight)
4. Flag decisions, escalations, and open items
5. Review project health (stale projects, missing project files, scope drift)

The daily digest is the user's end-of-day briefing. It should be readable in 3-5 minutes and highlight anything urgent or surprising.

### Agent 3: Weekly Sync (5:25 PM weekdays)

**Input:** Daily digests from the current week + existing weekly file.

**Output:** `daily/YYYY-Www.md` -- a weekly planning file with two zones.

**The two-zone design:**
- **Auto section** (top): Open items aggregated from daily digests. Rebuilt each sync.
- **Manual section** (bottom): The user's day-by-day plan. Never touched by automation.

The `<!-- MANUAL SECTION -->` HTML comment separates the two zones. Everything below it is preserved byte-for-byte.

**Checkbox merge logic:**
The weekly sync preserves the user's triage decisions. If the user checks off an item `[x]` in the weekly file, it stays checked even if the daily source still has `[ ]`. The merge algorithm:
1. Extract all `[x]` items from the current weekly auto section (the "overrides")
2. Pull items from each day's daily digest
3. For each item: if it's in the overrides set OR marked `[x]` in the daily source, keep it `[x]`
4. Deduplicate across days (same task appears in Monday and Tuesday -- keep only the Tuesday version)

---

## File Naming Conventions

All files use **lowercase-kebab-case** with date prefixes for chronological sorting.

| Source | Pattern | Example |
|--------|---------|---------|
| Meeting | `YYYY-MM-DD-meeting-description.md` | `2026-04-03-meeting-team-weekly.md` |
| Email | `YYYY-MM-DD-email-subject-summary.md` | `2026-04-03-email-pricing-update.md` |
| Slack | `YYYY-MM-DD-slack-description.md` | `2026-04-03-slack-activity.md` |
| Raw | Same as above + `-raw` suffix | `2026-04-03-meeting-team-weekly-raw.md` |

Files are organized by year and month:
```
intelligence/
├── 2026/
│   ├── 03/
│   │   ├── 2026-03-15-meeting-product-review.md
│   │   └── 2026-03-15-email-budget-approval.md
│   └── 04/
│       └── 2026-04-01-meeting-kickoff.md
└── _raw/
    └── 2026/
        └── 03/
            └── 2026-03-15-meeting-product-review-raw.md
```

---

## Frontmatter Schema

Every intelligence file has YAML frontmatter for structured querying:

```yaml
---
date: 2026-04-03          # Date of the event (not processing date)
source: granola            # granola | gmail | slack | manual
type: meeting              # meeting | email | thread | decision | research
projects:                  # List of related project paths
  - product-launch/go-to-market
  - infrastructure/security-audit
people:                    # People involved or mentioned
  - Jane Doe
  - John Smith
tags:                      # Flexible topic tags
  - pricing
  - q2-planning
  - customer-feedback
---
```

Project files use a different schema:

```yaml
---
status: active             # active | paused | completed
owner: Jane Doe
stakeholders:
  - John Smith
  - Alice Johnson
started: 2026-01-15
target: 2026-06-30
---
```

---

## Graph Traversal

The vault uses `[[wiki-links]]` (Obsidian-style) to connect files. This creates a navigable knowledge graph.

### When to use flat search vs. graph traversal

| Question type | Strategy | Example |
|--------------|----------|---------|
| Specific fact lookup | Flat (grep) | "What was the Q2 revenue target?" |
| Date-bounded search | Flat (glob) | "What happened last Thursday?" |
| Person deep-dive | Graph | "Tell me about Jane Doe" |
| Project status | Graph | "What's the state of the product launch?" |
| Meeting prep | Graph | "Prepare me for my meeting with the CEO" |

### Graph traversal procedure

```
Start Node (teams/jane-doe.md)
    │
    ├──▶ First-degree links (read all [[wiki-links]] in the file)
    │    ├── projects/product-launch/overview.md
    │    ├── intelligence/2026/03/2026-03-20-meeting-product-review.md
    │    └── intelligence/2026/04/2026-04-01-email-launch-timeline.md
    │
    ├──▶ Second-degree links (follow relevant links from first-degree files, up to 10)
    │    ├── intelligence/2026/03/2026-03-18-meeting-design-review.md
    │    └── teams/john-smith.md
    │
    └──▶ Cross-reference (grep for "Jane Doe" to catch orphaned mentions)
         └── intelligence/2026/04/2026-04-03-slack-activity.md (not linked but mentions Jane)
```

Graph traversal reads more files but catches second-degree relationships, strategic context, and structural patterns that flat search misses.

---

## Propagation Rules

When the intelligence sync processes a new file, it checks for updates that should propagate to other parts of the vault:

| Detected in intelligence | Action | Target |
|------------------------|--------|--------|
| New responsibility for a person | Append to their profile | `teams/firstname-lastname.md` |
| Decision affecting a project | Prepend to Decisions section (with date) | `projects/path/file.md` |
| Change in org structure or strategy | Update relevant section | `context/org-structure.md` or `context/strategy.md` |
| New project mentioned | Flag for user confirmation | Don't auto-create -- ask the user |
| Person not yet in teams/ | Create a stub profile | `teams/firstname-lastname.md` |

The intelligence file is always the **source record**. Propagation adds a summary with a wiki-link back to the intelligence entry.

---

## Deduplication

Before processing any item, the intelligence sync checks for existing files:

1. **Filename match:** Does `intelligence/YYYY/MM/YYYY-MM-DD-*description*` already exist?
2. **Content match:** For emails, check if the subject line is already covered in an existing thread file.
3. **Skip or append:** If an existing file covers the same event, skip. If the source has new content (e.g., meeting was extended), append rather than create a duplicate.

---

## Project Health Monitoring

The daily wrap-up acts as a project health monitor:

| Signal | Meaning | Action |
|--------|---------|--------|
| No intelligence tagged to a project in 2+ weeks | Project may be stale or completed | Flag for user: "Should this be marked paused/completed?" |
| Intelligence tagged to a non-existent project path | A new project may have emerged | Flag for user: "Should I create a project file for X?" |
| Two projects frequently co-occur in intelligence | Projects may be converging | Flag for user: "Should these be merged?" |
| Project scope has drifted from its description | Description may need updating | Flag for user with suggested updates |
