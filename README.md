# Second Brain

A persistent knowledge vault that gives AI agents full context across conversations.

Second Brain turns Claude Code into a long-term memory system. It continuously ingests your meetings, emails, and Slack messages, processes them into structured intelligence files, and connects everything through a graph of wiki-links. The result: Claude always knows what you discussed, decided, and need to do next.

---

## How It Works

```
You work normally                    Three agents run in the background
  Meetings (Granola)  ──┐
  Emails (Gmail)      ──┼──▶  Intelligence Sync (hourly)
  Slack messages      ──┘         │
                                  ▼
                           Processed intelligence files
                           (tagged, linked, cross-referenced)
                                  │
                                  ▼
                           Daily Wrap-up (5 PM)
                           (synthesized digest by project)
                                  │
                                  ▼
                           Weekly Sync (5:25 PM)
                           (open items → weekly plan)
```

The vault lives as a folder of markdown files you can browse in [Obsidian](https://obsidian.md). Claude reads the vault at the start of every conversation, giving it full context about who you are, what you're working on, and what happened recently.

## Vault Structure

```
your-vault/
├── CLAUDE.md              ← Navigation and operating rules for Claude
├── context/               ← Who you are, your company, strategy, preferences
├── daily/                 ← Synthesized daily digests and weekly plans
├── intelligence/          ← Processed meetings, emails, Slack threads
│   └── _raw/              ← Full raw transcripts
├── projects/              ← Active projects with status, decisions, open questions
├── resources/             ← Templates, frameworks, agent skill files
└── teams/                 ← One file per person you work with
```

Everything is connected through `[[wiki-links]]`. When Claude needs to answer "Tell me about Project X," it doesn't just grep -- it follows the link graph from the project file through related intelligence, team profiles, and strategic context.

---

## Prerequisites

1. **[Claude Code](https://docs.anthropic.com/en/docs/claude-code)** installed and working
2. **[Obsidian](https://obsidian.md)** installed (for browsing and editing vault files)
3. **MCP servers** connected in Claude Code:
   - **Gmail** -- for email intelligence
   - **[Granola](https://granola.ai)** -- for meeting transcripts
   - **Slack** -- for Slack messages and threads
   - **Google Calendar** (optional) -- for schedule-aware context

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/second-brain.git
cd second-brain
```

### 2. Copy the vault template to your preferred location

```bash
cp -r vault/ ~/path/to/your/vault
```

Pick a location that syncs across devices (Google Drive, iCloud, Dropbox) so you can browse in Obsidian from anywhere.

### 3. Run the interactive setup

Open Claude Code in the vault directory and run the setup skill:

```
cd ~/path/to/your/vault
claude
```

Then tell Claude:

```
Read and follow the instructions in resources/setup-skill.md to set up my Second Brain.
```

The setup skill will:
- Ask you about your role, team, projects, and stakeholders
- Generate your personalized `CLAUDE.md`
- Create context files, team profiles, and project files
- Set up the three automated agents (intelligence sync, daily wrap-up, weekly sync)
- Do an initial backfill of your recent meetings and emails
- Connect the wiki-link graph

The whole process takes about 15-20 minutes.

### 4. Open in Obsidian

Open your vault folder in Obsidian. Enable the Graph View to see how your files are connected.

### 5. Verify the agents

The setup will have created three scheduled tasks in Claude Code:
- **intelligence-sync** -- runs every hour, pulls new meetings/emails/Slack
- **daily-wrapup** -- runs at 5 PM weekdays, synthesizes the day
- **weekly-sync** -- runs at 5:25 PM weekdays, builds/updates weekly plan

Check they're running: in Claude Code, run `/tasks` to see scheduled tasks.

---

## Daily Usage

Once set up, the vault is mostly self-maintaining:

- **Morning:** Open your weekly file (`daily/YYYY-Www.md`) in Obsidian. Review the auto-synced open items and distribute them into your day plan in the manual section.
- **During the day:** Just work normally. Attend meetings, send emails, chat on Slack. The intelligence sync picks everything up.
- **End of day:** Read your daily digest (`daily/YYYY-MM-DD.md`) for a synthesized overview. Check off completed items in the weekly file.
- **Anytime:** Ask Claude questions with full context: "What did we decide about X?", "Prepare me for my meeting with Y", "What's the status of Project Z?"

## Asking Questions

Claude uses two search strategies depending on your question:

- **Flat search** (grep) -- for narrow lookups: "What did Alice say about pricing on Thursday?"
- **Graph traversal** -- for broad context: "Tell me everything about the customer acceleration project" or "Prepare me for a meeting with Bob"

Graph traversal follows wiki-links across files, reading first-degree and second-degree connections to build a complete picture.

---

## Customization

### Adding a new intelligence source

Edit `resources/intelligence-sync-skill.md` to add new data sources. The processing format and file naming conventions are documented in `CLAUDE.md`.

### Changing agent schedules

In Claude Code, use the scheduled tasks tools to update cron expressions:
- Every 30 minutes: `*/30 * * * *`
- Every 2 hours during business hours: `0 9,11,13,15,17 * * 1-5`

### Adding context files

Create new files in `context/` for any slow-changing background information Claude should know: company strategy, competitive landscape, org structure, etc. The setup skill creates initial ones, but you can add more anytime.

### Writing preferences

Add communication rules to `context/writing-preferences.md`. Examples:
- "Never use em dashes"
- "Always use bullet points over paragraphs"
- "Match the tone of the recipient"

---

## Architecture

See [docs/architecture.md](docs/architecture.md) for a deep dive into:
- The three-agent processing pipeline
- File naming and frontmatter conventions
- Graph traversal procedure
- Propagation rules (how intelligence updates flow to projects, teams, and context)
- Weekly sync merge logic (preserving user triage)

---

## Requirements

- Claude Code with Claude Opus or Sonnet
- MCP servers for your data sources
- ~5-10 minutes/day for weekly planning (optional but recommended)

## License

MIT -- see [LICENSE](LICENSE).
