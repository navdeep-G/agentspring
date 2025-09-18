from fastapi import HTTPException
ROLE_ORDER = {"viewer": 1, "editor": 2, "admin": 3}
def has_role(user_role: str, required: str) -> bool:
    return ROLE_ORDER.get(user_role, 0) >= ROLE_ORDER.get(required, 99)
def require_perm_for(required_role: str, resolve_tenant, tenant_dep):
    async def dep(tenant_hint=awaitable_dep(tenant_dep)):
        tenant = await resolve_tenant(tenant_hint)
        role = tenant.get("role", "viewer")
        if not has_role(role, required_role):
            raise HTTPException(403, f"Requires role {required_role} (current: {role})")
        return tenant
    return dep
async def awaitable_dep(dep):
    # helper to allow wrapping dep call inside other deps
    return dep
