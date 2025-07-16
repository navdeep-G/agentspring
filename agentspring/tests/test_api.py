import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from agentspring.api import FastAPIAgent, MetricsTracker, AuthMiddleware, HealthEndpoint, standard_endpoints
from unittest.mock import MagicMock


def test_fastapiagent_creation():
    agent = FastAPIAgent(title="Test Agent")
    assert isinstance(agent.get_app(), FastAPI)

def test_metrics_tracker(monkeypatch):
    mock_redis = MagicMock()
    monkeypatch.setattr("redis.Redis.from_url", lambda url: mock_redis)
    tracker = MetricsTracker(redis_url="redis://test")
    tracker.track_request(True, 0.1, "test")
    assert mock_redis.incr.called
    assert tracker.get_average_response_time() == 0.0 or isinstance(tracker.get_average_response_time(), float)

def test_auth_middleware_valid():
    auth = AuthMiddleware(api_key_env="NOT_SET", default_key="test-key")
    assert auth("test-key") == "test-key"

def test_auth_middleware_invalid():
    auth = AuthMiddleware(api_key_env="NOT_SET", default_key="test-key")
    with pytest.raises(HTTPException):
        auth("wrong-key")

def test_health_endpoint(monkeypatch):
    app = FastAPI()
    tracker = MagicMock()
    tracker.redis_client.ping.return_value = True
    tracker.track_request.return_value = None
    HealthEndpoint(app, tracker)
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_standard_endpoints_registration():
    app = FastAPI()
    class DummyTaskManager:
        def get_task_status(self, task_id):
            return {"task_id": task_id, "status": "SUCCESS"}
    standard_endpoints(app, DummyTaskManager())
    paths = [route.path for route in app.routes]
    assert any("/task/" in p for p in paths) 