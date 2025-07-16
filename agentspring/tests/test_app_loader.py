from agentspring.app_loader import load_app
import importlib
from unittest.mock import patch

def test_load_app(monkeypatch):
    monkeypatch.setattr(importlib, "import_module", lambda name: "mock_module")
    assert load_app() == "mock_module" 