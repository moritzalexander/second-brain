#!/usr/bin/env python3
"""Create or merge next week's weekly Kanban baseline and archive old planning files."""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path


WEEK_FILE_RE = re.compile(r"^(\d{4})-W(\d{2})(.*)\.md$")
DATE_FILE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")
ROOT_TASK_RE = re.compile(r"^- \[([^\]])\] (.+)$")
CHILD_TASK_RE = re.compile(r"^(\s+)- \[([^\]])\] (.+)$")
OPEN_STATES = {" ", "/", "!", "?", ">"}
DAY_ORDER = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4}
MONDAY_TAG = "#plan/day/mon"


@dataclass
class TaskBlock:
    state: str
    lines: list[str]

    @property
    def root(self) -> str:
        return self.lines[0]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", required=True, type=Path)
    parser.add_argument("--today", type=date.fromisoformat, default=date.today())
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def monday_for_iso_week(year: int, week: int) -> date:
    return date.fromisocalendar(year, week, 1)


def next_monday(day: date) -> date:
    return day + timedelta(days=7 - day.weekday())


def week_id(day: date) -> str:
    year, week, _ = day.isocalendar()
    return f"{year}-W{week:02d}"


def split_frontmatter(text: str) -> tuple[list[str], str]:
    if not text.startswith("---\n"):
        return [], text
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("Unclosed YAML frontmatter")
    return text[4:end].splitlines(), text[end + 5 :]


def update_frontmatter(lines: list[str], values: dict[str, str]) -> list[str]:
    result = list(lines)
    seen: set[str] = set()
    for index, line in enumerate(result):
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match or match.group(1) not in values:
            continue
        key = match.group(1)
        result[index] = f"{key}: {values[key]}"
        seen.add(key)
    for key, value in values.items():
        if key not in seen:
            result.append(f"{key}: {value}")
    return result


def render_frontmatter(lines: list[str]) -> str:
    return "---\n" + "\n".join(lines) + "\n---\n\n"


def extract_task_blocks(body: str) -> list[TaskBlock]:
    lines = body.splitlines()
    blocks: list[TaskBlock] = []
    index = 0
    while index < len(lines):
        match = ROOT_TASK_RE.match(lines[index])
        if not match:
            index += 1
            continue
        end = index + 1
        while end < len(lines) and not ROOT_TASK_RE.match(lines[end]):
            if lines[end].startswith("## "):
                break
            end += 1
        block_lines = lines[index:end]
        while block_lines and block_lines[-1] == "":
            block_lines.pop()
        blocks.append(TaskBlock(match.group(1), block_lines))
        index = end
    return blocks


def visible_task_key(task_line: str) -> str:
    match = re.match(r"^\s*- \[[^\]]\]\s+(.+)$", task_line)
    value = match.group(1) if match else task_line
    value = re.sub(r"\s+#plan/(?:project|day)/\S+", "", value)
    value = re.sub(r"\s+#weekly-starred(?=\s|$)", "", value)
    value = re.sub(r"\s+\^[A-Za-z0-9-]+\s*$", "", value)
    return re.sub(r"\s+", " ", value).strip().casefold()


def inherited_tag(root: str, prefix: str) -> str | None:
    match = re.search(rf"#plan/{prefix}/\S+", root)
    return match.group(0) if match else None


def move_block_to_monday(block: TaskBlock) -> TaskBlock:
    root = re.sub(r"\s+#plan/day/\S+", "", block.root)
    block_id = re.search(r"(\s+\^[A-Za-z0-9-]+)\s*$", root)
    if block_id:
        root = root[: block_id.start()].rstrip() + f" {MONDAY_TAG}" + block_id.group(1)
    else:
        root = root.rstrip() + f" {MONDAY_TAG}"
    return TaskBlock(block.state, [root, *block.lines[1:]])


def promote_open_children(block: TaskBlock) -> list[TaskBlock]:
    project = inherited_tag(block.root, "project")
    day = inherited_tag(block.root, "day")
    promoted: list[TaskBlock] = []
    for line in block.lines[1:]:
        match = CHILD_TASK_RE.match(line)
        if not match or match.group(2) not in OPEN_STATES:
            continue
        content = match.group(3).strip()
        if project and "#plan/project/" not in content:
            content += f" {project}"
        if day and "#plan/day/" not in content:
            content += f" {day}"
        promoted.append(TaskBlock(match.group(2), [f"- [{match.group(2)}] {content}"]))
    return promoted


def carry_forward_blocks(source_body: str) -> list[TaskBlock]:
    carried: list[TaskBlock] = []
    seen: set[str] = set()
    for block in extract_task_blocks(source_body):
        candidates = [block] if block.state in OPEN_STATES else promote_open_children(block)
        for candidate in candidates:
            candidate = move_block_to_monday(candidate)
            key = visible_task_key(candidate.root)
            if not key or key in seen:
                continue
            seen.add(key)
            carried.append(candidate)
    return carried


def task_sort_key(block: TaskBlock) -> tuple[int, str]:
    match = re.search(r"#plan/day/(mon|tue|wed|thu|fri)\b", block.root, re.I)
    day = DAY_ORDER.get(match.group(1).lower(), 5) if match else 5
    return day, visible_task_key(block.root)


def heading(start: date, end: date) -> str:
    if start.month == end.month:
        return f"# Week of {start.strftime('%B')} {start.day}-{end.day}, {start.year}"
    return f"# Week of {start.strftime('%B')} {start.day}-{end.strftime('%B')} {end.day}, {end.year}"


def source_week_from_path(path: Path) -> str:
    match = re.match(r"^(\d{4}-W\d{2})-kanban(?:-tasks)?\.md$", path.name)
    if not match:
        raise ValueError(f"Cannot determine source week from {path.name}")
    return match.group(1)


def latest_source(daily: Path, suffix: str, target_start: date) -> Path | None:
    candidates: list[tuple[date, Path]] = []
    for path in daily.glob(f"????-W??-{suffix}.md"):
        match = WEEK_FILE_RE.match(path.name)
        if not match:
            continue
        monday = monday_for_iso_week(int(match.group(1)), int(match.group(2)))
        if monday < target_start:
            candidates.append((monday, path))
    return max(candidates, default=(None, None), key=lambda item: item[0])[1]


def render_new_tasks(source_text: str, target_start: date, blocks: list[TaskBlock]) -> str:
    frontmatter, _ = split_frontmatter(source_text)
    target_end = target_start + timedelta(days=4)
    target_week = week_id(target_start)
    frontmatter = update_frontmatter(
        frontmatter,
        {"week": target_week, "start": target_start.isoformat(), "end": target_end.isoformat()},
    )
    intro = (
        f"{heading(target_start, target_end)}\n\n"
        "Carry-forward tasks plus short, high-confidence context cues. Calendar preparation appears one working day before the meeting. "
        "Add, edit, move, complete, link, or star tasks from the Kanban board.\n\n"
        "## Context cues\n"
    )
    rendered = "\n\n".join("\n".join(block.lines) for block in sorted(blocks, key=task_sort_key))
    return render_frontmatter(frontmatter) + intro + ("\n\n" + rendered if rendered else "\n") + "\n"


def merge_missing_blocks(target_text: str, blocks: list[TaskBlock]) -> tuple[str, int]:
    body = split_frontmatter(target_text)[1]
    existing = {visible_task_key(block.root) for block in extract_task_blocks(body)}
    missing = [block for block in blocks if visible_task_key(block.root) not in existing]
    if not missing:
        return target_text, 0
    separator = "" if target_text.endswith("\n\n") else "\n" if target_text.endswith("\n") else "\n\n"
    addition = "\n\n".join("\n".join(block.lines) for block in sorted(missing, key=task_sort_key))
    return target_text + separator + addition + "\n", len(missing)


def archive_old_planning_files(daily: Path, today: date, dry_run: bool) -> list[tuple[Path, Path]]:
    archive = daily / "Archive"
    current_monday = today - timedelta(days=today.weekday())
    threshold = current_monday - timedelta(weeks=1)
    moves: list[tuple[Path, Path]] = []
    for source in sorted(daily.glob("*.md")):
        week_match = WEEK_FILE_RE.match(source.name)
        date_match = DATE_FILE_RE.match(source.name)
        if week_match:
            source_date = monday_for_iso_week(int(week_match.group(1)), int(week_match.group(2)))
        elif date_match:
            source_date = date.fromisoformat(date_match.group(1))
        else:
            continue
        if source_date >= threshold:
            continue
        destination = archive / source.name
        if destination.exists():
            digest = hashlib.sha256(source.read_bytes()).hexdigest()[:8]
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            destination = archive / f"{source.stem}-archived-{stamp}-{digest}{source.suffix}"
        moves.append((source, destination))
        if not dry_run:
            archive.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
    return moves


def main() -> int:
    args = parse_args()
    vault = args.vault.expanduser().resolve()
    daily = vault / "daily"
    if not daily.is_dir():
        raise SystemExit(f"Missing daily folder: {daily}")

    target_start = next_monday(args.today)
    target_end = target_start + timedelta(days=4)
    target_week = week_id(target_start)
    source_tasks = latest_source(daily, "kanban-tasks", target_start)
    source_board = latest_source(daily, "kanban", target_start)
    if source_tasks is None:
        source_task_text = (
            Path(__file__).resolve().parent.parent / "assets" / "weekly-kanban-tasks.md"
        ).read_text(encoding="utf-8")
        source_label = "skills/weekly-kanban-overview/assets/weekly-kanban-tasks.md"
    else:
        source_task_text = source_tasks.read_text(encoding="utf-8")
        source_label = str(source_tasks.relative_to(vault))
    _, source_body = split_frontmatter(source_task_text)
    carried = carry_forward_blocks(source_body)

    target_tasks = daily / f"{target_week}-kanban-tasks.md"
    target_board = daily / f"{target_week}-kanban.md"
    created_tasks = False
    created_board = False
    merged_count = 0

    if target_tasks.exists():
        merged_text, merged_count = merge_missing_blocks(target_tasks.read_text(encoding="utf-8"), carried)
        if merged_count and not args.dry_run:
            target_tasks.write_text(merged_text, encoding="utf-8")
    else:
        created_tasks = True
        if not args.dry_run:
            target_tasks.write_text(render_new_tasks(source_task_text, target_start, carried), encoding="utf-8")

    if not target_board.exists():
        created_board = True
        if source_board is not None:
            source_week = source_week_from_path(source_board)
            board_text = source_board.read_text(encoding="utf-8").replace(source_week, target_week)
        else:
            template = Path(__file__).resolve().parent.parent / "assets" / "weekly-kanban-board.md"
            board_text = template.read_text(encoding="utf-8").replace("{WEEK_ID}", target_week)
        if not args.dry_run:
            target_board.write_text(board_text, encoding="utf-8")

    archive_moves = archive_old_planning_files(daily, args.today, args.dry_run)

    mode = "DRY RUN" if args.dry_run else "DONE"
    print(f"{mode}: prepared {target_week} ({target_start} to {target_end})")
    print(f"Source: {source_label}")
    print(f"Open cards carried: {len(carried)}")
    task_action = "would create" if args.dry_run and created_tasks else "created" if created_tasks else "merged"
    board_action = "would create" if args.dry_run and created_board else "created" if created_board else "kept"
    print(f"Task file: {task_action} {target_tasks.relative_to(vault)}")
    print(f"Missing cards merged: {merged_count}")
    print(f"Board file: {board_action} {target_board.relative_to(vault)}")
    print(f"Archived files: {len(archive_moves)}")
    for source, destination in archive_moves:
        print(f"  {source.relative_to(vault)} -> {destination.relative_to(vault)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
