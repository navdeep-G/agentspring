import os
from typing import AsyncGenerator, Optional
from openai import AsyncOpenAI
from pydantic import Field
from ..base import LLMProvider, ProviderConfig
from ..registry import register_provider
class OpenAIConfig(ProviderConfig):
    model: str = Field(default="gpt-4o-mini")
    api_key: Optional[str] = None
    json_mode: bool = True
@register_provider("openai")
class OpenAIProvider(LLMProvider):
    def __init__(self, config: Optional[OpenAIConfig] = None):
        self.config = config or OpenAIConfig()
        api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key: raise RuntimeError("OPENAI_API_KEY not set")
        self.client = AsyncOpenAI(api_key=api_key)
    async def generate_async(self, prompt: str, **kwargs) -> str:
        messages = kwargs.get("messages") or [{"role":"user","content":prompt}]
        tools = kwargs.get("tools")
        response_format = {"type":"json_object"} if (kwargs.get("response_json") or self.config.json_mode) else None
        resp = await self.client.chat.completions.create(model=self.config.model, messages=messages, tools=tools,
            tool_choice=kwargs.get("tool_choice","auto") if tools else None, temperature=kwargs.get("temperature",0.2),
            response_format=response_format)
        ch = resp.choices[0]; msg = ch.message
        if ch.finish_reason == "tool_calls": return msg.model_dump_json()
        return msg.content or ""
    async def stream_async(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        messages = kwargs.get("messages") or [{"role":"user","content":prompt}]
        tools = kwargs.get("tools")
        response_format = {"type":"json_object"} if (kwargs.get("response_json") or self.config.json_mode) else None
        stream = await self.client.chat.completions.create(model=self.config.model,messages=messages,tools=tools,
            tool_choice=kwargs.get("tool_choice","auto") if tools else None, temperature=kwargs.get("temperature",0.2),
            response_format=response_format, stream=True)
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content: yield delta.content
