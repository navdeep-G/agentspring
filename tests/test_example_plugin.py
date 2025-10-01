"""
Tests for the example plugin.

These tests demonstrate how to use the example plugin and its components.
"""
import asyncio
import pytest
from unittest.mock import MagicMock, patch

from agentspring.core import (
    ExtensionRegistry,
    Message,
    MessageRole,
    Context,
    ToolParameter
)
from agentspring.plugins.example import (
    ExamplePlugin,
    GreeterTool,
    ExampleAgent,
    EnglishGreeter,
    SpanishGreeter,
    GreetingExtensionPoint
)

@pytest.fixture
def registry():
    """Fixture that provides a clean extension registry."""
    registry = ExtensionRegistry()
    yield registry
    # Clean up after tests
    for plugin_name in list(registry._plugins.keys()):
        registry.unregister_plugin(plugin_name)

@pytest.mark.asyncio
async def test_greeter_tool():
    """Test the GreeterTool with different languages."""
    tool = GreeterTool()
    context = Context(workflow_id="test", execution_id="1")
    
    # Test English greeting
    result = await tool.execute({"name": "Alice", "language": "en"}, context)
    assert result == "Hello, Alice!"
    
    # Test Spanish greeting
    result = await tool.execute({"name": "Bob", "language": "es"}, context)
    assert result == "¡Hola, Bob!"
    
    # Test default language (English)
    result = await tool.execute({"name": "Charlie"}, context)
    assert result == "Hello, Charlie!"

@pytest.mark.asyncio
async def test_example_agent():
    """Test the ExampleAgent with the greeter tool."""
    agent = ExampleAgent()
    context = Context(workflow_id="test", execution_id="1")
    
    # Test agent execution
    messages = [Message(role=MessageRole.USER, content="Hello")]
    response = await agent.execute(messages, context)
    
    assert isinstance(response, Message)
    assert response.role == MessageRole.ASSISTANT
    assert response.content == "Hello, World!"

def test_plugin_registration():
    """Test that the plugin can be registered and provides the expected components."""
    plugin = ExamplePlugin()
    registry = ExtensionRegistry()
    
    # Register the plugin
    registry.register_plugin(plugin)
    
    # Check that the plugin is registered
    assert plugin.name in registry._plugins
    assert registry.get_plugin(plugin.name) == plugin
    
    # Check that the tool is available
    tools = registry.get_tools()
    assert any(isinstance(tool, GreeterTool) for tool in tools)
    
    # Check that the agent is available
    agents = registry.get_agents()
    assert ExampleAgent in agents

def test_greeting_extensions():
    """Test that the greeting extensions work correctly."""
    english_greeter = EnglishGreeter()
    spanish_greeter = SpanishGreeter()
    
    # Test English greeter
    assert asyncio.run(english_greeter.greet("Alice")) == "Hello, Alice!"
    
    # Test Spanish greeter
    assert asyncio.run(spanish_greeter.greet("Bob")) == "¡Hola, Bob!"

def test_plugin_auto_discovery():
    """Test that the plugin can be auto-discovered."""
    # This test verifies that the __plugin__ attribute is set correctly
    from agentspring.plugins.example import __plugin__
    assert isinstance(__plugin__, ExamplePlugin)

@pytest.mark.asyncio
async def test_tool_parameter_validation():
    """Test that tool parameters are properly validated."""
    tool = GreeterTool()
    context = Context(workflow_id="test", execution_id="1")
    
    # Test missing required parameter
    with pytest.raises(KeyError, match="The 'name' parameter is required"):
        await tool.execute({}, context)
    
    # Test with None as name (should raise KeyError)
    with pytest.raises(KeyError, match="The 'name' parameter is required"):
        await tool.execute({"name": None}, context)
    
    # Test with empty string as name (should work)
    result = await tool.execute({"name": ""}, context)
    assert result == "Hello, !"
    
    # Test with invalid parameter type (should still work as we convert to string)
    result = await tool.execute({"name": 123}, context)
    assert result == "Hello, 123!"
    
    # Test invalid language (should default to English)
    result = await tool.execute({"name": "Alice", "language": "fr"}, context)
    assert result == "Hello, Alice!"  # Should default to English
