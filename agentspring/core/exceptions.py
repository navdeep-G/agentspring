"""
Custom exceptions for the AgentSpring framework.

This module defines all custom exceptions used throughout the framework.
"""

class AgentSpringError(Exception):
    """Base exception for all AgentSpring errors."""
    pass

# Agent-related exceptions
class AgentError(AgentSpringError):
    """Base exception for agent-related errors."""
    pass

class AgentExecutionError(AgentError):
    """Raised when an error occurs during agent execution."""
    pass

class AgentConfigurationError(AgentError):
    """Raised when there is an error in agent configuration."""
    pass

# Tool-related exceptions
class ToolError(AgentSpringError):
    """Base exception for tool-related errors."""
    pass

class ToolExecutionError(ToolError):
    """Raised when an error occurs during tool execution."""
    pass

class ToolValidationError(ToolError):
    """Raised when tool input validation fails."""
    pass

# Workflow-related exceptions
class WorkflowError(AgentSpringError):
    """Base exception for workflow-related errors."""
    pass

class WorkflowExecutionError(WorkflowError):
    """Raised when an error occurs during workflow execution."""
    pass

# Plugin and extension-related exceptions
class PluginError(AgentSpringError):
    """Base exception for plugin-related errors."""
    pass

class RegistrationError(PluginError):
    """Raised when there is an error during plugin registration."""
    pass

class DependencyError(PluginError):
    """Raised when a plugin has unmet dependencies."""
    pass

class ExtensionError(PluginError):
    """Raised when there is an error with an extension."""
    pass

# General framework exceptions
class ValidationError(AgentSpringError):
    """Raised when input validation fails."""
    pass

class ConfigurationError(AgentSpringError):
    """Raised when there is a configuration error."""
    pass

class ExecutionError(AgentSpringError):
    """Raised when an error occurs during execution."""
    pass

class TimeoutError(AgentSpringError):
    """Raised when an operation times out."""
    pass

class RateLimitError(AgentSpringError):
    """Raised when a rate limit is exceeded."""
    pass

class AuthenticationError(AgentSpringError):
    """Raised when authentication fails."""
    pass

class AuthorizationError(AgentSpringError):
    """Raised when authorization fails."""
    pass

class NotFoundError(AgentSpringError):
    """Raised when a resource is not found."""
    pass

class ConflictError(AgentSpringError):
    """Raised when there is a conflict with the current state."""
    pass
