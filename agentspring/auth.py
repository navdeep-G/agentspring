# agentspring/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Optional

# List of valid API keys (in production, store these securely and check against a database)
VALID_API_KEYS = {
    "test-api-key": {"user_id": "test-user", "is_admin": True},
    "your-admin-key": {"user_id": "admin", "is_admin": True}
}

api_key_header = APIKeyHeader(name="X-API-Key")

async def get_current_user(api_key: str = Depends(api_key_header)):
    if not api_key or api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "API-Key"},
        )
    return VALID_API_KEYS[api_key]