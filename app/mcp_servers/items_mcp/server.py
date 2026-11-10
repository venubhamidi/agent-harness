"""Items MCP server: read-only tools for agents. The server, not the model, talks to PostgreSQL.

Run over stdio:  python -m app.mcp_servers.items_mcp.server
Tools return a JSON document as text. `TOOLS` exposes the same functions for in-process tests.
"""
from __future__ import annotations

import json
from typing import Any

from mcp.server.mcpserver import MCPServer  # MCP SDK 2.x (FastMCP was renamed)

from app.config import settings
from harness.db import get_conn

server = MCPServer("items-mcp", version="0.1.0")


def _get_item(item_key: str) -> dict[str, Any] | None:
    with get_conn(settings.database_url) as conn:
        row = conn.execute("SELECT item_key, title, owner, priority, status, updated_at::text FROM items "
                           "WHERE item_key = %s", (item_key,)).fetchone()
    return dict(row) if row else None


@server.tool()
def get_item(item_key: str) -> str:
    """Return one item by its key, as JSON (null if there is no such item). Read-only."""
    return json.dumps(_get_item(item_key))


TOOLS = {"get_item": _get_item}

if __name__ == "__main__":
    server.run()
