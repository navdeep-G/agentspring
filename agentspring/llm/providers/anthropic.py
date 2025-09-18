import os
from typing import AsyncGenerator, Optional
from anthropic import AsyncAnthropic
from pydantic import Field
from ..base import LLMProvider, ProviderConfig
from ..registry import register_provider
class AnthropicConfig(ProviderConfig):
    model: str = Field(default="claude-3-5-sonnet-20240620")
    api_key: Optional[str] = None
@register_provider("anthropic")
class AnthropicProvider(LLMProvider):
    def __init__(self, config: Optional[AnthropicConfig] = None):
        self.config = config or AnthropicConfig()
        key = self.config.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not key: raise RuntimeError("ANTHROPIC_API_KEY not set")
        self.client = AsyncAnthropic(api_key=key)
    async def generate_async(self, prompt: str, **kwargs) -> str:
        messages = kwargs.get("messages") or [{"role":"user","content":prompt}]
        content = []
        for m in messages:
            if m["role"] == "user": content.append({"role":"user","content":m["content"]})
            elif m["role"] in ("assistant","system"): content.append({"role":"assistant","content":m["content"]})
        resp = await self.client.messages.create(model=self.config.model, max_tokens=1024, messages=content, temperature=kwargs.get("temperature",0.2))
        parts = [b.text for b in resp.content if b.type == "text"]; return "".join(parts)
    async def stream_async(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        messages = kwargs.get("messages") or [{"role":"user","content":prompt}]
        content = []
        for m in messages:
            if m["role"] == "user": content.append({"role":"user","content":m["content"]})
            elif m["role"] in ("assistant","system"): content.append({"role":"assistant","content":m["content"]})
        async with self.client.messages.stream(model=self.config.model, max_tokens=1024, messages=content) as stream:
            async for event in stream:
                if event.type == "content_block_delta" and event.delta.get("type") == "text_delta":
                    yield event.delta.get("text","")
