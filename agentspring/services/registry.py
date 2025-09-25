from typing import Dict, Type, Optional, List
from ..core.agent import BaseAgent

class AgentRegistry:
    """
    Registry for managing agent instances.
    This is a singleton class that holds all registered agents.
    """
    _instance = None
    
    def __init__(self):
        if AgentRegistry._instance is not None:
            raise Exception("This class is a singleton!")
        self._agents: Dict[str, BaseAgent] = {}
    
    @classmethod
    def get_instance(cls) -> 'AgentRegistry':
        """Get the singleton instance of the registry."""
        if cls._instance is None:
            cls._instance = AgentRegistry()
        return cls._instance
    
    def register(self, name: str, agent: BaseAgent) -> None:
        """Register an agent instance with a name."""
        if name in self._agents:
            raise ValueError(f"Agent with name '{name}' already registered")
        self._agents[name] = agent
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name."""
        return self._agents.get(name)
    
    def list_agents(self) -> List[str]:
        """List all registered agent names."""
        return list(self._agents.keys())
    
    def clear(self) -> None:
        """Clear all registered agents (for testing)."""
        self._agents.clear()


def register_agent(name: str):
    """
    Decorator to register an agent class with the registry.
    
    Example:
        @register_agent("my_agent")
        class MyAgent(BaseAgent):
            ...
    """
    def decorator(agent_class: Type[BaseAgent]):
        registry = AgentRegistry.get_instance()
        registry.register(name, agent_class())
        return agent_class
    return decorator
