import pytest
from agentspring.api_versioning import VersionManager, APIVersion, version_manager, get_api_version, create_versioned_router, versioned_response, versioned_request
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

def test_get_version_info_error():
    vm = VersionManager()
    with pytest.raises(ValueError):
        vm.get_version_info("not_a_version")

def test_get_sunset_date_and_features():
    vm = VersionManager()
    # v1 should have no sunset date
    assert vm.get_sunset_date("v1") is None
    # v2 should have features
    assert isinstance(vm.get_supported_features("v2"), list)

def test_transform_request_v1():
    vm = VersionManager()
    req = {}
    out = vm.transform_request(APIVersion.V1, req)
    assert out["customer_id"] == "unknown"
    assert out["message"] == ""

def test_transform_request_v2():
    vm = VersionManager()
    req = {}
    out = vm.transform_request(APIVersion.V2, req)
    assert out["priority"] == "Medium"

def test_transform_request_v3():
    vm = VersionManager()
    req = {"foo": "bar"}
    out = vm.transform_request(APIVersion.V3, req)
    assert out == req