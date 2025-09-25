# agentspring/llm/registry.py
from typing import Dict, Type, Optional, Any
from .base import LLMProvider
from ..models import ToolDefinition

class ProviderRegistry:
    _instance = None
    _providers: Dict[str, Type[LLMProvider]] = {}
    _default_provider: Optional[str] = "mock"
    _tools: Dict[str, ToolDefinition] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProviderRegistry, cls).__new__(cls)
        return cls._instance

    def register_provider(self, name: str, provider_cls: Type[LLMProvider], is_default: bool = False):
        self._providers[name] = provider_cls
        if is_default or not self._default_provider:
            self._default_provider = name

    def get_provider(self, name: Optional[str] = None) -> LLMProvider:
        provider_name = name or self._default_provider
        if not provider_name or provider_name not in self._providers:
            raise ValueError(f"Provider '{provider_name}' not found")
        return self._providers[provider_name]()

    def register_tool(self, tool_def: ToolDefinition):
        self._tools[tool_def.name] = tool_def

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self) -> list:
        return list(self._tools.values())

# Global registry instance
registry = ProviderRegistry()

# For backward compatibility
def get_provider(name: str = None) -> LLMProvider:
    return registry.get_provider(name)

def register_provider(name: str, provider_cls: Type[LLMProvider], is_default: bool = False):
    registry.register_provider(name, provider_cls, is_default)

# Export the registry and functions
__all__ = ['registry', 'ProviderRegistry', 'get_provider', 'register_provider']