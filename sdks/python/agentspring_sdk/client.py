import asyncio, json, httpx
from typing import AsyncGenerator, Optional, Dict, Any

class AgentSpringClient:
    def __init__(self, base_url: str, api_key: str, bearer_token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.bearer_token = bearer_token
        headers = {"X-API-Key": self.api_key}
        if bearer_token: headers["Authorization"] = f"Bearer {bearer_token}"
        self._client = httpx.AsyncClient(base_url=self.base_url, headers=headers)

    async def close(self): await self._client.aclose()

    async def run(self, prompt: str, provider: str = "openai") -> Dict[str, Any]:
        r = await self._client.post("/v1/agents/run", json={"prompt": prompt, "provider": provider, "stream": False}); r.raise_for_status(); return r.json()

    async def stream(self, prompt: str, provider: str = "openai") -> AsyncGenerator[Dict[str, Any], None]:
        headers = {"Accept":"text/event-stream"}
        async with self._client.stream("POST", "/v1/agents/run", json={"prompt": prompt, "provider": provider, "stream": True}, headers=headers) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line or not line.startswith("data: "): continue
                data = line[len("data: "):]
                try: yield json.loads(data)
                except Exception: yield {"type":"text","data": data}

    async def upsert_doc(self, collection: str, doc_id: str, text: str, metadata: dict = None) -> Dict[str, Any]:
        r = await self._client.post(f"/v1/collections/{collection}/docs", json={"doc_id": doc_id, "text": text, "metadata": metadata or {}}); r.raise_for_status(); return r.json()

    async def search(self, collection: str, q: str, k: int = 5) -> Dict[str, Any]:
        r = await self._client.get(f"/v1/collections/{collection}/search", params={"q": q, "k": k}); r.raise_for_status(); return r.json()
