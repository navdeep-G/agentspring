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
            
            # Validate and map parameters
            validated_kwargs = self._validate_and_map_parameters(tool, kwargs)
            
            result = tool(**validated_kwargs)
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

    def _validate_and_map_parameters(self, tool: Callable, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and map parameters to match function signature"""
        import inspect
        sig = inspect.signature(tool)
        param_names = list(sig.parameters.keys())
        
        # Common parameter name mappings
        param_mappings = {
            'is_prime': {'n': 'number', 'num': 'number', 'value': 'number'},
            'calculate': {'expr': 'expression', 'calc': 'expression', 'formula': 'expression'},
            'text_to_uppercase': {'input_text': 'text', 'input': 'text', 'string': 'text'},
            'text_to_lowercase': {'input_text': 'text', 'input': 'text', 'string': 'text'},
            'count_characters': {'input_text': 'text', 'input': 'text', 'string': 'text'},
            'generate_random': {'min': 'min_value', 'max': 'max_value', 'start': 'min_value', 'end': 'max_value'},
            'sum_range': {'start_num': 'start', 'end_num': 'end', 'from': 'start', 'to': 'end'},
        }
        
        validated = {}
        tool_name = tool.__name__
        
        for param_name, value in kwargs.items():
            # Check if parameter name needs mapping
            if tool_name in param_mappings and param_name in param_mappings[tool_name]:
                mapped_name = param_mappings[tool_name][param_name]
                if mapped_name in param_names:
                    validated[mapped_name] = value
                    continue
            
            # Direct parameter name match
            if param_name in param_names:
                validated[param_name] = value
            else:
                # Try to find a close match
                for actual_param in param_names:
                    if param_name.lower() in actual_param.lower() or actual_param.lower() in param_name.lower():
                        validated[actual_param] = value
                        break
                else:
                    # Log unknown parameter but don't fail
                    logger.warning(f"Unknown parameter '{param_name}' for tool '{tool_name}'. Available: {param_names}")
        
        return validated

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