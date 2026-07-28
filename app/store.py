"""Persistent record of already-seen articles, so tomorrow's digest never
repeats what you've already read.

A tiny SQLite database keyed by a stable article id (the feed's guid/id, or
the link as a fallback). `filter_new` returns only the entries you haven't
seen; `mark_seen` records them once they've made it into a digest.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "seen.db"


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS seen (
            id         TEXT PRIMARY KEY,
            source     TEXT,
            title      TEXT,
            link       TEXT,
            first_seen TEXT
        )
        """
    )
    return conn


def filter_new(articles):
    """Return the subset of `articles` whose id is not already in the store."""
    if not articles:
        return []
    conn = _connect()
    try:
        seen_ids = {row[0] for row in conn.execute("SELECT id FROM seen")}
    finally:
        conn.close()
    return [a for a in articles if a["id"] not in seen_ids]


def mark_seen(articles):
    """Record `articles` as seen so future runs skip them."""
    if not articles:
        return
    now = datetime.now(timezone.utc).isoformat()
    conn = _connect()
    try:
        conn.executemany(
            "INSERT OR IGNORE INTO seen (id, source, title, link, first_seen) "
            "VALUES (?, ?, ?, ?, ?)",
            [(a["id"], a["source"], a["title"], a["link"], now) for a in articles],
        )
        conn.commit()
    finally:
        conn.close()


def stats():
    """Return (total_seen, distinct_sources) for a quick status line."""
    conn = _connect()
    try:
        total = conn.execute("SELECT COUNT(*) FROM seen").fetchone()[0]
        sources = conn.execute(
            "SELECT COUNT(DISTINCT source) FROM seen"
        ).fetchone()[0]
    finally:
        conn.close()
    return total, sources
