import pytest
from fastapi.testclient import TestClient

from app.config import MIGRATIONS_DIR, settings
from app.main import app
from app.seed import seed
from harness.db import apply_migrations, get_conn

EDITOR = {"Authorization": "Bearer dev-editor-token"}
VIEWER = {"Authorization": "Bearer dev-viewer-token"}
GUEST = {"Authorization": "Bearer dev-guest-token"}


@pytest.fixture(scope="session", autouse=True)
def schema():
    apply_migrations(MIGRATIONS_DIR, database_url=settings.database_url)


@pytest.fixture(autouse=True)
def fresh_data(schema):
    with get_conn(settings.database_url) as conn:
        conn.execute("TRUNCATE items, audit_log, model_usage, agent_executions, agent_definitions, "
                     "eval_results, eval_runs RESTART IDENTITY CASCADE")
        conn.commit()
    seed(settings.database_url)
    yield


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
