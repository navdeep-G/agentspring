"""
This module provides a flexible plugin system for AgentSpring, allowing for dynamic
loading and management of plugins with dependency resolution, version checking,
and resource management.
"""

from .base import BasePlugin, PluginMetadata, PluginState
from .manager import PluginManager
from .exceptions import (
    PluginError,
    PluginLoadError,
    PluginDependencyError,
    PluginConflictError,
    PluginVersionError,
)

__version__ = "0.1.0"

__all__ = [
    # Core classes
    'BasePlugin',
    'PluginManager',
    'PluginMetadata',
    'PluginState',
    
    # Exceptions
    'PluginError',
    'PluginLoadError',
    'PluginDependencyError',
    'PluginConflictError',
    'PluginVersionError',
]

# Set default logging handler to avoid "No handler found" warnings
import logging
logging.getLogger('agentspring.plugin').addHandler(logging.NullHandler())