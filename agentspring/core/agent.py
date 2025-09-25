from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class AgentMessage(BaseModel):
    """Base message format for agent communication."""
    role: str  # user, system, assistant, tool
    content: str
    metadata: Dict[str, Any] = {}

class AgentResult(BaseModel):
    """Result returned from an agent's execution."""
    content: str
    metadata: Dict[str, Any] = {}

class BaseAgent(ABC, Generic[T]):
    """
    Base class for all agents.
    Users should subclass this and implement the `execute` method.
    """
    
    def __init__(self, config: Optional[T] = None):
        self.config = config or self.get_default_config()
    
    @classmethod
    @abstractmethod
    def get_default_config(cls) -> T:
        """Return default configuration for this agent."""
        pass
    
    @abstractmethod
    async def execute(
        self, 
        messages: List[AgentMessage],
        **kwargs
    ) -> AgentResult:
        """
        Execute the agent with the given messages and return the result.
        
        Args:
            messages: List of messages in the conversation
            **kwargs: Additional arguments specific to the agent implementation
            
        Returns:
            AgentResult containing the agent's response
        """
        pass
    
    async def __call__(
        self, 
        messages: List[AgentMessage],
        **kwargs
    ) -> AgentResult:
        """Allow the agent to be called directly."""
        return await self.execute(messages, **kwargs)
