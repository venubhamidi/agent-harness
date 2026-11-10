"""Evaluation suites for this application's agents:  python -m harness.evals app

Suites use fixed fixture records, not the database, so results are repeatable."""
from __future__ import annotations

import json
from pathlib import Path

from app.agents.review_agent import ItemReviewAgent
from app.config import settings
from harness.agents.contract import build_agent
from harness.evals import EvalSuite
from harness.testing import DictToolClient

HERE = Path(__file__).resolve().parent
FIXTURES: dict[str, dict] = json.loads((HERE / "fixtures.json").read_text())

EVAL_SUITES = {
    "item-review": EvalSuite(
        agent_factory=lambda: build_agent(ItemReviewAgent, settings,
                                          DictToolClient({"get_item": lambda item_key: FIXTURES.get(item_key)})),
        cases_dir=HERE / "item_review"),
}
