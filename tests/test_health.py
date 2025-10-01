"""Test the health check endpoint."""
import os
from fastapi.testclient import TestClient

# Set up test environment variables
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

# Import the FastAPI app
from agentspring.api import app

def test_health():
    """Test the health check endpoint."""
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
