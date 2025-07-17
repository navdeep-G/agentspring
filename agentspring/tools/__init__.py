import logging
import inspect
from typing import Dict, Any, List, Optional, Callable, Union
from functools import wraps
from pydantic import BaseModel, Field
from datetime import datetime

logger = logging.getLogger(__name__)

class ToolSchema(BaseModel):
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters schema")
    returns: Dict[str, Any] = Field(..., description="Tool return schema")

class ToolExecutionResult(BaseModel):
    success: bool = Field(..., description="Whether execution was successful")
    result: Any = Field(None, description="Tool execution result")
    error: Optional[str] = Field(None, description="Error message if failed")
    execution_time: float = Field(..., description="Execution time in seconds")
    timestamp: datetime = Field(default_factory=datetime.now)

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: Dict[str, ToolSchema] = {}
        self._permissions: Dict[str, List[str]] = {}

    def register(self, name: str, description: str = "", permissions: List[str] = []):
        if description is None:
            description = ""
        if permissions is None:
            permissions = []
        def decorator(func: Callable):
            schema = self._generate_schema(func, name, description or func.__doc__ or "")
            self._tools[name] = func
            self._schemas[name] = schema
            if permissions:
                self._permissions[name] = permissions
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def _generate_schema(self, func: Callable, name: str, description: str) -> ToolSchema:
        sig = inspect.signature(func)
        parameters = {}
        required = []
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else str
            param_desc = f"Parameter {param_name}"
            if param_type == str:
                param_schema = {"type": "string", "description": param_desc}
            elif param_type == int:
                param_schema = {"type": "integer", "description": param_desc}
            elif param_type == float:
                param_schema = {"type": "number", "description": param_desc}
            elif param_type == bool:
                param_schema = {"type": "boolean", "description": param_desc}
            elif param_type == list or param_type == List[str]:
                param_schema = {"type": "array", "items": {"type": "string"}, "description": param_desc}
            else:
                param_schema = {"type": "string", "description": param_desc}
            parameters[param_name] = param_schema
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        if required:
            parameters["required"] = required
        return ToolSchema(
            name=name,
            description=description,
            parameters=parameters,
            returns={"type": "object", "description": "Execution result"}
        )

    def get_tool(self, name: str) -> Optional[Callable]:
        return self._tools.get(name)

    def get_schema(self, name: str) -> Optional[ToolSchema]:
        return self._schemas.get(name)

    def list_tools(self) -> List[str]:
        return list(self._tools.keys())

    def get_all_schemas(self) -> Dict[str, ToolSchema]:
        return self._schemas.copy()

    def execute_tool(self, name: str, **kwargs) -> ToolExecutionResult:
        start_time = datetime.now()
        try:
            tool = self.get_tool(name)
            if not tool:
                return ToolExecutionResult(
                    success=False,
                    result=None,
                    error=f"Tool '{name}' not found",
                    execution_time=0.0
                )
            result = tool(**kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            return ToolExecutionResult(
                success=True,
                result=result,
                error=None,
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error executing tool '{name}': {e}")
            return ToolExecutionResult(
                success=False,
                result=None,
                error=str(e),
                execution_time=execution_time
            )

# Global tool registry instance
tool_registry = ToolRegistry()

def tool(name: str, description: str = "", permissions: List[str] = []):
    return tool_registry.register(name, description, permissions)

# Import all tool modules to register them
from . import communication
from . import data_storage
from . import web_search
from . import business
from . import media
from . import system

# Export the main classes and functions
__all__ = [
    ToolRegistry,
    ToolSchema,
    ToolExecutionResult,
    tool,
    tool_registry
] 