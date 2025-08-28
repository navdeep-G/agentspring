"""Memory interfaces (stubs): short-term & long-term"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


class Memory:
    def remember(self, key: str, value: Any) -> None:
        raise NotImplementedError

    def recall(self, key: str, default: Any = None) -> Any:
        raise NotImplementedError


@dataclass
class InMemoryMemory(Memory):
    _store: Dict[str, Any] = field(default_factory=dict)

    def remember(self, key: str, value: Any) -> None:
        self._store[key] = value

    def recall(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)


__all__ = ["Memory", "InMemoryMemory"]
