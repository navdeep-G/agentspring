import os
from typing import AsyncGenerator, Optional
from openai import AsyncOpenAI
from pydantic import Field
from ..base import LLMProvider, ProviderConfig
from ..registry import register_provider
class AzureOpenAIConfig(ProviderConfig):
    model: str = Field(default="gpt-4o-mini")  # deployment name
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    api_version: str = "2024-06-01"
@register_provider("azure_openai")
class AzureOpenAIProvider(LLMProvider):
    def __init__(self, config: Optional[AzureOpenAIConfig] = None):
        self.config = config or AzureOpenAIConfig()
        key = self.config.api_key or os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = self.config.endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = self.config.api_version or os.getenv("AZURE_OPENAI_API_VERSION","2024-06-01")
        if not key or not endpoint: raise RuntimeError("AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT must be set")
        self.client = AsyncOpenAI(api_key=key, base_url=f"{endpoint}/openai", default_query={"api-version": api_version})
        self.deployment = self.config.model
    async def generate_async(self, prompt: str, **kwargs) -> str:
        messages = kwargs.get("messages") or [{"role":"user","content":prompt}]
        tools = kwargs.get("tools")
        resp = await self.client.chat.completions.create(model=self.deployment, messages=messages, tools=tools,
            tool_choice=kwargs.get("tool_choice","auto") if tools else None, temperature=kwargs.get("temperature",0.2))
        ch = resp.choices[0]; msg = ch.message
        if ch.finish_reason == "tool_calls": return msg.model_dump_json()
        return msg.content or ""
    async def stream_async(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        messages = kwargs.get("messages") or [{"role":"user","content":prompt}]
        tools = kwargs.get("tools")
        stream = await self.client.chat.completions.create(model=self.deployment, messages=messages, tools=tools,
            tool_choice=kwargs.get("tool_choice","auto") if tools else None, temperature=kwargs.get("temperature",0.2), stream=True)
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content: yield delta.content
