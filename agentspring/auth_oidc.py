import time, httpx
from typing import Dict
from jose import jwt
from functools import lru_cache
from .config import settings

class OIDCError(Exception): ...

@lru_cache(maxsize=1)
def _well_known():
    if not settings.OIDC_ISSUER:
        raise OIDCError("OIDC issuer not configured")
    return f"{settings.OIDC_ISSUER.rstrip('/')}/.well-known/openid-configuration"

@lru_cache(maxsize=1)
def _jwks_uri():
    with httpx.Client(timeout=10) as c:
        r = c.get(_well_known()); r.raise_for_status()
        return r.json()["jwks_uri"]

@lru_cache(maxsize=1)
def _jwks():
    with httpx.Client(timeout=10) as c:
        r = c.get(_jwks_uri()); r.raise_for_status()
        return r.json()

def verify_bearer(token: str) -> Dict:
    if not settings.OIDC_ISSUER or not settings.OIDC_AUDIENCE:
        raise OIDCError("OIDC not enabled")
    claims = jwt.decode(token, _jwks(), algorithms=["RS256","RS384","RS512","ES256","ES384"], audience=settings.OIDC_AUDIENCE, issuer=settings.OIDC_ISSUER.rstrip("/"))
    if claims.get("exp") and time.time() > claims["exp"]:
        raise OIDCError("Token expired")
    return claims
