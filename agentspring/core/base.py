"""
Base classes and interfaces for the AgentSpring framework.

This module defines the core abstractions that form the foundation of the framework.
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Callable, Awaitable

from pydantic import BaseModel, Field, field_validator, ConfigDict

TConfig = TypeVar('TConfig', bound='AgentConfig')

class MessageRole(str, Enum):
    """Role of a message in a conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

class Message(BaseModel):
    """A message in a conversation."""
    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def model_dump(self, **kwargs):
        """Custom model dump to handle Enum serialization."""
        data = super().model_dump(**kwargs)
        if 'role' in data and isinstance(data['role'], Enum):
            data['role'] = data['role'].value
        return data

class Context(BaseModel):
    """Execution context for agents and tools."""
    workflow_id: str
    execution_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    callbacks: Dict[str, List[Callable]] = Field(default_factory=dict, exclude=True)
    
    def on(self, event: str, callback: Callable[[Dict[str, Any]], Awaitable[None]]):
        """Register a callback for an event."""
        self.callbacks.setdefault(event, []).append(callback)
        return self
    
    async def emit(self, event: str, data: Optional[Dict[str, Any]] = None):
        """Emit an event."""
        data = data or {}
        for callback in self.callbacks.get(event, []):
            await callback(data)

class ToolParameter(BaseModel):
    """Definition of a tool parameter."""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None
    enum: Optional[List[str]] = None

class Tool(ABC):
    """Base class for tools that can be used by agents."""
    
    def __init__(self, name: str, description: str, parameters: List[ToolParameter]):
        self.name = name
        self.description = description
        self.parameters = parameters
    
    @abstractmethod
    async def execute(self, params: Dict[str, Any], context: Optional[Context] = None) -> Any:
        """Execute the tool with the given parameters and context."""
        pass

class AgentConfig(BaseModel):
    """Base configuration class for agents."""
    model_config = ConfigDict(extra='forbid')

class Agent(Generic[TConfig], ABC):
    """Base class for agents."""
    
    def __init__(self, config: Optional[TConfig] = None):
        self.config = config or self.get_default_config()
    
    @classmethod
    @abstractmethod
    def get_default_config(cls) -> TConfig:
        """Return the default configuration for this agent."""
        pass
    
    @abstractmethod
    async def execute(
        self,
        messages: List[Message],
        context: Optional[Context] = None,
        **kwargs
    ) -> Message:
        """Process a list of messages and return a response."""
        pass

class Workflow(ABC):
    """Base class for workflows that coordinate multiple agents and tools."""
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any], context: Optional[Context] = None) -> Dict[str, Any]:
        """Execute the workflow with the given input and context."""
        pass

class ExtensionPoint(ABC):
    """Base class for extension points that can be extended by plugins."""
    
    @classmethod
    @abstractmethod
    def get_interface(cls) -> Type['ExtensionPoint']:
        """Return the interface that this extension point implements."""
        pass

class Plugin(ABC):
    """Base class for plugins that extend the framework's functionality."""
    
    def __init__(self, name: str, version: str, description: str = ""):
        self.name = name
        self.version = version
        self.description = description
    
    @abstractmethod
    def register_extensions(self, registry: 'ExtensionRegistry') -> None:
        """Register extensions provided by this plugin."""
        pass
    
    def get_tools(self) -> List[Type[Tool]]:
        """Return tools provided by this plugin."""
        return []
    
    def get_agents(self) -> List[Type[Agent]]:
        """Return agents provided by this plugin."""
        return []
    
    def get_workflows(self) -> List[Type[Workflow]]:
        """Return workflows provided by this plugin."""
        return []
