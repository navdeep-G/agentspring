"""
Custom exceptions for the AgentSpring plugin system.
"""

class PluginError(Exception):
    """Base class for all plugin-related exceptions."""
    pass

class PluginLoadError(PluginError):
    """Raised when a plugin fails to load."""
    pass

class PluginDependencyError(PluginError):
    """Raised when a plugin has unresolved dependencies."""
    pass

class PluginConflictError(PluginError):
    """Raised when there is a conflict between plugins."""
    pass

class PluginVersionError(PluginError):
    """Raised when there is a version incompatibility."""
    pass

__all__ = [
    'PluginError',
    'PluginLoadError',
    'PluginDependencyError',
    'PluginConflictError',
    'PluginVersionError',
]