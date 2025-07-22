import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from agentspring.api import FastAPIAgent, MetricsTracker, AuthMiddleware, HealthEndpoint, standard_endpoints
from unittest.mock import MagicMock
import os
import json


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

client = TestClient(app)

# Test /health endpoint
def test_health_endpoint():
    response = client.get('/health')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    assert 'timestamp' in data

# Test /test-error endpoint (should log error and return 500)
def test_error_endpoint():
    response = client.get('/test-error')
    assert response.status_code == 500
    data = response.json()
    assert data['error'] == 'An unexpected error occurred.'
    assert data['code'] == 'INTERNAL_ERROR'
    assert 'timestamp' in data

# Test /task-status/{task_id} endpoint (unknown task)
def test_task_status_unknown():
    response = client.get('/task-status/unknown-task-id')
    assert response.status_code == 200
    data = response.json()
    assert data['task_id'] == 'unknown-task-id'
    assert data['status'] in ['PENDING', 'FAILURE', 'SUCCESS', 'RETRY', 'STARTED']

# Test log enrichment and scrubbing
def test_log_enrichment_and_scrubbing():
    log_file = os.getenv('LOG_FILE', 'logs/agentspring.log')
    # Trigger an error to ensure log is written
    client.get('/test-error')
    found_enrichment = False
    found_scrub = False
    with open(log_file) as f:
        for line in f:
            try:
                log = json.loads(line)
            except Exception:
                continue
            # Check enrichment fields
            if all(k in log for k in ['tenant_id', 'environment', 'hostname']):
                found_enrichment = True
            # Check scrubbing (simulate a log with sensitive data)
            if '***REDACTED***' in log.get('message', ''):
                found_scrub = True
    assert found_enrichment, 'Log enrichment fields missing'
    # For scrubbing, we can only check if the filter works if a sensitive message is logged
    # To force this, log a message with a password
    logger = app.logger if hasattr(app, 'logger') else None
    if logger:
        logger.error('User password=supersecret123')
        with open(log_file) as f:
            for line in f:
                if '***REDACTED***' in line:
                    found_scrub = True
    assert found_scrub, 'Sensitive data not scrubbed from logs' 