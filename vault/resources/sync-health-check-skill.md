---
name: sync-health-check
description: Audit Second Brain automation execution, source coverage, backlogs, document freshness, and QMD health without declaring success from logs alone.
---

# Sync health check

Work in `{VAULT_ROOT}`.

## Execution checks

- exactly one active automation exists for each enabled module
- schedules match the intended timezone and cadence
- the most recent expected runs completed with a final result
- zero-token, connection, or permission failures are investigated
- dependent jobs do not overlap in the wrong order

## Coverage checks

For each enabled source, compare recent eligible stable IDs with:

- IDs covered by raw or processed records
- IDs in a persistent pending backlog
- IDs explicitly skipped with a reason
- missing IDs

Report the reconciliation. Do not infer coverage from the newest file date.

Also check:

- document records against live modification timestamps
- weekly board filter and target task file
- QMD collection path, file count, vectors, and last refresh
- duplicate active jobs and timezone drift

Only report “healthy” when execution and coverage both pass. Repair only an unambiguous in-scope schedule, duplicate, or status defect; otherwise report the blocker and required action.
