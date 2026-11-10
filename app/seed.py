"""Load a few sample items:  python -m app.seed   (safe to run repeatedly)"""
from __future__ import annotations

from app.config import settings
from harness.db import get_conn

SAMPLE = [
    ("IT-1", "Renew the wildcard certificate", "kim", "high"),
    ("IT-2", "Decide the log retention period", None, "medium"),
    ("IT-3", "Archive last year's reports", "sam", "unknown"),
    ("IT-4", "Review access to the shared drive", None, "unknown"),
]


def seed(database_url: str) -> int:
    with get_conn(database_url) as conn:
        for key, title, owner, priority in SAMPLE:
            conn.execute("""INSERT INTO items (item_key, title, owner, priority) VALUES (%s,%s,%s,%s)
                            ON CONFLICT (item_key) DO NOTHING""", (key, title, owner, priority))
        conn.commit()
    return len(SAMPLE)


if __name__ == "__main__":
    print(f"seeded {seed(settings.database_url)} sample items")
