from datetime import datetime
from unittest.mock import MagicMock

import pytest

from agentspring.multi_tenancy import TenantConfig, TenantManager


def test_tenant_config_model():
    t = TenantConfig(
        tenant_id="t1",
        name="Tenant",
        api_key="key",
        routing_rules={},
        llm_model="m",
        max_requests_per_hour=10,
        features_enabled=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        active=True,
    )
    assert t.tenant_id == "t1"


def test_tenant_manager_crud(monkeypatch):
    mock_redis = MagicMock()
    monkeypatch.setattr("agentspring.multi_tenancy.redis_client", mock_redis)
    manager = TenantManager()
    t = TenantConfig(
        tenant_id="t2",
        name="T2",
        api_key="k2",
        routing_rules={},
        llm_model="m",
        max_requests_per_hour=10,
        features_enabled=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        active=True,
    )
    # Create
    monkeypatch.setattr(manager, "get_tenant_by_id", lambda tid: None)
    monkeypatch.setattr(manager, "get_tenant_by_api_key", lambda k: None)
    manager.create_tenant(t)
    # Update
    monkeypatch.setattr(manager, "get_tenant_by_id", lambda tid: t)
    manager.update_tenant("t2", {"name": "T2-updated"})
    # Delete
    monkeypatch.setattr(manager, "get_tenant_by_id", lambda tid: t)
    manager.delete_tenant("t2")
    # List
    mock_redis.keys.return_value = [b"tenant:t2"]
    mock_redis.get.return_value = t.model_dump_json().encode()
    tenants = manager.list_tenants()
    assert isinstance(tenants, list)


def test_get_tenant_by_api_key_and_id(monkeypatch):
    mock_redis = MagicMock()
    monkeypatch.setattr("agentspring.multi_tenancy.redis_client", mock_redis)
    manager = TenantManager()
    # Not found
    monkeypatch.setattr(manager, "tenant_cache", {})
    mock_redis.get.return_value = None
    assert manager.get_tenant_by_api_key("nope") is None
    assert manager.get_tenant_by_id("nope") is None
    # Found in Redis
    t = TenantConfig(
        tenant_id="t3",
        name="T3",
        api_key="k3",
        routing_rules={},
        llm_model="m",
        max_requests_per_hour=10,
        features_enabled=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        active=True,
    )
    mock_redis.get.return_value = t.model_dump_json().encode()
    manager.tenant_cache = {}
    assert manager.get_tenant_by_api_key("k3").tenant_id == "t3"
    manager.tenant_cache = {}
    assert manager.get_tenant_by_id("t3").api_key == "k3"


def test_create_tenant_errors(monkeypatch):
    mock_redis = MagicMock()
    monkeypatch.setattr("agentspring.multi_tenancy.redis_client", mock_redis)
    manager = TenantManager()
    t = TenantConfig(
        tenant_id="t4",
        name="T4",
        api_key="k4",
        routing_rules={},
        llm_model="m",
        max_requests_per_hour=10,
        features_enabled=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        active=True,
    )
    monkeypatch.setattr(manager, "get_tenant_by_id", lambda tid: t)
    with pytest.raises(ValueError):
        manager.create_tenant(t)
    monkeypatch.setattr(manager, "get_tenant_by_id", lambda tid: None)
    monkeypatch.setattr(manager, "get_tenant_by_api_key", lambda k: t)
    with pytest.raises(ValueError):
        manager.create_tenant(t)


def test_update_tenant_errors(monkeypatch):
    mock_redis = MagicMock()
    monkeypatch.setattr("agentspring.multi_tenancy.redis_client", mock_redis)
    manager = TenantManager()
    monkeypatch.setattr(manager, "get_tenant_by_id", lambda tid: None)
    with pytest.raises(ValueError):
        manager.update_tenant("bad", {"name": "fail"})


def test_delete_tenant_not_found(monkeypatch):
    mock_redis = MagicMock()
    monkeypatch.setattr("agentspring.multi_tenancy.redis_client", mock_redis)
    manager = TenantManager()
    monkeypatch.setattr(manager, "get_tenant_by_id", lambda tid: None)
    assert not manager.delete_tenant("missing")


def test_list_tenants_error(monkeypatch):
    mock_redis = MagicMock()
    monkeypatch.setattr("agentspring.multi_tenancy.redis_client", mock_redis)
    manager = TenantManager()
    mock_redis.keys.side_effect = Exception()
    assert manager.list_tenants() == []


def test_check_rate_limit(monkeypatch):
    mock_redis = MagicMock()
    monkeypatch.setattr("agentspring.multi_tenancy.redis_client", mock_redis)
    manager = TenantManager()
    t = TenantConfig(
        tenant_id="t5",
        name="T5",
        api_key="k5",
        routing_rules={},
        llm_model="m",
        max_requests_per_hour=1,
        features_enabled=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        active=True,
    )
    monkeypatch.setattr(manager, "get_tenant_by_id", lambda tid: t)
    mock_redis.get.return_value = None
    assert manager.check_rate_limit("t5")
    mock_redis.get.return_value = b"1"
    assert not manager.check_rate_limit("t5")
    monkeypatch.setattr(manager, "get_tenant_by_id", lambda tid: None)
    assert not manager.check_rate_limit("bad")
    mock_redis.get.side_effect = Exception()
    assert manager.check_rate_limit("t5")


def test_get_tenant_routing_rules(monkeypatch):
    mock_redis = MagicMock()
    monkeypatch.setattr("agentspring.multi_tenancy.redis_client", mock_redis)
    manager = TenantManager()
    t = TenantConfig(
        tenant_id="t6",
        name="T6",
        api_key="k6",
        routing_rules={"foo": "bar"},
        llm_model="m",
        max_requests_per_hour=1,
        features_enabled=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        active=True,
    )
    monkeypatch.setattr(manager, "get_tenant_by_id", lambda tid: t)
    assert manager.get_tenant_routing_rules("t6") == {"foo": "bar"}
    t.routing_rules = {}
    assert manager.get_tenant_routing_rules("t6") == {}
    monkeypatch.setattr(
        manager,
        "get_tenant_by_id",
        lambda tid: (_ for _ in ()).throw(Exception()),
    )
    assert manager.get_tenant_routing_rules("bad") == {}
