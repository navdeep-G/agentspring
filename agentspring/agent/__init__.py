"""
Agent module for AgentSpring.

This module provides the base Agent class and related components for creating
intelligent agents that can use tools, maintain state, and participate in workflows.
"""
from typing import Dict, List, Any, Optional, Type, TypeVar, Callable
from pydantic import BaseModel, Field
from ..tools import ToolRegistry
from ..goals import Goal

T = TypeVar('T', bound='Agent')

class AgentState(BaseModel):
    """Represents the state of an agent."""
    memory: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    current_goals: List[Goal] = Field(default_factory=list)
    completed_goals: List[Goal] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

class Agent:
    """
    Base class for all agents in AgentSpring.
    
    Agents are autonomous entities that can use tools, maintain state,
    and work towards achieving goals.
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        tools: Optional[ToolRegistry] = None,
        state: Optional[AgentState] = None,
        **kwargs
    ):
        """
        Initialize a new agent.
        
        Args:
            name: Unique name for the agent
            description: Description of the agent's purpose
            tools: Tool registry containing tools the agent can use
            state: Initial agent state (if any)
            **kwargs: Additional agent-specific configuration
        """
        self.name = name
        self.description = description
        self.tools = tools or ToolRegistry()
        self.state = state or AgentState()
        self.config = kwargs
        
        # Register agent's methods as tools if they're decorated
        self._register_agent_methods()
    
    def _register_agent_methods(self) -> None:
        """Register methods decorated with @agent_tool."""
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, '_is_agent_tool') and attr._is_agent_tool:
                self.tools.register(attr_name)(attr)
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return a response.
        
        This is the main entry point for the agent. Subclasses should override
        this method to implement their specific behavior.
        
        Args:
            input_data: Input data to process
            
        Returns:
            Dictionary containing the agent's response
        """
        raise NotImplementedError("Subclasses must implement process()")
    
    async def execute_tool(
        self,
        tool_name: str,
        **kwargs
    ) -> Any:
        """
        Execute a tool by name with the given arguments.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Arguments to pass to the tool
            
        Returns:
            Result of the tool execution
            
        Raises:
            ValueError: If the tool is not found
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
            
        tool = self.tools[tool_name]
        return await tool.execute(**kwargs)
    
    def add_goal(self, goal: Goal) -> None:
        """Add a new goal for the agent to work on."""
        self.state.current_goals.append(goal)
    
    def complete_goal(self, goal_id: str) -> None:
        """Mark a goal as completed."""
        for i, goal in enumerate(self.state.current_goals):
            if goal.id == goal_id:
                goal.status = GoalStatus.COMPLETED
                self.state.completed_goals.append(goal)
                self.state.current_goals.pop(i)
                return
        raise ValueError(f"Goal with ID '{goal_id}' not found")
    
    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """Get a goal by ID."""
        for goal in self.state.current_goals + self.state.completed_goals:
            if goal.id == goal_id:
                return goal
        return None
    
    def update_memory(self, key: str, value: Any) -> None:
        """Update the agent's memory."""
        self.state.memory[key] = value
    
    def get_memory(self, key: str, default: Any = None) -> Any:
        """Get a value from the agent's memory."""
        return self.state.memory.get(key, default)
    
    def clear_memory(self) -> None:
        """Clear the agent's memory."""
        self.state.memory = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the agent to a dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "state": self.state.dict(),
            "config": self.config,
            "tools": [tool.name for tool in self.tools.tools.values()]
        }
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create an agent from a dictionary."""
        agent = cls(
            name=data["name"],
            description=data.get("description", ""),
            state=AgentState(**data.get("state", {})),
            **data.get("config", {})
        )
        return agent

def agent_tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    args_schema: Optional[Dict[str, Any]] = None
) -> Callable:
    """
    Decorator to mark a method as an agent tool.
    
    Args:
        name: Name of the tool (defaults to method name)
        description: Description of what the tool does
        args_schema: Schema for the tool's arguments
    """
    def decorator(method):
        method._is_agent_tool = True
        method._tool_name = name or method.__name__
        method._tool_description = description or method.__doc__ or ""
        method._args_schema = args_schema or {}
        return method
    return decorator
