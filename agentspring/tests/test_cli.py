import os
import sys
from unittest.mock import patch, mock_open
from agentspring import cli

def test_create_app(monkeypatch, tmp_path):
    app_name = "TestApp"
    app_dir = tmp_path / app_name.lower()
    monkeypatch.setattr("os.path.exists", lambda p: False)
    monkeypatch.setattr("os.makedirs", lambda p: None)
    m = mock_open()
    with patch("builtins.open", m):
        cli.create_app(app_name)
    # Check that open was called for endpoints.py and README.md
    assert m.call_count == 2 