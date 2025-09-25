from .registry import registry, ProviderRegistry
from .base import LLMProvider, ProviderConfig, Message, MessageRole

# For backward compatibility
get_provider = registry.get_provider
register_provider = registry.register_provider

__all__ = [
    'LLMProvider',
    'ProviderConfig',
    'Message',
    'MessageRole',
    'registry',
    'ProviderRegistry',
    'get_provider',
    'register_provider'
]
