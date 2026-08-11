---
name: second-brain-setup
description: Configure a private Second Brain 2.0 vault, authorized source adapters, modular automations, Obsidian planning, and validation.
---

# Second Brain setup

Use the copied private `vault/` directory, not the public template repository, as `{VAULT_ROOT}`.

## 1. Discover the operating context

Gather only what is needed to build useful hubs:

- user identity, role, timezone, and writing preferences
- three to seven active projects
- team and recurring stakeholders
- approved source systems and account identities
- desired planning time and acceptable automation cadence
- private or regulated topics that must never enter automated ingestion

## 2. Personalize the vault

Replace `{USER_FULL_NAME}`, `{USER_FIRST_NAME}`, and `{VAULT_FOLDER_NAME}` in `AGENTS.md` and context templates. Create project and people hubs only from confirmed information.

Create the current year/month directories under `intelligence/`, `_raw/`, and the relevant `documents/` kinds.

## 3. Configure source adapters

For every enabled source record:

- stable ID and raw retrieval method
- authorization or mailbox guard
- finalized/ready criteria
- cursor and persistent backlog location
- strict and backstop windows
- per-run cap

Test each source read-only. Do not enable a source merely because an integration exists.

## 4. Configure Obsidian

Install Tasks and Task List Kanban. Copy the `weekly-kanban-overview` skill into the agent skill directory. Run its script with `--dry-run` against a fixture or an existing weekly board before enabling automation.

## 5. Configure QMD

Register the private vault as one collection, embed it, and verify status. Keep the index outside the public repository.

## 6. Create automations

Use the product's automation tool. The examples under `automations/templates/` are references, not secrets-ready files. Start paused, run on demand, inspect output, then activate exactly one job per module.

Recommended starting cadence:

- intelligence sync: weekdays once or twice daily
- document radar: after intelligence sync
- daily wrap-up: Monday, Wednesday, Friday
- weekly Kanban: Friday before planning
- QMD reindex: every two days
- health check: weekly

## 7. Backfill carefully

Start with a small date window. Process meetings and substantive email with stable-ID deduplication. Do not backfill noisy chat until current ingestion is healthy. Run QMD only after files have been verified.

## 8. Validate

- source adapters: eligible, covered, pending, and failed counts reconcile
- raw and processed pairs exist and link correctly
- project and people propagation links back to evidence
- weekly carry-forward lands on Monday
- exactly one active automation exists per module
- QMD collection points to the private vault
- no private data has entered the template repository
