"""
LLM Provider Registry

This module handles the registration and management of LLM providers.
"""
from typing import Dict, Type, Optional, Any

from .base import LLMProvider  # Import after base is defined to avoid circular imports

class LLMRegistry:
    """Registry for LLM providers"""
    _providers: Dict[str, Type[LLMProvider]] = {}
    _default_provider: Optional[str] = None
    _instances: Dict[str, LLMProvider] = {}
    
    @classmethod
    def register(cls, name: str, is_default: bool = False) -> callable:
        """Register a new LLM provider"""
        def decorator(provider_class: Type[LLMProvider]) -> Type[LLMProvider]:
            cls._providers[name] = provider_class
            if is_default:
                cls._default_provider = name
            return provider_class
        return decorator
    
    @classmethod
    def get_provider(cls, name: Optional[str] = None, **kwargs) -> LLMProvider:
        """Get an instance of the specified LLM provider"""
        provider_name = name or cls._default_provider
        if not provider_name:
            raise ValueError("No default LLM provider set and no provider specified")
            
        if provider_name not in cls._providers:
            raise ValueError(f"Unknown LLM provider: {provider_name}")
            
        # Create a unique cache key based on provider name and config
        config_key = str(sorted(kwargs.items()))
        cache_key = f"{provider_name}:{config_key}"
        
        if cache_key not in cls._instances:
            cls._instances[cache_key] = cls._providers[provider_name](**kwargs)
            
        return cls._instances[cache_key]
    
    @classmethod
    def list_providers(cls) -> Dict[str, Type[LLMProvider]]:
        """List all registered LLM providers"""
        return cls._providers.copy()
    
    @classmethod
    def set_default_provider(cls, name: str) -> None:
        """Set the default LLM provider"""
        if name not in cls._providers:
            raise ValueError(f"Unknown LLM provider: {name}")
        cls._default_provider = name

# Create a default registry instance
registry = LLMRegistry()

# Convenience functions
def register_provider(name: str, is_default: bool = False):
    """Register a provider with the default registry"""
    return registry.register(name, is_default)

def get_provider(name: Optional[str] = None, **kwargs) -> LLMProvider:
    """Get a provider instance from the default registry"""
    return registry.get_provider(name, **kwargs)

def list_providers() -> Dict[str, Type[LLMProvider]]:
    """List all providers in the default registry"""
    return registry.list_providers()

def set_default_provider(name: str) -> None:
    """Set the default provider in the default registry"""
    return registry.set_default_provider(name)
