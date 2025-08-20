"""
Tests for the Agent and Workflow classes.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from agentspring.agent import Agent
from agentspring.workflow import Workflow,NodeStatus
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
    """Create a test tool registry."""
    registry = ToolRegistry()
    registry.register("mock_tool")(mock_tool)
    return registry

@pytest.mark.asyncio
async def test_agent_execution(test_agent):
    """Test basic agent execution."""
    # Setup test data
    test_input = {"task": "test task"}
    expected_output = {"result": "success"}
    
    # Configure the mock
    test_agent.process_mock.return_value = expected_output
    
    # Execute the agent
    result = await test_agent.process(test_input)
    
    # Verify the results
    assert result == expected_output
    test_agent.process_mock.assert_awaited_once_with(test_input)

@pytest.mark.asyncio
async def test_agent_with_tools(test_agent, test_tools):
    """Test agent tool execution."""
    # Add tools to the agent
    test_agent.tools = test_tools
    
    # Execute a tool
    result = await test_agent.execute_tool("mock_tool", param1="test", param2=123)
    
    # Verify the result
    assert result == {"result": "test_123"}

@pytest.mark.asyncio
async def test_workflow_execution(test_agent, test_tools):
    """Test workflow execution with agents and tools."""
    # Create a workflow
    workflow = Workflow(
        workflow_id="test_workflow",
        name="Test Workflow",
        description="A test workflow",
        agents={"test_agent": test_agent},
        tools=test_tools
    )
    
    # Add nodes to the workflow
    goal = Goal(description="Test goal")
    
    # Add an agent node
    workflow.add_agent_node(
        node_id="agent_node_1",
        agent_id="test_agent",
        goal=goal
    )
    
    # Add a tool node that depends on the agent node
    workflow.add_tool_node(
        node_id="tool_node_1",
        tool_name="mock_tool",
        parameters={"param1": "test", "param2": 123},
        dependencies=["agent_node_1"]
    )
    
    # Configure the agent's process method
    test_agent.process_mock.return_value = {"agent_result": "success"}
    
    # Execute the workflow
    result = await workflow.execute()
    
    # Verify the results
    assert result["status"] == "completed"
    assert result["results"]["tool_node_1"] == {"result": "test_123"}
    
    # Verify the agent node was executed
    test_agent.process_mock.assert_awaited_once()
    
    # Verify node statuses
    assert workflow.nodes["agent_node_1"].status == NodeStatus.COMPLETED
    assert workflow.nodes["tool_node_1"].status == NodeStatus.COMPLETED

@pytest.mark.asyncio
async def test_workflow_with_goals(test_agent):
    """Test workflow with goal tracking."""
    # Create a workflow
    workflow = Workflow(
        workflow_id="goal_workflow",
        name="Goal Workflow",
        agents={"test_agent": test_agent}
    )
    
    # Create a goal with subgoals
    main_goal = Goal(description="Main goal")
    subgoal1 = Goal(description="Subgoal 1")
    subgoal2 = Goal(description="Subgoal 2")
    
    main_goal.add_subgoal(subgoal1)
    main_goal.add_subgoal(subgoal2)
    
    # Add agent nodes for each goal
    workflow.add_agent_node("main_goal", "test_agent", main_goal)
    workflow.add_agent_node("subgoal1", "test_agent", subgoal1, ["main_goal"])
    workflow.add_agent_node("subgoal2", "test_agent", subgoal2, ["subgoal1"])
    
    # Configure the agent's process method
    test_agent.process_mock.side_effect = [
        {"status": "completed"},
        {"status": "completed"},
        {"status": "completed"}
    ]
    
    # Execute the workflow
    result = await workflow.execute()
    
    # Verify the results
    assert result["status"] == "completed"
    assert test_agent.process_mock.await_count == 3
    
    # Verify goal statuses
    assert main_goal.status == GoalStatus.COMPLETED
    assert subgoal1.status == GoalStatus.COMPLETED
    assert subgoal2.status == GoalStatus.COMPLETED

@pytest.mark.asyncio
async def test_workflow_with_failure(test_agent):
    """Test workflow execution with a failing node."""
    # Create a workflow
    workflow = Workflow(
        workflow_id="failure_workflow",
        name="Failure Workflow",
        agents={"test_agent": test_agent}
    )
    
    # Add nodes that will fail
    workflow.add_agent_node("failing_node", "test_agent", "This will fail")
    workflow.add_agent_node("dependent_node", "test_agent", "Should be skipped", ["failing_node"])
    
    # Configure the agent to raise an exception
    test_agent.process_mock.side_effect = Exception("Simulated failure")
    
    # Execute the workflow and expect an exception
    with pytest.raises(Exception, match="Simulated failure"):
        await workflow.execute()
    
    # Verify node statuses
    assert workflow.nodes["failing_node"].status == NodeStatus.FAILED
    assert workflow.nodes["dependent_node"].status == NodeStatus.PENDING
