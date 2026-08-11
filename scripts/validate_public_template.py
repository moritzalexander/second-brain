#!/usr/bin/env python3
"""Validate repository structure and catch common private-vault leaks."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "README.md",
    "docs/architecture.md",
    "docs/privacy-and-security.md",
    "vault/AGENTS.md",
    "vault/resources/intelligence-sync-skill.md",
    "skills/weekly-kanban-overview/SKILL.md",
    "skills/weekly-kanban-overview/scripts/prepare_weekly_overview.py",
    "adapters/wispr-flow/wispr_flow_meetings.py",
}
ALLOWED_KNOWLEDGE_FILES = {
    "vault/daily/.gitkeep",
    "vault/daily/Archive/.gitkeep",
    "vault/intelligence/.gitkeep",
    "vault/intelligence/_raw/.gitkeep",
    "vault/documents/.gitkeep",
    "vault/documents/_raw/.gitkeep",
    "vault/documents/docs/.gitkeep",
    "vault/documents/presentations/.gitkeep",
    "vault/documents/spreadsheets/.gitkeep",
}
KNOWLEDGE_PREFIXES = ("vault/daily/", "vault/intelligence/", "vault/documents/")
TEXT_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".toml", ".example", ".txt"}
FORBIDDEN_PATTERNS = {
    "local macOS home path": re.compile("/" + r"Users/[^/{\s`]+/"),
    "email address": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "private database file": re.compile(r"\b(?:ChatStorage|state_\d+|logs_\d+|index)\.sqlite\b"),
}


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return sorted(set(result.stdout.splitlines()))


def skill_frontmatter_errors(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        return [f"{path.relative_to(ROOT)}: missing YAML frontmatter"]
    end = text.find("\n---\n", 4)
    keys = []
    for line in text[4:end].splitlines():
        match = re.match(r"^([A-Za-z0-9_-]+):", line)
        if match:
            keys.append(match.group(1))
    if set(keys) != {"name", "description"}:
        return [f"{path.relative_to(ROOT)}: SKILL.md frontmatter must contain only name and description"]
    return []


def main() -> int:
    errors: list[str] = []
    files = tracked_files()
    missing = sorted(REQUIRED - set(files))
    errors.extend(f"missing required file: {path}" for path in missing)

    for relative in files:
        if relative.startswith(KNOWLEDGE_PREFIXES) and relative not in ALLOWED_KNOWLEDGE_FILES:
            errors.append(f"operational knowledge file is tracked: {relative}")
        path = ROOT / relative
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in FORBIDDEN_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{relative}: contains {label}")

    for relative in files:
        if relative.endswith("/SKILL.md"):
            errors.extend(skill_frontmatter_errors(ROOT / relative))

    if errors:
        print("Public-template validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Public-template validation passed for {len(files)} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
