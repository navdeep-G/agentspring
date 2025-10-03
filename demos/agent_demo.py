import asyncio
from typing import Dict, Any, Optional
from pydantic import BaseModel
from agentspring.core.agent import BaseAgent
from agentspring.core.base import Context
from agentspring.core.extensions import Tool
from enum import Enum

class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"

class Message(BaseModel):
    role: MessageRole
    content: str

class AgentConfig(BaseModel):
    name: str = "default_agent"
    description: str = "A generic agent"

class GreetingAgent(BaseAgent[AgentConfig]):
    """A simple agent that responds to greetings."""
    
    @classmethod
    def get_default_config(cls) -> AgentConfig:
        return AgentConfig(
            name="greeting_agent",
            description="Responds to greetings"
        )
    
    async def execute(self, messages, context=None):
        last_message = messages[-1].content.lower()
        
        if any(greeting in last_message for greeting in ["hello", "hi", "hey"]):
            response = "Hello there! How can I assist you today?"
        elif "how are you" in last_message:
            response = "I'm doing well, thank you for asking! How can I help you?"
        elif "bye" in last_message or "goodbye" in last_message:
            response = "Goodbye! Have a great day!"
        elif "thank" in last_message:
            response = "You're welcome! Is there anything else I can help you with?"
        else:
            response = "I'm here to help! What would you like to know?"
            
        return Message(role=MessageRole.ASSISTANT, content=response)

async def main():
    print("🤖 AgentSpring CLI Demo")
    print("Type 'exit' or 'quit' to end the session\n")
    
    agent = GreetingAgent()
    print(f"Agent: {agent.get_default_config().description}\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                print("\n👋 Goodbye!")
                break
                
            if not user_input:
                continue
                
            # Create a proper Message object
            user_message = Message(role=MessageRole.USER, content=user_input)
            response = await agent.execute([user_message])
            
            print(f"\nAgent: {response.content}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n⚠️  Error: {str(e)}\n")

if __name__ == "__main__":
    asyncio.run(main())