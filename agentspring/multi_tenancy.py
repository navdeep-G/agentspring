"""
Multi-tenancy support for SupportFlow Agent
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import redis  # type: ignore
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Initialize Redis connection
redis_client = redis.Redis.from_url(
    os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
)


class TenantConfig(BaseModel):
    """Tenant configuration model"""

    tenant_id: str = Field(..., description="Unique tenant identifier")
    name: str = Field(..., description="Tenant display name")
    api_key: str = Field(..., description="Tenant-specific API key")
    routing_rules: Dict[str, Any] = Field(
        default_factory=dict, description="Tenant-specific routing rules"
    )
    llm_model: str = Field(
        default="mistral", description="Preferred LLM model"
    )
    max_requests_per_hour: int = Field(
        default=1000, description="Rate limit per hour"
    )
    features_enabled: List[str] = Field(
        default_factory=list, description="Enabled features"
    )
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    active: bool = Field(default=True, description="Whether tenant is active")


class TenantManager:
    """Manages multi-tenant configurations"""

    def __init__(self):
        self.tenant_cache = {}
        self.load_tenants()

    def load_tenants(self):
        """Load all tenants from Redis"""
        try:
            tenant_keys = redis_client.keys("tenant:*")
            for key in tenant_keys:
                tenant_data = redis_client.get(key)
                if tenant_data:
                    tenant_config = TenantConfig(**json.loads(tenant_data))
                    self.tenant_cache[tenant_config.tenant_id] = tenant_config
                    self.tenant_cache[tenant_config.api_key] = tenant_config
        except Exception as e:
            logger.error(f"Error loading tenants: {e}")

    def get_tenant_by_api_key(self, api_key: str) -> Optional[TenantConfig]:
        """Get tenant configuration by API key"""
        if api_key in self.tenant_cache:
            return self.tenant_cache[api_key]

        try:
            tenant_data = redis_client.get(f"tenant_api_key:{api_key}")
            if tenant_data:
                tenant_config = TenantConfig(**json.loads(tenant_data))
                self.tenant_cache[tenant_config.tenant_id] = tenant_config
                self.tenant_cache[tenant_config.api_key] = tenant_config
                return tenant_config
        except Exception as e:
            logger.error(f"Error getting tenant by API key: {e}")

        return None

    def get_tenant_by_id(self, tenant_id: str) -> Optional[TenantConfig]:
        """Get tenant configuration by tenant ID"""
        if tenant_id in self.tenant_cache:
            return self.tenant_cache[tenant_id]

        try:
            tenant_data = redis_client.get(f"tenant:{tenant_id}")
            if tenant_data:
                tenant_config = TenantConfig(**json.loads(tenant_data))
                self.tenant_cache[tenant_config.tenant_id] = tenant_config
                self.tenant_cache[tenant_config.api_key] = tenant_config
                return tenant_config
        except Exception as e:
            logger.error(f"Error getting tenant by ID: {e}")

        return None

    def create_tenant(self, tenant_config: TenantConfig) -> TenantConfig:
        """Create a new tenant"""
        try:
            # Check if tenant already exists
            if self.get_tenant_by_id(tenant_config.tenant_id):
                raise ValueError(
                    f"Tenant {tenant_config.tenant_id} already exists"
                )

            if self.get_tenant_by_api_key(tenant_config.api_key):
                raise ValueError(
                    f"API key {tenant_config.api_key} already exists"
                )

            # Save to Redis
            redis_client.set(
                f"tenant:{tenant_config.tenant_id}",
                tenant_config.model_dump_json(),
            )
            redis_client.set(
                f"tenant_api_key:{tenant_config.api_key}",
                tenant_config.model_dump_json(),
            )

            # Update cache
            self.tenant_cache[tenant_config.tenant_id] = tenant_config
            self.tenant_cache[tenant_config.api_key] = tenant_config

            logger.info(f"Created tenant: {tenant_config.tenant_id}")
            return tenant_config

        except Exception as e:
            logger.error(f"Error creating tenant: {e}")
            raise

    def update_tenant(
        self, tenant_id: str, updates: Dict[str, Any]
    ) -> TenantConfig:
        """Update tenant configuration"""
        try:
            tenant = self.get_tenant_by_id(tenant_id)
            if not tenant:
                raise ValueError(f"Tenant {tenant_id} not found")

            # Update fields
            for key, value in updates.items():
                if hasattr(tenant, key):
                    setattr(tenant, key, value)

            tenant.updated_at = datetime.now()

            # Save to Redis
            redis_client.set(
                f"tenant:{tenant.tenant_id}", tenant.model_dump_json()
            )
            redis_client.set(
                f"tenant_api_key:{tenant.api_key}", tenant.model_dump_json()
            )

            # Update cache
            self.tenant_cache[tenant.tenant_id] = tenant
            self.tenant_cache[tenant.api_key] = tenant

            logger.info(f"Updated tenant: {tenant_id}")
            return tenant

        except Exception as e:
            logger.error(f"Error updating tenant: {e}")
            raise

    def delete_tenant(self, tenant_id: str) -> bool:
        """Delete a tenant"""
        try:
            tenant = self.get_tenant_by_id(tenant_id)
            if not tenant:
                return False

            # Remove from Redis
            redis_client.delete(f"tenant:{tenant_id}")
            redis_client.delete(f"tenant_api_key:{tenant.api_key}")

            # Remove from cache
            if tenant_id in self.tenant_cache:
                del self.tenant_cache[tenant_id]
            if tenant.api_key in self.tenant_cache:
                del self.tenant_cache[tenant.api_key]

            logger.info(f"Deleted tenant: {tenant_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting tenant: {e}")
            return False

    def list_tenants(self) -> List[TenantConfig]:
        """List all tenants"""
        try:
            tenant_keys = redis_client.keys("tenant:*")
            tenants = []

            for key in tenant_keys:
                if not key.startswith(b"tenant_api_key:"):
                    tenant_data = redis_client.get(key)
                    if tenant_data:
                        tenant_config = TenantConfig(**json.loads(tenant_data))
                        tenants.append(tenant_config)

            return tenants
        except Exception as e:
            logger.error(f"Error listing tenants: {e}")
            return []

    def check_rate_limit(self, tenant_id: str) -> bool:
        """Check if tenant has exceeded rate limit"""
        try:
            current_hour = datetime.now().strftime("%Y-%m-%d-%H")
            key = f"rate_limit:{tenant_id}:{current_hour}"

            current_count = redis_client.get(key)
            if current_count is None:
                current_count = 0
            else:
                current_count = int(current_count)

            tenant = self.get_tenant_by_id(tenant_id)
            if not tenant:
                return False

            if current_count >= tenant.max_requests_per_hour:
                return False

            # Increment counter
            redis_client.incr(key)
            redis_client.expire(key, 3600)  # Expire in 1 hour

            return True

        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True  # Allow request if rate limiting fails

    def get_tenant_routing_rules(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant-specific routing rules"""
        try:
            tenant = self.get_tenant_by_id(tenant_id)
            if tenant and tenant.routing_rules:
                return tenant.routing_rules
            return {}
        except Exception as e:
            logger.error(f"Error getting tenant routing rules: {e}")
            return {}


# Global tenant manager instance
tenant_manager = TenantManager()

tenant_router = APIRouter()


@tenant_router.post("/tenants")
def create_tenant(
    tenant_config: TenantConfig,
    admin_key: str = Header(..., alias="X-Admin-Key"),
):
    if admin_key != "admin-key":
        raise HTTPException(status_code=403, detail="Admin access required")
    created_tenant = tenant_manager.create_tenant(tenant_config)
    return {"message": "Tenant created successfully", "tenant": created_tenant}


@tenant_router.get("/tenants")
def list_tenants(admin_key: str = Header(..., alias="X-Admin-Key")):
    if admin_key != "admin-key":
        raise HTTPException(status_code=403, detail="Admin access required")
    tenants = tenant_manager.list_tenants()
    return {"tenants": tenants}


@tenant_router.get("/tenants/{tenant_id}")
def get_tenant(
    tenant_id: str, admin_key: str = Header(..., alias="X-Admin-Key")
):
    if admin_key != "admin-key":
        raise HTTPException(status_code=403, detail="Admin access required")
    tenant = tenant_manager.get_tenant_by_id(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"tenant": tenant}


@tenant_router.put("/tenants/{tenant_id}")
def update_tenant(
    tenant_id: str,
    updates: dict,
    admin_key: str = Header(..., alias="X-Admin-Key"),
):
    if admin_key != "admin-key":
        raise HTTPException(status_code=403, detail="Admin access required")
    updated_tenant = tenant_manager.update_tenant(tenant_id, updates)
    return {"message": "Tenant updated successfully", "tenant": updated_tenant}


@tenant_router.delete("/tenants/{tenant_id}")
def delete_tenant(
    tenant_id: str, admin_key: str = Header(..., alias="X-Admin-Key")
):
    if admin_key != "admin-key":
        raise HTTPException(status_code=403, detail="Admin access required")
    success = tenant_manager.delete_tenant(tenant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"message": "Tenant deleted successfully"}


def get_current_tenant(x_api_key: str = Header(...)) -> TenantConfig:
    """Dependency to get current tenant from API key"""
    tenant = tenant_manager.get_tenant_by_api_key(x_api_key)
    if not tenant:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if not tenant.active:
        raise HTTPException(
            status_code=403, detail="Tenant account is inactive"
        )

    # Check rate limit
    if not tenant_manager.check_rate_limit(tenant.tenant_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    return tenant


def create_default_tenant():
    """Create default tenant if none exists"""
    try:
        tenants = tenant_manager.list_tenants()
        if not tenants:
            default_tenant = TenantConfig(
                tenant_id="default",
                name="Default Tenant",
                api_key="demo-key",
                routing_rules={
                    "default_rules": {
                        "Infrastructure": "DevOps Queue",
                        "Account": "Customer Success",
                        "Billing": "Finance Ops",
                        "Legal": "Compliance",
                        "Other": "General Inbox",
                    },
                    "priority_escalation": {
                        "Critical": "Emergency Response",
                        "High": "Senior Support",
                        "Medium": "Standard Support",
                        "Low": "General Inbox",
                    },
                    "custom_rules": [],
                },
                llm_model="mistral",
                max_requests_per_hour=1000,
                features_enabled=[
                    "async_processing",
                    "batch_processing",
                    "admin_dashboard",
                ],
            )
            tenant_manager.create_tenant(default_tenant)
            logger.info("Created default tenant")
    except Exception as e:
        logger.error(f"Error creating default tenant: {e}")


# Initialize default tenant
create_default_tenant()
