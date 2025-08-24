import importlib

from agentspring.app_loader import load_app


def test_load_app(monkeypatch):
    monkeypatch.setattr(importlib, "import_module", lambda name: "mock_module")
    assert load_app() == "mock_module"
