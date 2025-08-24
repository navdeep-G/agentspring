from unittest.mock import patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from agentspring.api import AuthMiddleware, FastAPIAgent


@pytest.fixture
def healthy_app():
    """Creates a FastAPIAgent instance with a mocked (healthy) AsyncTaskManager."""
    with patch("agentspring.api.AsyncTaskManager") as MockAsyncTaskManager:
        mock_task_manager = MockAsyncTaskManager.return_value
        # Mock the backend client's ping method to simulate a healthy connection
        mock_task_manager.celery_app.backend.client.ping.return_value = True
        agent = FastAPIAgent(title="Healthy Test Agent")
        yield agent.get_app()


@pytest.fixture
def unhealthy_app():
    """Creates a FastAPIAgent instance with a mocked (unhealthy) AsyncTaskManager."""
    with patch("agentspring.api.AsyncTaskManager") as MockAsyncTaskManager:
        mock_task_manager = MockAsyncTaskManager.return_value
        # Mock the backend client's ping method to simulate a failure
        mock_task_manager.celery_app.backend.client.ping.side_effect = (
            Exception("Redis down")
        )
        agent = FastAPIAgent(title="Unhealthy Test Agent")
        yield agent.get_app()


@pytest.fixture
def no_async_app():
    """Creates a FastAPIAgent instance where AsyncTaskManager fails to initialize."""
    with patch(
        "agentspring.api.AsyncTaskManager",
        side_effect=Exception("Redis not available"),
    ):
        agent = FastAPIAgent(title="No Async Test Agent")
        yield agent.get_app()


def test_fastapiagent_creation():
    agent = FastAPIAgent(title="Test Agent")
    assert isinstance(agent.get_app(), FastAPI)


def test_auth_middleware_valid():
    auth = AuthMiddleware(api_key_env="NOT_SET", default_key="test-key")
    assert auth("test-key") == "test-key"


def test_auth_middleware_invalid():
    auth = AuthMiddleware(api_key_env="NOT_SET", default_key="test-key")
    with pytest.raises(HTTPException):
        auth("wrong-key")


def test_health_endpoint_healthy(healthy_app):
    client = TestClient(healthy_app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "redis": "connected"}


def test_health_endpoint_unhealthy(unhealthy_app):
    client = TestClient(unhealthy_app)
    response = client.get("/health")
    # The health endpoint itself should still return 200, but with a disconnected status
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "redis": "disconnected"}


def test_health_endpoint_no_async(no_async_app):
    client = TestClient(no_async_app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "redis": "disconnected"}


def test_standard_endpoints_registration(healthy_app):
    app = healthy_app
    paths = {route.path for route in app.routes}
    assert "/tasks/{task_id}/status" in paths
    assert "/tasks/{task_id}/result" in paths


def test_standard_endpoints_not_registered(no_async_app):
    app = no_async_app
    paths = {route.path for route in app.routes}
    assert "/tasks/{task_id}/status" not in paths
    assert "/tasks/{task_id}/result" not in paths
