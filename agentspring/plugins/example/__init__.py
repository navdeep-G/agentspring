"""
Example plugin for the AgentSpring framework.

This module demonstrates how to create a plugin with extension points, tools, and agents.
"""
from typing import Dict, Any, Optional, List, Type
import asyncio
from abc import ABC, abstractmethod

from agentspring.core import (
    Tool,
    Agent,
    AgentConfig,
    ExtensionPoint,
    Message,
    MessageRole,
    Context,
    registry,
)

# Import the plugin class from the plugin module
from .plugin import ExamplePlugin, create_plugin

__all__ = ['ExamplePlugin', 'create_plugin']
