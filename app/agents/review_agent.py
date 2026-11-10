"""Item Review Agent: the example agent.

Python decides the facts (which gaps an item has). The model only writes a short summary and a
suggested next step, as a validated structure. Nothing the model says changes stored data.

    python -m app.agents.review_agent IT-2
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from pydantic import BaseModel

from app.config import settings
from app.rules import item_flags
from harness.agents.contract import Agent, AgentRequest, AgentResponse, AgentRunner, AgentSpec, ToolClient, build_agent
from harness.agents.mcp_client import McpStdioToolClient
from harness.db import conn_factory

REPO_ROOT = str(Path(__file__).resolve().parents[2])

SYSTEM = ("You help a team lead review work items. Write for a busy reader. State only facts that "
          "are in the data. If something is missing, say it is missing.")


class Review(BaseModel):
    summary: str                 # one or two sentences
    suggested_next_step: str     # one concrete action for a person to consider


class ItemReviewAgent(Agent):
    spec = AgentSpec(agent_id="item-review-agent", name="Item Review Agent", version="0.1.0",
                     description="Summarizes one item and flags missing ownership or priority.",
                     allowed_tools=["get_item"])

    def run(self, request: AgentRequest) -> AgentResponse:
        item = self.call_tool("get_item", item_key=request.input["item_key"])
        if item is None:
            return self.fail(request, "item_not_found", f"No item {request.input['item_key']}")
        flags = item_flags(item)                                  # computed, never inferred by the model
        review = self.llm(SYSTEM, f"Review this item. Known gaps: {flags or 'none'}.",
                          data=json.dumps(item), schema=Review)
        return self.ok(request,
                       {"item": item, "flags": flags, "summary": review.summary,
                        "suggested_next_step": review.suggested_next_step},
                       "Flags come from rules in code; the summary and next step are model-written from those facts.")


def mcp_tools() -> ToolClient:
    return McpStdioToolClient(sys.executable, ["-m", "app.mcp_servers.items_mcp.server"], cwd=REPO_ROOT)


def review_item(item_key: str, requested_by: str, tools: ToolClient | None = None) -> AgentResponse:
    agent = build_agent(ItemReviewAgent, settings, tools or mcp_tools())
    return AgentRunner(conn_factory(settings.database_url)).execute(
        agent, AgentRequest(requested_by=requested_by, input={"item_key": item_key}))


if __name__ == "__main__":
    response = review_item(sys.argv[1] if len(sys.argv) > 1 else "IT-2", requested_by="cli:dev")
    print(json.dumps(response.model_dump(mode="json"), indent=2))
