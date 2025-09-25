from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from .core.agent import AgentMessage, AgentResult, BaseAgent
from .llm.base import LLMProvider

class AgentConfig(BaseModel):
    """Configuration for the Agent."""
    system_prompt: str = "You are a helpful AI assistant."
    temperature: float = 0.7
    max_tokens: int = 1000

class Agent(BaseAgent[AgentConfig]):
    """Main Agent class that uses an LLM provider and tools."""
    
    def __init__(self, provider: LLMProvider, tools: Optional[List[Dict]] = None):
        self.provider = provider
        self.tools = tools or []
        super().__init__()
    
    @classmethod
    def get_default_config(cls) -> AgentConfig:
        return AgentConfig()
    
    async def run(self, prompt: str) -> str:
        """Run the agent with the given prompt."""
        messages = [
            {"role": "system", "content": self.config.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # If we have tools, include them in the prompt
        if self.tools:
            messages[0]["content"] += "\n\nAvailable tools: " + ", ".join([t.name for t in self.tools])
        
        # Get response from the provider
        response = await self.provider.generate_async(
            prompt=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        
        return response
    
    async def execute(
        self, 
        messages: List[AgentMessage],
        **kwargs
    ) -> AgentResult:
        """Execute the agent with the given messages."""
        # Convert AgentMessage to the format expected by the provider
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Get response from the provider
        response = await self.provider.generate_async(
            prompt=formatted_messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            **kwargs
        )
        
        return AgentResult(content=response)
