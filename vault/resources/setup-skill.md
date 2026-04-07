# Second Brain Setup Skill

This skill guides Claude Code through setting up a Second Brain vault from scratch.

## Prerequisites

Before running this skill, the user needs:
1. **Claude Code** installed and working
2. **Obsidian** installed (the vault is viewed/edited in Obsidian)
3. **MCP servers** connected in Claude Code:
   - **Gmail** (for email intelligence)
   - **Granola** (for meeting transcripts)
   - **Slack** (for Slack messages)
   - **Google Calendar** (optional, for schedule-aware context)
4. A **vault location** chosen (e.g., a Google Drive folder, local folder, or iCloud path)

---

## Phase 1: Discovery -- Learn About the User

Before building anything, gather the following from the user. Ask conversationally, not as a form.

### Required Information

**Identity:**
- Full name
- Title / role
- Organization and team
- Who they report to (name + title)

**Team:**
- Direct reports (name, role, focus area)
- Interns or support staff
- Key collaborators they interact with daily/weekly

**Projects:**
- What are they actively working on? (3-7 main initiatives)
- For each: brief description, status, key stakeholders, timeline
- Any sub-projects within larger initiatives?

**Key Stakeholders:**
- Beyond their direct team, who are the 10-20 people they interact with most?
- For each: name, role, relationship (peer, skip-level, cross-functional, etc.)

**Communication Patterns:**
- Which Slack channels do they actively participate in? (skip broadcast-only channels)
- How many meetings per day on average?
- Do they get high-volume email from specific people?

**Weekly Rhythms:**
- What recurring tasks do they do each Monday? Tuesday? etc.
- Any recurring meetings they own or prep for?

**Preferences:**
- Any communication style preferences? (e.g., "no em dashes", "always use bullet points")
- Timezone?

---

## Phase 2: Create the Vault Structure

Create the folder hierarchy:

```
{VAULT_ROOT}/
├── CLAUDE.md
├── context/
├── daily/
├── intelligence/
│   └── _raw/
│       └── {YYYY}/
│           └── {MM}/
├── projects/
├── resources/
└── teams/
```

Also create the intelligence year/month directories for the current period:

```bash
mkdir -p "{VAULT_ROOT}/intelligence/{YYYY}/{MM}"
mkdir -p "{VAULT_ROOT}/intelligence/_raw/{YYYY}/{MM}"
```

---

## Phase 3: Generate CLAUDE.md

The vault template already includes a `CLAUDE.md` with `{PLACEHOLDER}` values. Replace all placeholders with user-specific values gathered in Phase 1:

- `{USER_FULL_NAME}` -- the user's full name
- `{USER_FIRST_NAME}` -- the user's first name
- `{VAULT_FOLDER_NAME}` -- the folder name of the vault

Review the routing rules, writing rules, and sync rules. Adjust schedules if the user has different preferences (e.g., wrap-up at 6 PM instead of 5 PM).

---

## Phase 4: Create Initial Context Files

### `context/me.md`
Fill in the template in `context/me.md` with the user's information from Phase 1.

### `context/writing-preferences.md`
Add any preferences the user mentioned. This file grows over time as the user says "remember this."

### Additional context files
Create files as needed based on what the user shares:
- `context/company.md` -- company overview, strategy, competitive landscape
- `context/org-structure.md` -- org chart and reporting lines
- `context/stakeholders.md` -- key stakeholder directory
- `context/team.md` -- team overview with links to individual team files
- `context/strategy.md` -- strategic priorities and goals

---

## Phase 5: Create Team Files

For each person the user identified in Phase 1, create a file at `teams/firstname-lastname.md`:

```markdown
---
name: {PERSON_NAME}
role: {ROLE}
team: {TEAM}
relationship: {RELATIONSHIP TO USER}
---

# {PERSON_NAME}

## Role
{BRIEF DESCRIPTION}

## Key Context
{ANYTHING THE USER SHARED ABOUT THIS PERSON}

## Working Style
<!-- To be expanded over time -->

## Related Intelligence
<!-- Will be populated by intelligence sync -->
```

---

## Phase 6: Create Project Files

For each project identified in Phase 1, create the appropriate structure:

```markdown
---
status: active
owner: {USER_FULL_NAME}
stakeholders: [{STAKEHOLDER_NAMES}]
started: {DATE}
target: {DATE_OR_TBD}
---

# {PROJECT_NAME}

{BRIEF DESCRIPTION}

## Current Focus
{WHAT'S HAPPENING NOW}

## Key Decisions
<!-- Will be populated by intelligence sync -->

## Open Questions
{ANY OPEN QUESTIONS THE USER MENTIONED}

## Related Intelligence
<!-- Will be populated by intelligence sync -->
```

---

## Phase 7: Create Templates

### `resources/weekly-plan-template.md`

Customize the manual section based on the user's weekly rhythms from Phase 1. The template is already in `resources/weekly-plan-template.md` -- update the Monday-Friday sections with their recurring tasks.

---

## Phase 8: Set Up Scheduled Tasks

Create three scheduled tasks using the `create_scheduled_task` MCP tool.

### Task 1: Intelligence Sync
- **ID:** `intelligence-sync`
- **Schedule:** `0 * * * *` (every hour, every day including weekends)
- **Skill:** Adapt the `resources/intelligence-sync-skill.md` from the vault, replacing the vault path, user name, project paths, and team file list with real values.

### Task 2: Daily Wrap-up
- **ID:** `daily-wrapup`
- **Schedule:** `3 17 * * 1-5` (5:03 PM weekdays)
- **Skill:** Adapt the `resources/daily-wrapup-skill.md`, replacing vault path and user name.

### Task 3: Weekly Sync
- **ID:** `weekly-sync`
- **Schedule:** `25 17 * * 1-5` (5:25 PM weekdays)
- **Skill:** Adapt the `resources/weekly-sync-skill.md`, replacing vault path and user name.

**Important:** The scheduled task SKILL.md files live at `~/.claude/scheduled-tasks/{task-id}/SKILL.md`. Also save a backup copy in `{VAULT_ROOT}/resources/` for version control.

---

## Phase 9: Initial Data Population (Backfill)

After the vault is set up, do an initial backfill:

1. **Meetings**: Pull the last 1-2 weeks of meetings from Granola. Process each into intelligence files.
2. **Email**: Pull the last week of relevant emails. Focus on threads with key stakeholders and project-related decisions.
3. **Skip Slack** for backfill -- it's usually too noisy for historical pulls. Start fresh.

For each item, create both processed (`intelligence/`) and raw (`_raw/`) files following the conventions in CLAUDE.md.

---

## Phase 10: Connect the Graph

After initial population:

1. **Parse YAML frontmatter** from all intelligence files to build reverse indexes:
   - For each person in `people:` field -- find their `teams/` file
   - For each project in `projects:` field -- find the project file
2. **Add `## Related Intelligence` sections** to team files and project files with wiki-links back to the intelligence files that reference them.
3. **Add inline links** in context files to team files where people are mentioned.
4. **Verify in Obsidian** -- open the graph view and check for orphans. Connect any remaining disconnected files.

---

## Phase 11: Verify Everything Works

Run each component manually once:

1. **Intelligence sync**: Trigger it and verify it pulls recent meetings/emails, creates files in the right locations with proper frontmatter, and propagates updates.
2. **Daily wrap-up**: Trigger it and verify it reads today's intelligence and produces a well-structured daily digest.
3. **Weekly sync**: Trigger it and verify it creates a weekly file from the template, syncs open items, and preserves the manual section.
4. **Graph view**: Open Obsidian's graph view and verify the files are connected.
5. **Query test**: Ask Claude a broad question (e.g., "Tell me about {PERSON}") and verify graph traversal works across teams, intelligence, and projects.

---

## Maintenance Notes

- The vault is self-maintaining once the three scheduled tasks are running
- The user should spend 5-10 minutes per day in the weekly file, distributing open items into their day plan and checking off completed ones
- Context files evolve slowly -- update when the user says "remember this"
- Project files evolve through intelligence propagation -- the daily wrap-up flags when projects need attention
- Team files grow automatically as intelligence links accumulate
- Periodically check the Obsidian graph for orphans and connect them
