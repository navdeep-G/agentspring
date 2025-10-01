"""
Core components of the AgentSpring framework.

This module provides the fundamental building blocks for creating agents, tools,
workflows, and plugins in the AgentSpring ecosystem.
"""

# Import base classes
from .base import (
    Agent,
    AgentConfig,
    Tool,
    ToolParameter,
    Workflow,
    Plugin,
    ExtensionPoint,
    Message,
    MessageRole,
    Context,
)

# Import extension registry
from .extensions import ExtensionRegistry, registry

# Import exceptions
from .exceptions import (
    # Base exception
    AgentSpringError,
    
    # Agent exceptions
    AgentError,
    AgentExecutionError,
    AgentConfigurationError,
    
    # Tool exceptions
    ToolError,
    ToolExecutionError,
    ToolValidationError,
    
    # Workflow exceptions
    WorkflowError,
    WorkflowExecutionError,
    
    # Plugin and extension exceptions
    PluginError,
    RegistrationError,
    DependencyError,
    ExtensionError,
    
    # General framework exceptions
    ValidationError,
    ConfigurationError,
    ExecutionError,
    TimeoutError,
    RateLimitError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
)

__all__ = [
    # Core classes
    'Agent',
    'AgentConfig',
    'Tool',
    'ToolParameter',
    'Workflow',
    'Plugin',
    'ExtensionPoint',
    'Message',
    'MessageRole',
    'Context',
    'ExtensionRegistry',
    'registry',
    
    # Exceptions
    'AgentSpringError',
    'AgentError',
    'AgentExecutionError',
    'AgentConfigurationError',
    'ToolError',
    'ToolExecutionError',
    'ToolValidationError',
    'WorkflowError',
    'WorkflowExecutionError',
    'PluginError',
    'RegistrationError',
    'DependencyError',
    'ExtensionError',
    'ValidationError',
    'ConfigurationError',
    'ExecutionError',
    'TimeoutError',
    'RateLimitError',
    'AuthenticationError',
    'AuthorizationError',
    'NotFoundError',
    'ConflictError',
]
