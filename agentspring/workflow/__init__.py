"""
Workflow module for AgentSpring.

This module provides the Workflow class for defining and executing
sequences of agent tasks with dependencies.
"""
from typing import Dict, List, Any, Optional, Union, Callable, Awaitable, TypeVar, Generic, Type
from enum import Enum
from pydantic import BaseModel, Field
from ..agent import Agent
from ..tools import ToolRegistry
from ..goals import Goal
import time

T = TypeVar('T')

class NodeType(str, Enum):
    """Types of workflow nodes."""
    AGENT = "agent"
    TOOL = "tool"
    CONDITION = "condition"
    PARALLEL = "parallel"
    SEQUENCE = "sequence"

class NodeStatus(str, Enum):
    """Status of a workflow node."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class WorkflowNode(BaseModel):
    """Represents a node in a workflow."""
    node_id: str
    node_type: NodeType
    config: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    status: NodeStatus = NodeStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    
    class Config:
        arbitrary_types_allowed = True

class WorkflowContext(BaseModel):
    """Context shared across a workflow execution."""
    variables: Dict[str, Any] = Field(default_factory=dict)
    results: Dict[str, Any] = Field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a variable from the context."""
        return self.variables.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a variable in the context."""
        self.variables[key] = value
    
    def update(self, data: Dict[str, Any]) -> None:
        """Update multiple variables in the context."""
        self.variables.update(data)

class Workflow:
    """
    A workflow defines a sequence of nodes (agents, tools, etc.) to be executed.
    """
    
    def __init__(
        self,
        workflow_id: str,
        name: str = "",
        description: str = "",
        agents: Optional[Dict[str, Agent]] = None,
        tools: Optional[ToolRegistry] = None
    ):
        """
        Initialize a new workflow.
        
        Args:
            workflow_id: Unique identifier for the workflow
            name: Human-readable name of the workflow
            description: Description of the workflow's purpose
            agents: Dictionary of agents available to the workflow
            tools: Tool registry with tools available to the workflow
        """
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.agents = agents or {}
        self.tools = tools or ToolRegistry()
        self.nodes: Dict[str, WorkflowNode] = {}
        self.context = WorkflowContext()
        self._execution_order: List[str] = []
    
    def add_agent(self, agent_id: str, agent: Agent) -> None:
        """Add an agent to the workflow."""
        self.agents[agent_id] = agent
    
    def add_node(
        self,
        node_id: str,
        node_type: Union[NodeType, str],
        config: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None
    ) -> WorkflowNode:
        """
        Add a node to the workflow.
        
        Args:
            node_id: Unique identifier for the node
            node_type: Type of the node (from NodeType enum)
            config: Configuration for the node
            dependencies: List of node IDs this node depends on
            
        Returns:
            The created WorkflowNode
        """
        if isinstance(node_type, str):
            node_type = NodeType(node_type.lower())
            
        node = WorkflowNode(
            node_id=node_id,
            node_type=node_type,
            config=config or {},
            dependencies=dependencies or []
        )
        self.nodes[node_id] = node
        return node
    
    def add_agent_node(
        self,
        node_id: str,
        agent_id: str,
        goal: Union[Goal, str],
        dependencies: Optional[List[str]] = None,
        **kwargs
    ) -> WorkflowNode:
        """
        Add an agent node to the workflow.
        
        Args:
            node_id: Unique identifier for the node
            agent_id: ID of the agent to execute
            goal: Goal for the agent to work on (or goal description)
            dependencies: List of node IDs this node depends on
            **kwargs: Additional configuration for the agent node
            
        Returns:
            The created WorkflowNode
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent '{agent_id}' not found in workflow")
            
        config = {
            "agent_id": agent_id,
            "goal": goal.dict() if isinstance(goal, Goal) else {"description": str(goal)},
            **kwargs
        }
        
        return self.add_node(
            node_id=node_id,
            node_type=NodeType.AGENT,
            config=config,
            dependencies=dependencies
        )
    
    def add_tool_node(
        self,
        node_id: str,
        tool_name: str,
        parameters: Dict[str, Any],
        dependencies: Optional[List[str]] = None
    ) -> WorkflowNode:
        """
        Add a tool node to the workflow.
        
        Args:
            node_id: Unique identifier for the node
            tool_name: Name of the tool to execute
            parameters: Parameters to pass to the tool
            dependencies: List of node IDs this node depends on
            
        Returns:
            The created WorkflowNode
        """
        if not self.tools.get_tool(tool_name):
            raise ValueError(f"Tool '{tool_name}' not found in workflow")
            
        config = {
            "tool_name": tool_name,
            "parameters": parameters
        }
        
        return self.add_node(
            node_id=node_id,
            node_type=NodeType.TOOL,
            config=config,
            dependencies=dependencies
        )
    
    async def execute(self, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the workflow.
        
        Args:
            initial_context: Initial context variables for the workflow
            
        Returns:
            Dictionary containing the workflow results
        """
        # Reset workflow state
        self.context = WorkflowContext()
        if initial_context:
            self.context.update(initial_context)
        
        # Determine execution order (topological sort)
        self._determine_execution_order()
        
        # Execute nodes in order
        for node_id in self._execution_order:
            node = self.nodes[node_id]
            await self._execute_node(node)
        
        # Return the final context
        return {
            "status": "completed",
            "context": self.context.variables,
            "results": self.context.results
        }
    
    def _determine_execution_order(self) -> None:
        """Determine the execution order of nodes using topological sort."""
        # Simple implementation - assumes no cycles
        # For production use, implement a proper topological sort
        visited = set()
        temp = set()
        order = []
        
        def visit(node_id):
            if node_id in temp:
                raise ValueError(f"Cycle detected in workflow at node {node_id}")
            if node_id not in visited:
                temp.add(node_id)
                for dep in self.nodes[node_id].dependencies:
                    visit(dep)
                temp.remove(node_id)
                visited.add(node_id)
                order.append(node_id)
        
        for node_id in self.nodes:
            visit(node_id)
        
        self._execution_order = order
    
    async def _execute_node(self, node: WorkflowNode) -> None:
        """Execute a single workflow node."""
        try:
            node.status = NodeStatus.RUNNING
            
            # Check if dependencies are met
            for dep_id in node.dependencies:
                dep = self.nodes.get(dep_id)
                if not dep or dep.status != NodeStatus.COMPLETED:
                    node.status = NodeStatus.SKIPPED
                    return
            
            # Execute based on node type
            if node.node_type == NodeType.AGENT:
                result = await self._execute_agent_node(node)
            elif node.node_type == NodeType.TOOL:
                result = await self._execute_tool_node(node)
            elif node.node_type == NodeType.CONDITION:
                result = await self._execute_condition_node(node)
            elif node.node_type == NodeType.PARALLEL:
                result = await self._execute_parallel_node(node)
            elif node.node_type == NodeType.SEQUENCE:
                result = await self._execute_sequence_node(node)
            else:
                raise ValueError(f"Unknown node type: {node.node_type}")
            
            # Store the result
            node.result = result
            node.status = NodeStatus.COMPLETED
            self.context.results[node.node_id] = result
            
        except Exception as e:
            node.status = NodeStatus.FAILED
            node.error = str(e)
            raise
    
    async def _execute_agent_node(self, node: WorkflowNode) -> Any:
        """Execute an agent node."""
        config = node.config
        agent_id = config["agent_id"]
        agent = self.agents.get(agent_id)
        
        if not agent:
            raise ValueError(f"Agent '{agent_id}' not found")
        
        # Update agent's context with workflow context
        agent.state.context.update(self.context.variables)
        
        # Execute the agent
        result = await agent.process(config["goal"])
        
        # Update workflow context with agent's results
        if isinstance(result, dict):
            self.context.update(result)
        
        return result
    
    async def _execute_tool_node(self, node: WorkflowNode) -> Dict[str, Any]:
        """Execute a tool node."""
        config = node.config
        tool_name = config["tool_name"]
        parameters = config["parameters"]
        
        # Check if tool exists in the registry
        tool_func = self.tools.get_tool(tool_name)
        if not tool_func:
            raise ValueError(f"Tool '{tool_name}' not found in registry")
        
        # Execute the tool
        start_time = time.time()
        try:
            result = await tool_func(**parameters)
            node.status = NodeStatus.COMPLETED
            node.result = {"success": True, "result": result}
            return node.result
        except Exception as e:
            node.status = NodeStatus.FAILED
            node.error = str(e)
            node.result = {"success": False, "error": str(e)}
            return node.result
        finally:
            node.execution_time = time.time() - start_time
    
    async def _execute_condition_node(self, node: WorkflowNode) -> Any:
        """Execute a condition node."""
        # TODO: Implement condition node execution
        raise NotImplementedError("Condition nodes not yet implemented")
    
    async def _execute_parallel_node(self, node: WorkflowNode) -> Any:
        """Execute child nodes in parallel."""
        # TODO: Implement parallel node execution
        raise NotImplementedError("Parallel nodes not yet implemented")
    
    async def _execute_sequence_node(self, node: WorkflowNode) -> Any:
        """Execute child nodes in sequence."""
        # TODO: Implement sequence node execution
        raise NotImplementedError("Sequence nodes not yet implemented")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the workflow to a dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "nodes": {k: v.dict() for k, v in self.nodes.items()},
            "context": self.context.dict(),
            "agents": list(self.agents.keys())
        }
    
    @classmethod
    def from_dict(
        cls: Type['Workflow'],
        data: Dict[str, Any],
        agents: Optional[Dict[str, Agent]] = None,
        tools: Optional[ToolRegistry] = None
    ) -> 'Workflow':
        """
        Create a workflow from a dictionary.
        
        Args:
            data: Dictionary containing workflow data
            agents: Dictionary of agents to use in the workflow
            tools: Tool registry to use in the workflow
            
        Returns:
            The created Workflow instance
        """
        workflow = cls(
            workflow_id=data["workflow_id"],
            name=data.get("name", ""),
            description=data.get("description", ""),
            agents=agents or {},
            tools=tools or ToolRegistry()
        )
        
        # Add nodes
        for node_id, node_data in data.get("nodes", {}).items():
            workflow.add_node(
                node_id=node_id,
                node_type=node_data["node_type"],
                config=node_data.get("config", {}),
                dependencies=node_data.get("dependencies", [])
            )
        
        # Set context
        if "context" in data:
            workflow.context = WorkflowContext(**data["context"])
        
        return workflow
