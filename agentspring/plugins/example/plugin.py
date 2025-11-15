"""
Example plugin for the AgentSpring framework.
"""
from typing import Dict, Any, Optional, List, Type
import asyncio

from agentspring.plugin.base import BasePlugin, PluginMetadata
from agentspring.core import Context, Message, MessageRole

class ExamplePlugin(BasePlugin):
    """An example plugin that demonstrates the plugin system functionality."""
    
    def __init__(self):
        super().__init__()
        self._metadata = PluginMetadata(
            name="example",
            version="0.1.0",
            description="An example plugin for testing the AgentSpring plugin system",
            author="Your Name",
            dependencies=[]
        )
    
    @property
    def name(self) -> str:
        """Get the plugin name."""
        return self._metadata.name
    
    @property
    def version(self) -> str:
        """Get the plugin version."""
        return self._metadata.version
    
    @property
    def description(self) -> str:
        """Get the plugin description."""
        return self._metadata.description
    
    @property
    def author(self) -> str:
        """Get the plugin author."""
        return self._metadata.author
    
    @property
    def state(self) -> str:
        """Get the plugin state."""
        return str(self._state)
    
    @property
    def dependencies(self) -> List[str]:
        """Get the plugin dependencies."""
        return self._metadata.dependencies
    
    async def on_load(self):
        """Called when the plugin is loaded."""
        print(f"{self.name} plugin loaded!")
    
    async def on_enable(self):
        """Called when the plugin is enabled."""
        print(f"{self.name} plugin enabled!")
    
    async def on_disable(self):
        """Called when the plugin is disabled."""
        print(f"{self.name} plugin disabled!")
    
    async def greet(self, name: str) -> str:
        """Example method that can be called on the plugin.
        
        Args:
            name: The name to include in the greeting.
            
        Returns:
            A friendly greeting.
        """
        return f"Hello, {name}! This is a greeting from the example plugin."

# Required plugin entry point
def create_plugin():
    """Create and return an instance of the plugin."""
    return ExamplePlugin()
