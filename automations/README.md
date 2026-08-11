# Automation templates

These files document a safe starting configuration for Codex automations. They are examples, not installable secrets-ready files.

Replace every `{PLACEHOLDER}`, choose the correct project target, use the product's automation tool to create the job, and keep it paused until an on-demand run has been inspected.

The recurrence rule is interpreted in the automation's local timezone. Verify the effective time after creation.

Suggested order:

1. intelligence sync
2. document radar
3. daily wrap-up
4. weekly Kanban
5. QMD reindex
6. sync health check

Keep exactly one active job per enabled module.
