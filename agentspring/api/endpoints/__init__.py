from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from ...core.agent import AgentMessage, AgentResult
from ...db.session import get_db
from ...services.registry import AgentRegistry

router = APIRouter()

@router.post("/agents/execute", response_model=AgentResult)
async def execute_agent(
    messages: List[AgentMessage],
    agent_name: str,
    db=Depends(get_db),
    agent_registry: AgentRegistry = Depends(AgentRegistry.get_instance)
) -> AgentResult:
    """
    Execute an agent with the given messages.
    
    Args:
        messages: List of messages in the conversation
        agent_name: Name of the agent to execute
        
    Returns:
        Agent's response
    """
    try:
        agent = agent_registry.get_agent(agent_name)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_name}' not found"
            )
            
        result = await agent(messages)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/agents")
async def list_agents(
    agent_registry: AgentRegistry = Depends(AgentRegistry.get_instance)
) -> List[str]:
    """List all registered agents."""
    return agent_registry.list_agents()
