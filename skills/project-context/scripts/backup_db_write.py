#!/usr/bin/env python3
"""
Write backup/change records into a local SQLite database.

Example:
  python backup_db_write.py \
    --summary "Update skill docs" \
    --source codex \
    --repo-changes yes \
    --item ".agent/skills/project-context/SKILL.md|.agent/skills/project-context/backup/SKILL.md.bak_20260309|update"
"""

from __future__ import annotations

import argparse
import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = SKILL_ROOT / "backup_log.db"


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        PRAGMA journal_mode = WAL;
        CREATE TABLE IF NOT EXISTS backup_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            source TEXT NOT NULL,
            summary TEXT NOT NULL,
            repo_changes INTEGER NOT NULL CHECK (repo_changes IN (0,1)),
            note TEXT
        );

        CREATE TABLE IF NOT EXISTS backup_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            backup_path TEXT,
            action TEXT NOT NULL DEFAULT 'update',
            file_hash TEXT,
            file_size INTEGER,
            FOREIGN KEY(event_id) REFERENCES backup_events(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_backup_events_created_at
            ON backup_events(created_at);
        CREATE INDEX IF NOT EXISTS idx_backup_files_event_id
            ON backup_files(event_id);
        """
    )


def file_meta(path_text: str) -> tuple[str | None, int | None]:
    p = Path(path_text)
    if not p.exists() or not p.is_file():
        return None, None

    hasher = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest(), p.stat().st_size


def parse_item(item_text: str) -> tuple[str, str | None, str]:
    # Format: file_path|backup_path|action
    parts = item_text.split("|")
    file_path = parts[0].strip()
    backup_path = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
    action = parts[2].strip() if len(parts) > 2 and parts[2].strip() else "update"
    if not file_path:
        raise ValueError(f"Invalid item: {item_text!r}")
    return file_path, backup_path, action


def main() -> None:
    parser = argparse.ArgumentParser(description="Write one backup event into SQLite DB.")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to SQLite db file")
    parser.add_argument("--summary", required=True, help="Short event summary")
    parser.add_argument("--source", default="manual", help="Who/what created this event")
    parser.add_argument(
        "--repo-changes",
        default="yes",
        choices=["yes", "no"],
        help="Whether this event changed files in repo/workspace",
    )
    parser.add_argument("--note", default="", help="Optional longer note")
    parser.add_argument(
        "--item",
        action="append",
        default=[],
        help="Record item format: file_path|backup_path|action",
    )
    args = parser.parse_args()

    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        ensure_schema(conn)
        now = datetime.now().isoformat(timespec="seconds")
        repo_changes = 1 if args.repo_changes == "yes" else 0

        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO backup_events (created_at, source, summary, repo_changes, note)
            VALUES (?, ?, ?, ?, ?)
            """,
            (now, args.source, args.summary, repo_changes, args.note),
        )
        event_id = cur.lastrowid

        for raw in args.item:
            file_path, backup_path, action = parse_item(raw)
            digest, size = file_meta(file_path)
            cur.execute(
                """
                INSERT INTO backup_files (
                    event_id, file_path, backup_path, action, file_hash, file_size
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (event_id, file_path, backup_path, action, digest, size),
            )

        conn.commit()
        print(f"OK: event_id={event_id}, db={db_path}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

