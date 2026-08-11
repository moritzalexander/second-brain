# Wispr Flow meeting adapter

`wispr_flow_meetings.py` reads finalized refined meeting transcripts from Wispr Flow's local macOS application-support directory. It does not write to Wispr Flow.

Use `--source-root` if the application data is not at the default location.

```bash
python3 adapters/wispr-flow/wispr_flow_meetings.py check
python3 adapters/wispr-flow/wispr_flow_meetings.py list --since 2026-04-01
python3 adapters/wispr-flow/wispr_flow_meetings.py render --meeting-id SOURCE_ID
```

Ingest a meeting only when it is not deleted, is finalized, has completed refinement, and has a non-empty refined transcript. Leave unfinished items pending. The renderer produces a canonical Markdown raw record with source metadata and timestamped speaker segments.

Wispr Flow's local schema is not a public stability contract. Run `check` after application updates and fail closed if required columns or transcript files are unavailable.
