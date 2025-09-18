from typing import Dict, Type, Optional
from .base import LLMProvider
_REGISTRY: Dict[str, Type[LLMProvider]] = {}
_DEFAULT: Optional[str] = None
def register_provider(name: str):
    def deco(cls: Type[LLMProvider]):
        global _DEFAULT; _REGISTRY[name]=cls
        if _DEFAULT is None: _DEFAULT = name
        return cls
    return deco
def get_provider(name: Optional[str] = None, **kwargs) -> LLMProvider:
    key = name or _DEFAULT
    if not key or key not in _REGISTRY: raise KeyError(f"No LLM provider registered under '{name}'")
    cls = _REGISTRY[key]; config = kwargs.get("config", None)
    return cls(config) if config is not None else cls()  # type: ignore
