from fastapi.testclient import TestClient
from prometheus_client import Counter

import agentspring.metrics as metrics


def test_get_or_create_counter_creates_and_reuses():
    name = "test_counter_total"
    doc = "Test counter"
    # Should create new
    counter1 = metrics.get_or_create_counter(name, doc)
    assert isinstance(counter1, Counter)
    # Should reuse existing
    counter2 = metrics.get_or_create_counter(name, doc)
    assert counter1 is counter2


def test_register_custom_metric_and_call():
    calls = {}

    def custom_metric(request, response):
        calls["called"] = True

    metrics.custom_metrics.clear()
    metrics.register_custom_metric(custom_metric)
    assert custom_metric in metrics.custom_metrics

    # Simulate FastAPI request/response
    class DummyReq:
        method = "GET"
        url = type("U", (), {"path": "/foo"})()

    class DummyResp:
        pass

    for func in metrics.custom_metrics:
        func(DummyReq(), DummyResp())
    assert calls.get("called")


def test_setup_metrics_middleware_and_metrics_endpoint():
    from agentspring.api import FastAPIAgent

    agent = FastAPIAgent()
    client = TestClient(agent.get_app())

    # Simulate a request to trigger the middleware and increment the counter
    @agent.app.get("/foo")
    def foo():
        return {"ok": True}

    resp = client.get("/foo")
    assert resp.status_code == 200

    # /metrics endpoint should be present and return Prometheus text
    metrics_resp = client.get("/metrics")
    assert metrics_resp.status_code == 200
    assert "api_requests_total" in metrics_resp.text
