import os
from fastapi.testclient import TestClient
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/agentspring")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
from agentspring.api import app  # noqa
def test_health():
    c = TestClient(app)
    r = c.get("/health")
    assert r.status_code == 200 and r.json()["ok"] is True
