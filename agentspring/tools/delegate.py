# agentspring/tools/delegate.py
from __future__ import annotations
import os
import asyncio
import httpx
from . import tool
from agentspring.config import settings

INTERNAL_URL = os.getenv("AGENTSPRING_INTERNAL_URL", "http://127.0.0.1:8000/v1/agents/run")
MAX_DEPTH = int(os.getenv("MAX_AGENT_DEPTH", "0"))  # 0 = no limit

def _resolve_api_key(explicit: str | None) -> str:
    key = explicit or settings.API_KEY or os.getenv("API_KEY")
    if not key:
        raise RuntimeError("delegate_agent: no API key available; set API_KEY env or pass api_key")
    return key

def _next_depth(headers: dict | None = None) -> dict:
    """Propagate recursion depth using header X-Agent-Depth; enforce optional cap."""
    headers = dict(headers or {})
    current = int(headers.get("X-Agent-Depth", "0"))
    if MAX_DEPTH and current >= MAX_DEPTH:
        raise RuntimeError(f"Max delegation depth {MAX_DEPTH} reached")
    headers["X-Agent-Depth"] = str(current + 1)
    return headers

from typing import Optional, Dict

@tool(
    "delegate_agent",
    "Delegate a prompt to a sub-agent via /v1/agents/run",
    parameters={
        "type": "object",
        "properties": {
            "prompt": {"type": "string"},
            "provider": {"type": "string"},
            "stream": {"type": "boolean"},
        },
        "required": ["prompt", "provider"]
    },
)
async def delegate_agent(
    prompt: str,
    provider: str = "mock",
    stream: bool = False,
    __caller_headers__: Optional[Dict[str, str]] = None,  # injected by the API route
):
    # Prefer the tenant key from the incoming request; fall back to single-tenant API_KEY if set
    api_key = (__caller_headers__ or {}).get("X-API-Key") or (settings.API_KEY or "").strip()
    if not api_key:
        # In multi-tenant mode you MUST forward a tenant key
        raise RuntimeError("No tenant API key available for delegation. Pass X-API-Key on the outer request.")

    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

    # Call the local server inside the same container
    url = "http://127.0.0.1:8000/v1/agents/run"
    payload = {"prompt": prompt, "provider": provider, "stream": bool(stream)}

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()

@tool(
    "fanout_delegate",
    "Run multiple sub-agents in parallel and return their results array.",
    parameters={
        "type": "object",
        "properties": {
            "prompts": {"type": "array", "items": {"type": "string"}},
            "provider": {"type": "string"},
            "api_key": {"type": "string"},
            "timeout": {"type": "integer", "default": 60}
        },
        "required": ["prompts"]
    },
)
async def fanout_delegate(prompts: list[str], provider: str | None = None, api_key: str | None = None, timeout: int = 60) -> list[dict]:
    headers = {"X-API-Key": _resolve_api_key(api_key)}
    headers = _next_depth(headers)
    body_common = {"provider": provider or settings.DEFAULT_PROVIDER, "stream": False}

    async def _one(p: str):
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(INTERNAL_URL, headers=headers, json={**body_common, "prompt": p})
            r.raise_for_status()
            return r.json()

    return await asyncio.gather(*[_one(p) for p in prompts])

