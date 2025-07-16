import pytest
from agentspring.multi_tenancy import TenantManager, TenantConfig
from unittest.mock import patch, MagicMock
from datetime import datetime

def test_tenant_config_model():
    t = TenantConfig(tenant_id="t1", name="Tenant", api_key="key", routing_rules={}, llm_model="m", max_requests_per_hour=10, features_enabled=[], created_at=datetime.now(), updated_at=datetime.now(), active=True)
    assert t.tenant_id == "t1"

def test_tenant_manager_crud(monkeypatch):
    mock_redis = MagicMock()
    monkeypatch.setattr("agentspring.multi_tenancy.redis_client", mock_redis)
    manager = TenantManager()
    t = TenantConfig(tenant_id="t2", name="T2", api_key="k2", routing_rules={}, llm_model="m", max_requests_per_hour=10, features_enabled=[], created_at=datetime.now(), updated_at=datetime.now(), active=True)
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