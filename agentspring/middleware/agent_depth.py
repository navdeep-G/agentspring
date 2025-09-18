from __future__ import annotations
import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

MAX_DEPTH = int(os.getenv("MAX_AGENT_DEPTH", "0"))  # 0 disables guard

class AgentDepthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if MAX_DEPTH:
            depth = int(request.headers.get("X-Agent-Depth", "0"))
            if depth > MAX_DEPTH:
                return JSONResponse({"detail": f"Max agent depth {MAX_DEPTH} exceeded"}, status_code=400)
        return await call_next(request)

