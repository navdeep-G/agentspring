from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel

class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

class Message(BaseModel):
    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None

class ProviderConfig(BaseModel):
    model: str = "mock"
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    api_key: Optional[str] = None

T = TypeVar('T', bound='LLMProvider')

class LLMProvider:
    def __init__(self, config: Optional[ProviderConfig] = None):
        self.config = config or ProviderConfig()

    @classmethod
    def from_config(cls: Type[T], config: Dict[str, Any]) -> T:
        return cls(ProviderConfig(**config))
        
    async def generate_async(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError("Subclasses must implement generate_async")
        
    async def stream_async(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        raise NotImplementedError("Subclasses must implement stream_async")