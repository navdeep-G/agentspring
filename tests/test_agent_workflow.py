"""
Tests for the Agent and Workflow classes.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from agentspring.agent import Agent
from agentspring.workflow import Workflow, NodeStatus
from agentspring.tools import ToolRegistry
from typing import Dict, Any
from agentspring.goals import Goal, GoalStatus
from agentspring.tools import tool

# Test Agent Implementation
class TestAgent(Agent):
    """A test agent implementation."""
    
    def __init__(self, name: str = "TestAgent"):
        super().__init__(name=name, description="A test agent")
        self.process_mock = AsyncMock()
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return a response."""
        return await self.process_mock(input_data)

# Test Tools
@tool(
    name="mock_tool",
    description="A mock tool for testing that takes a string and an integer and returns a string"
)
async def mock_tool(param1: str, param2: int) -> Dict[str, Any]:
    """
    Mock tool implementation.
    
    Args:
        param1: First parameter (string)
        param2: Second parameter (integer)
        
    Returns:
        Dictionary containing the result
    """
    return {"result": f"{param1}_{param2}"}

@pytest.fixture
def test_agent():
    """Create a test agent."""
    return TestAgent()

@pytest.fixture
def test_tools():
    """Register test tools."""
    tool_registry = ToolRegistry()
    tool_registry.register(mock_tool)
    return tool_registry

@pytest.mark.asyncio
async def test_agent_execution(test_agent):
    """Test basic agent execution."""
    test_input = {"test": "data"}
    expected_output = {"response": "test response"}
    
    # Setup mock to return expected output
    test_agent.process_mock.return_value = expected_output
    
    # Execute agent
    result = await test_agent.process(test_input)
    
    # Verify results
    assert result == expected_output
    test_agent.process_mock.assert_awaited_once_with(test_input)
