# agentspring/tools/__init__.py
from __future__ import annotations
from typing import Callable, Awaitable, Any, Dict, Iterable, List

# Global maps
_fn_map: Dict[str, Callable[..., Awaitable[Any]]] = {}
_schema_map: Dict[str, dict] = {}


class ToolRegistry:
    """
    Planner/Executor-compatible registry:
    - Dict-like API: get/keys/items/__contains__/__getitem__
    - Schemas via .as_schemas()
    - OpenAI functions format via .to_openai_functions()
    - Self-referential .registry to satisfy code that expects tools.registry
    """
    def __init__(self, fn_map: Dict[str, Callable[..., Awaitable[Any]]] | None = None,
                 schema_map: Dict[str, dict] | None = None):
        self._fns = fn_map or _fn_map
        self._schemas = schema_map or _schema_map
        # Some planners expect `tools.registry` (often a dict); point it to self
        self.registry: ToolRegistry = self
        # Some code may read `tools.schemas`
        self.schemas: Dict[str, dict] = self._schemas

    # --- Dict-like ---
    def get(self, name: str):
        return self._fns.get(name)

    def keys(self) -> Iterable[str]:
        return self._fns.keys()

    def items(self):
        return self._fns.items()

    def values(self):
        return self._fns.values()

    def __contains__(self, k: str) -> bool:
        return k in self._fns

    def __getitem__(self, k: str):
        return self._fns[k]

    # --- Registration ---
    def register(self, name: str, fn: Callable[..., Awaitable[Any]], schema: dict | None = None) -> None:
        self._fns[name] = fn
        if schema:
            self._schemas[name] = schema

    # --- Introspection ---
    def as_schemas(self) -> Dict[str, dict]:
        return dict(self._schemas)

    def to_openai_functions(self) -> List[dict]:
        """Return list in OpenAI 'tools' format: {'type':'function','function':{name,description,parameters}}."""
        out: List[dict] = []
        for name, s in self._schemas.items():
            out.append({
                "type": "function",
                "function": {
                    "name": s.get("name", name),
                    "description": s.get("description", ""),
                    "parameters": s.get("parameters", {"type": "object", "properties": {}, "required": []}),
                },
            })
        return out


# Global registry instance exposed to the rest of the app
tool_registry = ToolRegistry(_fn_map, _schema_map)


def tool(name: str, description: str = "", parameters: dict | None = None):
    """
    Decorator to register a tool with schema.
    Usage:
        @tool("math_eval", "Evaluate arithmetic", parameters={...})
        async def math_eval(expr: str) -> float: ...
    """
    def _wrap(fn: Callable[..., Awaitable[Any]]):
        _fn_map[name] = fn
        _schema_map[name] = {
            "name": name,
            "description": description or "",
            "parameters": parameters or {"type": "object", "properties": {}, "required": []},
        }
        return fn
    return _wrap


# Back-compat names some code may import
registry = tool_registry
schemas = _schema_map

__all__ = ["tool_registry", "registry", "schemas", "tool", "ToolRegistry"]

