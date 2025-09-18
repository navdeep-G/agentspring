from typing import Any, AsyncGenerator, Optional
from pydantic import BaseModel
class ProviderConfig(BaseModel):
    model: str = "gpt-4o-mini"
    api_key: Optional[str] = None
class LLMProvider:
    async def generate_async(self, prompt: str, **kwargs) -> str: raise NotImplementedError
    async def stream_async(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]: raise NotImplementedError
