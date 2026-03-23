#!/usr/bin/env python3
"""
Read backup/change records from local SQLite database.

Examples:
  python backup_db_read.py --limit 20
  python backup_db_read.py --event-id 3
  python backup_db_read.py --event-id 3 --as-json
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = SKILL_ROOT / "backup_log.db"


def fetch_recent(conn: sqlite3.Connection, limit: int) -> list[dict]:
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT
            e.id,
            e.created_at,
            e.source,
            e.summary,
            e.repo_changes,
            e.note,
            COUNT(f.id) AS file_count
        FROM backup_events e
        LEFT JOIN backup_files f ON f.event_id = e.id
        GROUP BY e.id
        ORDER BY e.id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [
        {
            "id": r[0],
            "created_at": r[1],
            "source": r[2],
            "summary": r[3],
            "repo_changes": bool(r[4]),
            "note": r[5],
            "file_count": r[6],
        }
        for r in rows
    ]


def fetch_event(conn: sqlite3.Connection, event_id: int) -> dict | None:
    cur = conn.cursor()
    ev = cur.execute(
        """
        SELECT id, created_at, source, summary, repo_changes, note
        FROM backup_events
        WHERE id = ?
        """,
        (event_id,),
    ).fetchone()
    if not ev:
        return None

    files = cur.execute(
        """
        SELECT file_path, backup_path, action, file_hash, file_size
        FROM backup_files
        WHERE event_id = ?
        ORDER BY id
        """,
        (event_id,),
    ).fetchall()

    return {
        "id": ev[0],
        "created_at": ev[1],
        "source": ev[2],
        "summary": ev[3],
        "repo_changes": bool(ev[4]),
        "note": ev[5],
        "files": [
            {
                "file_path": f[0],
                "backup_path": f[1],
                "action": f[2],
                "file_hash": f[3],
                "file_size": f[4],
            }
            for f in files
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Read backup log SQLite DB.")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to SQLite db file")
    parser.add_argument("--limit", type=int, default=20, help="Rows for recent view")
    parser.add_argument("--event-id", type=int, default=0, help="Show one event in detail")
    parser.add_argument("--as-json", action="store_true", help="Print as JSON")
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"DB not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    try:
        if args.event_id > 0:
            event = fetch_event(conn, args.event_id)
            if not event:
                print(f"Event not found: {args.event_id}")
                return
            if args.as_json:
                print(json.dumps(event, ensure_ascii=False, indent=2))
                return

            print(f"Event #{event['id']} @ {event['created_at']}")
            print(f"source={event['source']} repo_changes={event['repo_changes']}")
            print(f"summary={event['summary']}")
            if event["note"]:
                print(f"note={event['note']}")
            print("files:")
            for f in event["files"]:
                print(
                    f"  - {f['action']}: {f['file_path']} | backup={f['backup_path']} | size={f['file_size']}"
                )
            return

        rows = fetch_recent(conn, args.limit)
        if args.as_json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
            return
        for r in rows:
            print(
                f"[{r['id']}] {r['created_at']} | {r['source']} | files={r['file_count']} | {r['summary']}"
            )
    finally:
        conn.close()


if __name__ == "__main__":
    main()

