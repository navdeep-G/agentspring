"""
Example plugin for the AgentSpring framework.

This module demonstrates how to create a plugin with extension points, tools, and agents.
"""
from typing import Dict, Any, Optional, List, Type
import asyncio
from abc import ABC, abstractmethod

from agentspring.core import (
    Plugin,
    Tool,
    Agent,
    AgentConfig,
    ExtensionPoint,
    Message,
    MessageRole,
    Context,
    registry,
)

# Define an extension point for greeting implementations
class GreetingExtensionPoint(ExtensionPoint, ABC):
    """Extension point for greeting implementations."""
    
    @classmethod
    def get_interface(cls) -> Type['GreetingExtensionPoint']:
        return GreetingExtensionPoint
    
    @abstractmethod
    async def greet(self, name: str) -> str:
        """Generate a greeting for the given name.
        
        Args:
            name: The name to greet.
            
        Returns:
            A greeting string.
        """
        pass

# Implement some greeting extensions
class EnglishGreeter(GreetingExtensionPoint):
    """English language greeter implementation."""
    
    async def greet(self, name: str) -> str:
        """Generate an English greeting."""
        return f"Hello, {name}!"
    
    @classmethod
    def get_interface(cls) -> Type[GreetingExtensionPoint]:
        return GreetingExtensionPoint

class SpanishGreeter(GreetingExtensionPoint):
    """Spanish language greeter implementation."""
    
    async def greet(self, name: str) -> str:
        """Generate a Spanish greeting."""
        return f"¡Hola, {name}!"
    
    @classmethod
    def get_interface(cls) -> Type[GreetingExtensionPoint]:
        return GreetingExtensionPoint

# Define a tool that uses the greeting extensions
class GreeterTool(Tool):
    """A tool that greets users in different languages."""
    
    def __init__(self):
        super().__init__(
            name="greeter",
            description="Greet a person in different languages",
            parameters=[
                {
                    "name": "name",
                    "type": "string",
                    "description": "The name of the person to greet",
                    "required": True
                },
                {
                    "name": "language",
                    "type": "string",
                    "description": "The language to use (en, es)",
                    "required": False,
                    "default": "en"
                }
            ]
        )
    
    async def execute(self, params: Dict[str, Any], context: Optional[Context] = None) -> str:
        """Execute the greeter tool.
        
        Args:
            params: Dictionary containing the following keys:
                - name: (str) The name to greet (required)
                - language: (str) The language to use (optional, defaults to 'en')
            context: Optional execution context
            
        Returns:
            A greeting string
            
        Raises:
            KeyError: If the 'name' parameter is missing
        """
        if "name" not in params or params["name"] is None:
            raise KeyError("The 'name' parameter is required")
            
        name = str(params["name"])  # Convert to string in case it's a number or other type
        language = params.get("language", "en")
        
        # Get all registered greeters
        greeters = registry.get_extensions(GreetingExtensionPoint)
        
        # Find a greeter for the requested language
        greeter_map = {
            'en': EnglishGreeter,
            'es': SpanishGreeter
        }
        
        greeter_class = greeter_map.get(language, EnglishGreeter)
        greeter = greeter_class()
        
        return await greeter.greet(name)

# Define an example agent
class ExampleAgentConfig(AgentConfig):
    """Configuration for the example agent."""
    greeting: str = "Hello, World!"

class ExampleAgent(Agent[ExampleAgentConfig]):
    """An example agent that uses the greeter tool."""
    
    @classmethod
    def get_default_config(cls) -> ExampleAgentConfig:
        return ExampleAgentConfig()
    
    async def execute(
        self,
        messages: List[Message],
        context: Optional[Context] = None,
        **kwargs
    ) -> Message:
        """Process a message and return a response."""
        # Use the greeter tool to generate a greeting
        greeter = GreeterTool()
        greeting = await greeter.execute({"name": "World"}, context)
        
        return Message(
            role=MessageRole.ASSISTANT,
            content=greeting
        )

# Define the plugin
class ExamplePlugin(Plugin):
    """An example plugin that provides a greeter tool and agent."""
    
    def __init__(self):
        super().__init__(
            name="example",
            version="0.1.0",
            description="An example plugin for the AgentSpring framework"
        )
    
    def register_extensions(self, registry: 'ExtensionRegistry') -> None:
        """Register extensions provided by this plugin."""
        # Register the greeter tool
        registry.register_extension(GreetingExtensionPoint, EnglishGreeter())
        registry.register_extension(GreetingExtensionPoint, SpanishGreeter())
    
    def get_tools(self) -> List[Tool]:
        """Return tools provided by this plugin."""
        return [GreeterTool()]
    
    def get_agents(self) -> List[Type[Agent]]:
        """Return agents provided by this plugin."""
        return [ExampleAgent]

# Create a plugin instance for auto-discovery
__plugin__ = ExamplePlugin()
