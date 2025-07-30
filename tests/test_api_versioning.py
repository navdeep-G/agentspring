import pytest
from agentspring.api_versioning import VersionManager, version_manager, get_api_version, create_versioned_router, versioned_response, versioned_request
from fastapi import Request
from unittest.mock import MagicMock

def test_version_manager_info():
    vm = VersionManager()
    info = vm.get_version_info("v1")
    assert "features" in info
    assert not vm.is_deprecated("v1")
    assert vm.validate_version("v2")

def test_transform_request_response():
    vm = VersionManager()
    req = vm.transform_request("v1", {})
    resp = vm.transform_response("v1", {"summary": "s"})
    assert "summary" in resp

def test_get_api_version(monkeypatch):
    req = MagicMock()
    req.headers = {"Accept": "application/vnd.api.v2+json"}
    req.url.path = "/api/v2/endpoint"
    assert get_api_version(req) == "v2"

def test_versioned_response_and_request():
    data = {"summary": "s"}
    result = versioned_response("v1", data)
    assert "summary" in result["data"]
    assert isinstance(versioned_request("v1", {}), dict) 