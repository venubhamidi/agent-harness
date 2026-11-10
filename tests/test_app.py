"""The example application. Copy the shape of these tests for your own endpoints and agents."""
from app.agents.review_agent import review_item
from app.config import settings
from app.evals import EVAL_SUITES
from app.main import app
from app.mcp_servers.items_mcp.server import TOOLS
from harness.audit import verify_audit_chain
from harness.db import conn_factory, get_conn
from harness.evals import run_suite
from harness.testing import DictToolClient
from tests.conftest import EDITOR, GUEST, VIEWER


def test_list_requires_login_and_permission_and_paginates(client):
    assert client.get("/api/v1/items").status_code == 401
    assert client.get("/api/v1/items", headers=GUEST).status_code == 403
    body = client.get("/api/v1/items?limit=2&offset=1", headers=VIEWER).json()
    assert (body["total"], body["limit"], body["offset"]) == (4, 2, 1)
    assert [i["item_key"] for i in body["items"]] == ["IT-2", "IT-3"]
    assert client.get("/api/v1/items?limit=0", headers=VIEWER).status_code == 422
    assert client.get("/api/v1/items/NOPE", headers=VIEWER).status_code == 404


def test_summary_counts_all_items_not_one_page(client):
    body = client.get("/api/v1/items/summary", headers=VIEWER).json()
    assert (body["total"], body["without_owner"], body["priority_unknown"]) == (4, 2, 2)
    assert client.get("/api/v1/items/summary", headers=GUEST).status_code == 403


def test_flags_are_the_same_in_api_and_agent(client):
    api_flags = client.get("/api/v1/items/IT-4", headers=VIEWER).json()["flags"]
    agent = review_item("IT-4", requested_by="test", tools=DictToolClient(TOOLS))
    assert api_flags == agent.output["flags"] == ["no_owner", "priority_unknown"]


def test_review_endpoint_runs_the_agent_over_mcp_and_changes_nothing(client):
    with get_conn(settings.database_url) as conn:
        before = conn.execute("SELECT * FROM items ORDER BY id").fetchall()
    assert client.post("/api/v1/items/IT-2/review", headers=VIEWER).status_code == 403      # viewers cannot run agents
    r = client.post("/api/v1/items/IT-2/review", headers=EDITOR)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "succeeded" and body["confidence"] == "advisory" and body["output"]["flags"] == ["no_owner"]
    assert (body["tool_calls"], body["llm_calls"]) == (1, 1) and body["usage"][0]["provider"] == "mock"
    with get_conn(settings.database_url) as conn:
        assert conn.execute("SELECT * FROM items ORDER BY id").fetchall() == before
        tool_audit = conn.execute("SELECT principal, action FROM audit_log WHERE role='agent'").fetchall()
        assert [(a["principal"], a["action"]) for a in tool_audit] == [("item-review-agent", "TOOL get_item")]
        assert conn.execute("SELECT count(*) AS n FROM model_usage").fetchone()["n"] == 1
        assert verify_audit_chain(conn) == (True, None)


def test_ticket_is_opened_by_a_person_through_the_ticketing_plugin(client):
    assert client.post("/api/v1/items/IT-1/ticket", headers=VIEWER).status_code == 403
    r = client.post("/api/v1/items/IT-1/ticket", headers=EDITOR)
    assert r.status_code == 200 and r.json()["number"] == "TKT0000001"
    sent = app.state.ticketing.requests[-1]
    assert (sent.external_ref, sent.severity, sent.requested_by) == ("IT-1", "high", "editor@example.com")


def test_agent_evals_pass():
    for name, suite in EVAL_SUITES.items():
        run = run_suite(suite, conn_factory(settings.database_url))
        assert run.score == 1.0, (name, run.failures)
