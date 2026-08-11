---
name: qmd-reindex
description: Refresh and verify the existing QMD collection for a private Second Brain vault without destructive recovery or duplicate indexes.
---

# QMD reindex

Configuration:

- collection: `{QMD_COLLECTION}`
- vault: `{VAULT_ROOT}`
- QMD cache and config directories: use the existing local installation

Run in this order:

1. `qmd status -c {QMD_COLLECTION}`
2. `qmd update -c {QMD_COLLECTION}`
3. `qmd embed -c {QMD_COLLECTION}`
4. `qmd status -c {QMD_COLLECTION}`

Confirm the collection still points at the intended private vault. Report files indexed, vectors, additions, updates, and errors. Do not run cleanup, delete the index, or create a second index as an automatic recovery step.
