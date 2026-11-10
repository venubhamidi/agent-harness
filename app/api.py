"""Example API. Every endpoint: permission check, database from the request, pagination for lists."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.agents.review_agent import review_item
from app.rules import item_flags, summary_counts
from harness.agents.contract import AgentResponse
from harness.app import db_url, ticketing
from harness.db import get_conn
from harness.pagination import Page
from harness.plugins.ticketing import Ticket, TicketingProvider, TicketRequest
from harness.security import Principal, require

router = APIRouter(prefix="/api/v1")


class Item(BaseModel):
    id: int
    item_key: str
    title: str
    owner: str | None
    priority: str
    status: str
    updated_at: datetime
    flags: list[str] = []


class ItemSummary(BaseModel):
    total: int
    without_owner: int
    priority_unknown: int
    data_as_of: datetime | None


def _item(row: dict) -> Item:
    return Item(**row, flags=item_flags(row))


@router.get("/items", response_model=Page[Item])
def list_items(_: Principal = Depends(require("items:read")), db: str = Depends(db_url),
               limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0),
               priority: str | None = None) -> Page[Item]:
    where, params = ("WHERE priority = %(priority)s", {"priority": priority}) if priority else ("", {})
    with get_conn(db) as conn:
        total = conn.execute(f"SELECT count(*) AS n FROM items {where}", params).fetchone()["n"]
        rows = conn.execute(f"SELECT * FROM items {where} ORDER BY id LIMIT %(limit)s OFFSET %(offset)s",
                            {**params, "limit": limit, "offset": offset}).fetchall()
    return Page(items=[_item(r) for r in rows], total=total, limit=limit, offset=offset)


@router.get("/items/summary", response_model=ItemSummary)
def items_summary(_: Principal = Depends(require("items:read")), db: str = Depends(db_url)) -> ItemSummary:
    """Counts for the dashboard, computed by the backend over all items."""
    with get_conn(db) as conn:
        return ItemSummary(**summary_counts(conn))


@router.get("/items/{item_key}", response_model=Item)
def get_item(item_key: str, _: Principal = Depends(require("items:read")), db: str = Depends(db_url)) -> Item:
    with get_conn(db) as conn:
        row = conn.execute("SELECT * FROM items WHERE item_key = %s", (item_key,)).fetchone()
    if row is None:
        raise HTTPException(404, "Item not found")
    return _item(row)


@router.post("/items/{item_key}/review", response_model=AgentResponse)
def review(item_key: str, p: Principal = Depends(require("agents:run"))) -> AgentResponse:
    """Run the review agent on one item. Advisory: nothing is changed."""
    return review_item(item_key, requested_by=p.subject)


@router.post("/items/{item_key}/ticket", response_model=Ticket)
def open_ticket(item_key: str, p: Principal = Depends(require("tickets:create")), db: str = Depends(db_url),
                provider: TicketingProvider = Depends(ticketing)) -> Ticket:
    """A person opens a ticket for an item in the configured ticket system (plugin). Agents cannot."""
    item = get_item(item_key, p, db)
    return provider.create(TicketRequest(title=item.title, description=f"Item {item.item_key}; gaps: {item.flags or 'none'}",
                                         severity={"high": "high", "low": "low"}.get(item.priority, "medium"),
                                         requested_by=p.subject, external_ref=item.item_key))
