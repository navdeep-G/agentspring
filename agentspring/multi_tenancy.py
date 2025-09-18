import hashlib, uuid
from sqlalchemy import select, delete
from .db.session import SessionLocal
from .db.models import Tenant, TenantUser

def _hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()

async def get_user_by_api_key(api_key: str):
    async with SessionLocal() as s:
        res = await s.execute(select(TenantUser).where(TenantUser.api_key_hash == _hash_key(api_key)))
        user = res.scalar_one_or_none()
        if not user:
            # fallback to tenant master key
            res2 = await s.execute(select(Tenant).where(Tenant.api_key_hash == _hash_key(api_key)))
            t = res2.scalar_one_or_none()
            if not t: return None
            return {"tenant_id": str(t.id), "role": "admin", "name": "owner"}
        return {"id": str(user.id), "tenant_id": str(user.tenant_id), "role": user.role, "name": user.name}

async def get_tenant_by_api_key(api_key: str):
    u = await get_user_by_api_key(api_key)
    if not u: return None
    async with SessionLocal() as s:
        t = await s.get(Tenant, uuid.UUID(u["tenant_id"]))
        return {"id": u["tenant_id"], "name": t.name if t else "tenant", "role": u["role"]}

async def create_tenant(name: str, api_key: str, rate_limit: str = "100/minute"):
    async with SessionLocal() as s:
        t = Tenant(name=name, api_key_hash=_hash_key(api_key), rate_limit=rate_limit)
        s.add(t); await s.commit(); await s.refresh(t)
        return {"id": str(t.id), "name": t.name}

async def create_tenant_user(tenant_id: str, name: str, api_key: str, role: str = "viewer"):
    assert role in ("admin","editor","viewer")
    async with SessionLocal() as s:
        from .db.models import TenantUser
        u = TenantUser(tenant_id=uuid.UUID(tenant_id), name=name, api_key_hash=_hash_key(api_key), role=role)
        s.add(u); await s.commit(); await s.refresh(u)
        return {"id": str(u.id), "name": u.name, "role": u.role}

async def list_tenant_users(tenant_id: str):
    async with SessionLocal() as s:
        from .db.models import TenantUser
        res = await s.execute(select(TenantUser).where(TenantUser.tenant_id == uuid.UUID(tenant_id)))
        return [{"id": str(u.id), "name": u.name, "role": u.role} for u in res.scalars()]

async def delete_tenant_user(tenant_id: str, user_id: str):
    async with SessionLocal() as s:
        from .db.models import TenantUser
        await s.execute(delete(TenantUser).where(TenantUser.tenant_id == uuid.UUID(tenant_id), TenantUser.id == uuid.UUID(user_id)))
        await s.commit()
        return {"ok": True}
