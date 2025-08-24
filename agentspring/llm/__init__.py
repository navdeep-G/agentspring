"""
LLM Provider System

This package provides a flexible and extensible system for integrating multiple LLM providers
with support for sync/async operations, rate limiting, and error handling.
"""

__version__ = "0.1.0"

# Core interfaces and base classes
from .base import (
    LLMError,
    LLMProvider,
    ProviderConfig,
    RateLimitConfig,
    RateLimitError,
)

# Registry functionality
from .registry import (
    LLMRegistry,
    get_provider,
    list_providers,
    register_provider,
    set_default_provider,
)

# Re-export for convenience
__all__ = [
    # Core classes
    "LLMProvider",
    "LLMError",
    "RateLimitError",
    "ProviderConfig",
    "RateLimitConfig",
    # Registry functions
    "LLMRegistry",
    "register_provider",
    "get_provider",
    "list_providers",
    "set_default_provider",
]
