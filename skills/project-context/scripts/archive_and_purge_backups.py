#!/usr/bin/env python3
"""
Archive all files under any `backup` directory into backup_log.db, then purge originals.

This script stores full file bytes in SQLite (BLOB) so deleting backup files still keeps recoverable data.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sqlite3
from datetime import datetime
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
SKILL_ROOT = SCRIPT_PATH.parents[1]
WORKSPACE_ROOT = SCRIPT_PATH.parents[4]
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

        CREATE TABLE IF NOT EXISTS backup_file_archives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            archived_at TEXT NOT NULL,
            backup_file_path TEXT NOT NULL,
            original_file_guess TEXT,
            action TEXT NOT NULL DEFAULT 'archive_backup',
            file_hash TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            content_blob BLOB NOT NULL,
            FOREIGN KEY(event_id) REFERENCES backup_events(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_bfa_event_id
            ON backup_file_archives(event_id);
        CREATE INDEX IF NOT EXISTS idx_bfa_backup_file_path
            ON backup_file_archives(backup_file_path);
        """
    )


def infer_original_path(backup_path: Path, workspace_root: Path) -> str:
    rel = backup_path.relative_to(workspace_root).as_posix()
    rel = rel.replace("/backup/", "/")
    rel = rel.replace("\\backup\\", "\\")
    name = Path(rel).name

    # Strip common backup suffixes
    for pattern in [r"\.bak_\d{8}(?:_\d{6})?$", r"\.backup_\d{8}_\d{6}$", r"\.backup$"]:
        name2 = re.sub(pattern, "", name)
        if name2 != name:
            name = name2
            break

    p = str(Path(rel).with_name(name)).replace("\\", "/")
    return p


def find_backup_files(workspace_root: Path) -> list[Path]:
    out: list[Path] = []
    for p in workspace_root.rglob("*"):
        if not p.is_file():
            continue
        if "backup" in [x.lower() for x in p.parts]:
            out.append(p)
    return out


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Archive all backup files into SQLite and delete originals.")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to backup_log.db")
    parser.add_argument("--source", default="codex", help="Event source")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, no DB write, no delete")
    args = parser.parse_args()

    db_path = Path(args.db).resolve()
    files = find_backup_files(WORKSPACE_ROOT)
    if not files:
        print("No backup files found.")
        return

    print(f"Found backup files: {len(files)}")
    if args.dry_run:
        for f in files[:20]:
            print(f"  {f.relative_to(WORKSPACE_ROOT).as_posix()}")
        if len(files) > 20:
            print("  ...")
        return

    conn = sqlite3.connect(db_path)
    try:
        ensure_schema(conn)
        now = datetime.now().isoformat(timespec="seconds")
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO backup_events (created_at, source, summary, repo_changes, note)
            VALUES (?, ?, ?, 1, ?)
            """,
            (
                now,
                args.source,
                f"Archive and purge backup files ({len(files)} files)",
                "Automatic archive of backup folders into SQLite BLOB storage",
            ),
        )
        event_id = cur.lastrowid

        ok = 0
        failed = 0
        for i, f in enumerate(files, 1):
            rel = f.relative_to(WORKSPACE_ROOT).as_posix()
            try:
                blob = f.read_bytes()
                cur.execute(
                    """
                    INSERT INTO backup_file_archives (
                        event_id, archived_at, backup_file_path, original_file_guess,
                        action, file_hash, file_size, content_blob
                    ) VALUES (?, ?, ?, ?, 'archive_backup', ?, ?, ?)
                    """,
                    (
                        event_id,
                        now,
                        rel,
                        infer_original_path(f, WORKSPACE_ROOT),
                        sha256_bytes(blob),
                        len(blob),
                        blob,
                    ),
                )
                f.unlink()
                ok += 1
            except Exception as e:
                failed += 1
                print(f"FAILED: {rel} | {e}")

            if i % 50 == 0:
                conn.commit()
                print(f"Progress: {i}/{len(files)}")

        conn.commit()
        print(f"DONE: event_id={event_id}, archived={ok}, failed={failed}, db={db_path}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

