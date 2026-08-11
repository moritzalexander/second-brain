#!/usr/bin/env python3
"""Read finalized Wispr Flow meetings without modifying Wispr's local data."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


DEFAULT_SOURCE_ROOT = Path.home() / "Library" / "Application Support" / "Wispr Flow"
REQUIRED_MEETING_COLUMNS = {
    "id",
    "title",
    "createdAt",
    "modifiedAt",
    "finalized",
    "isDeleted",
    "calendarEventExternalId",
    "participantNames",
    "speakerMap",
    "refineStatus",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Discover or render finalized Wispr Flow meeting transcripts."
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        default=DEFAULT_SOURCE_ROOT,
        help="Wispr Flow application-support folder.",
    )
    parser.add_argument(
        "--timezone",
        default="local",
        help="IANA timezone for meeting dates, or 'local' for the Mac timezone.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("check", help="Validate the source and report readiness counts.")

    list_parser = subparsers.add_parser("list", help="List meetings without transcript text.")
    list_parser.add_argument(
        "--since",
        required=True,
        help="Inclusive local date or ISO timestamp, for example 2026-08-01.",
    )

    render_parser = subparsers.add_parser(
        "render", help="Render one finalized refined transcript as canonical raw Markdown."
    )
    render_parser.add_argument("--meeting-id", required=True)
    render_parser.add_argument(
        "--output",
        type=Path,
        help="Optional output path. Existing files are never overwritten.",
    )
    return parser.parse_args()


def local_timezone(name: str):
    if name == "local":
        return datetime.now().astimezone().tzinfo
    return ZoneInfo(name)


def parse_datetime(value: str) -> datetime:
    normalized = value.strip().replace("Z", "+00:00").replace(" +00:00", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def parse_since(value: str, tz) -> datetime:
    try:
        parsed_date = date.fromisoformat(value)
    except ValueError:
        parsed = parse_datetime(value)
        return parsed.astimezone(timezone.utc)
    return datetime.combine(parsed_date, time.min, tzinfo=tz).astimezone(timezone.utc)


def open_database(source_root: Path) -> sqlite3.Connection:
    database = (source_root / "flow.sqlite").expanduser().resolve()
    transcript_root = source_root / "meetings"
    if not database.is_file():
        raise SystemExit(f"Wispr Flow database not found: {database}")
    if not transcript_root.is_dir():
        raise SystemExit(f"Wispr Flow transcript folder not found: {transcript_root}")
    connection = sqlite3.connect(f"{database.as_uri()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only = ON")
    columns = {
        row[1] for row in connection.execute("PRAGMA table_info(Meetings)").fetchall()
    }
    missing = sorted(REQUIRED_MEETING_COLUMNS - columns)
    if missing:
        connection.close()
        raise SystemExit(
            "Wispr Flow schema changed; missing Meetings columns: " + ", ".join(missing)
        )
    return connection


def load_json(value: str | None, fallback: Any) -> Any:
    if not value:
        return fallback
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback


def refined_transcript(source_root: Path, meeting_id: str) -> Path:
    return source_root / "meetings" / meeting_id / "refined.ndjson"


def count_segments(path: Path) -> int:
    if not path.is_file():
        return 0
    count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict) and str(item.get("text") or "").strip():
                count += 1
    return count


def meeting_rows(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, title, createdAt, modifiedAt, finalized, isDeleted,
               endedAt, calendarEventExternalId, participantNames,
               notes, summary, speakerMap, refineStatus, shareSlug
        FROM Meetings
        WHERE isDeleted = 0
        ORDER BY createdAt ASC
        """
    ).fetchall()


def manifest_item(row: sqlite3.Row, source_root: Path, tz) -> dict[str, Any]:
    created_utc = parse_datetime(row["createdAt"]).astimezone(timezone.utc)
    transcript = refined_transcript(source_root, row["id"])
    segment_count = count_segments(transcript)
    ready = bool(row["finalized"] and row["refineStatus"] == "complete" and segment_count)
    ended_at_utc = None
    if row["endedAt"]:
        ended_at_utc = datetime.fromtimestamp(
            int(row["endedAt"]) / 1000, tz=timezone.utc
        ).isoformat()
    return {
        "wispr_meeting_id": row["id"],
        "title": row["title"],
        "meeting_date": created_utc.astimezone(tz).date().isoformat(),
        "created_at_utc": created_utc.isoformat(),
        "ended_at_utc": ended_at_utc,
        "calendar_event_id": row["calendarEventExternalId"],
        "participants": load_json(row["participantNames"], []),
        "finalized": bool(row["finalized"]),
        "refine_status": row["refineStatus"],
        "transcript_variant": "refined" if segment_count else None,
        "transcript_segments": segment_count,
        "ready": ready,
        "has_notes": bool(row["notes"]),
        "has_summary": bool(row["summary"]),
    }


def speaker_lookup(speaker_map_text: str | None) -> dict[str, str]:
    speaker_map = load_json(speaker_map_text, {})
    people = speaker_map.get("people", {}) if isinstance(speaker_map, dict) else {}
    assignments = speaker_map.get("assignments", {}) if isinstance(speaker_map, dict) else {}
    result: dict[str, str] = {}
    for speaker_id, assignment in assignments.items():
        if not isinstance(assignment, dict):
            continue
        person_id = assignment.get("consensus")
        person = people.get(person_id, {}) if person_id else {}
        name = person.get("name") if isinstance(person, dict) else None
        if name:
            result[str(speaker_id)] = str(name)
    return result


def timestamp_label(value: Any) -> str:
    text = str(value or "").strip()
    parts = text.split(":")
    if len(parts) == 2:
        return f"00:{text}"
    if len(parts) == 3:
        return text
    return text or "00:00:00"


def transcript_segments(path: Path, speaker_names: dict[str, str]) -> list[str]:
    rendered: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(item, dict):
                continue
            text = str(item.get("text") or "").strip()
            if not text:
                continue
            speaker = item.get("speaker")
            speaker_id = None
            embedded_name = None
            if isinstance(speaker, dict):
                speaker_id = speaker.get("id")
                embedded_name = speaker.get("name")
            elif speaker is not None:
                speaker_id = speaker
            label = embedded_name or speaker_names.get(str(speaker_id))
            if not label:
                label = f"Speaker {speaker_id}" if speaker_id is not None else "Unknown speaker"
            clean_text = " ".join(text.replace("\r", "\n").splitlines())
            rendered.append(
                f"[{timestamp_label(item.get('timestamp'))}] {label}: {clean_text}"
            )
    return rendered


def yaml_string(value: Any) -> str:
    return json.dumps("" if value is None else str(value), ensure_ascii=False)


def render_markdown(row: sqlite3.Row, source_root: Path, tz) -> str:
    item = manifest_item(row, source_root, tz)
    if not item["ready"]:
        raise SystemExit(
            "Meeting is not ready: require finalized=1, refineStatus=complete, "
            "and a non-empty refined.ndjson transcript"
        )
    transcript = refined_transcript(source_root, row["id"])
    segments = transcript_segments(transcript, speaker_lookup(row["speakerMap"]))
    participants = ", ".join(item["participants"]) or "Unknown"
    title = " ".join(str(row["title"] or "Untitled meeting").splitlines())
    calendar_event_id = item["calendar_event_id"] or ""
    return (
        "---\n"
        f"date: {item['meeting_date']}\n"
        "source: wispr_flow\n"
        "type: meeting\n"
        f"wispr_meeting_id: {yaml_string(row['id'])}\n"
        f"wispr_calendar_event_id: {yaml_string(calendar_event_id)}\n"
        "wispr_transcript_variant: refined\n"
        f"created_at_utc: {yaml_string(item['created_at_utc'])}\n"
        f"ended_at_utc: {yaml_string(item['ended_at_utc'] or '')}\n"
        "---\n\n"
        f"# Raw Transcript — {title} — {item['meeting_date']}\n\n"
        "## Wispr Flow Metadata\n"
        f"- Meeting ID: {row['id']}\n"
        f"- Calendar event ID: {calendar_event_id or 'Not available'}\n"
        f"- Participants: {participants}\n"
        "- Transcript variant: refined\n\n"
        "## Transcript\n"
        + "\n".join(segments)
        + "\n"
    )


def command_check(connection: sqlite3.Connection, source_root: Path, tz) -> int:
    rows = meeting_rows(connection)
    items = [manifest_item(row, source_root, tz) for row in rows]
    print(
        json.dumps(
            {
                "source_root": str(source_root),
                "database_read_only": True,
                "refined_transcript_root_readable": True,
                "meetings_total": len(items),
                "meetings_ready": sum(1 for item in items if item["ready"]),
                "meetings_pending": sum(
                    1 for item in items if not item["ready"] and not item["finalized"]
                ),
                "finalized_without_refined_transcript": sum(
                    1 for item in items if item["finalized"] and not item["ready"]
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def command_list(
    connection: sqlite3.Connection, source_root: Path, tz, since: str
) -> int:
    since_utc = parse_since(since, tz)
    items = [
        manifest_item(row, source_root, tz)
        for row in meeting_rows(connection)
        if parse_datetime(row["createdAt"]).astimezone(timezone.utc) >= since_utc
    ]
    print(json.dumps(items, ensure_ascii=False, indent=2))
    return 0


def command_render(
    connection: sqlite3.Connection,
    source_root: Path,
    tz,
    meeting_id: str,
    output: Path | None,
) -> int:
    row = connection.execute(
        """
        SELECT id, title, createdAt, modifiedAt, finalized, isDeleted,
               endedAt, calendarEventExternalId, participantNames,
               notes, summary, speakerMap, refineStatus, shareSlug
        FROM Meetings
        WHERE id = ? AND isDeleted = 0
        """,
        (meeting_id,),
    ).fetchone()
    if row is None:
        raise SystemExit(f"Wispr Flow meeting not found: {meeting_id}")
    markdown = render_markdown(row, source_root, tz)
    if output is None:
        sys.stdout.write(markdown)
        return 0
    destination = output.expanduser().resolve()
    if destination.exists():
        raise SystemExit(f"Refusing to overwrite existing file: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(markdown, encoding="utf-8")
    print(destination)
    return 0


def main() -> int:
    args = parse_args()
    source_root = args.source_root.expanduser().resolve()
    tz = local_timezone(args.timezone)
    connection = open_database(source_root)
    try:
        if args.command == "check":
            return command_check(connection, source_root, tz)
        if args.command == "list":
            return command_list(connection, source_root, tz, args.since)
        if args.command == "render":
            return command_render(
                connection, source_root, tz, args.meeting_id, args.output
            )
    finally:
        connection.close()
    raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
