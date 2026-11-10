"""Business rules, defined once. The API, the MCP tools and the agent all use these, so the
dashboard and the agents can never disagree. Rules are code and SQL; a model never applies them."""
from __future__ import annotations

from typing import Any

NO_OWNER_SQL = "owner IS NULL"
NO_PRIORITY_SQL = "priority = 'unknown'"


def item_flags(item: dict[str, Any]) -> list[str]:
    flags = []
    if not item.get("owner"):
        flags.append("no_owner")
    if item.get("priority") == "unknown":
        flags.append("priority_unknown")
    return flags


def summary_counts(conn) -> dict[str, Any]:
    """Counts over the whole table, never over one page."""
    return dict(conn.execute(
        f"""SELECT count(*)::int AS total,
                   (count(*) FILTER (WHERE {NO_OWNER_SQL}))::int AS without_owner,
                   (count(*) FILTER (WHERE {NO_PRIORITY_SQL}))::int AS priority_unknown,
                   max(updated_at) AS data_as_of
            FROM items""").fetchone())
