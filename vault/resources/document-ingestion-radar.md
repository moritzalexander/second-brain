---
name: document-radar
description: Discover and refresh reusable document records using stable file IDs and live modification timestamps while preserving manual context.
---

# Document radar

Work in `{VAULT_ROOT}`. Inspect recently created, modified, viewed, commented, or context-linked files from approved document sources.

## Include

- decision documents and maintained project plans
- reusable slide decks, briefs, spreadsheets, and reference material
- customer-facing assets and source documents needed for future work

## Exclude by default

- generated meeting notes and transcript exports already covered by intelligence sync
- personal files unrelated to an existing topic
- duplicates, low-signal attachments, and temporary exports

## Processing

1. Continue the oldest deferred high-value file first.
2. Discover recent candidates.
3. Deduplicate by stable file ID.
4. Compare live modification time with the record's `updated_at`.
5. For a new file, create a record under `documents/{kind}/YYYY/MM/`.
6. For a changed file, refresh source metadata and source-content sections while preserving useful manual context.
7. If extraction fails, keep the prior record intact and leave the file pending.
8. Link conservatively to known projects and people.

The source content comes before generated retrieval context. End with counts for new, refreshed, unchanged, skipped, failed, and deferred files.
