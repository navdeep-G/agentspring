# agentspring/api.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Dict, Any, Optional, List
import json
import uuid

# Import the Agent class
from .agent import Agent

# Initialize the router
router = APIRouter()

# Move the API key header to the top level
API_KEY_HEADER = "X-API-Key"

# Add the auth import
from .auth import get_current_user

# Move the models import to the top
from .models import ToolDefinition, ToolRegistration, ProviderRegistration
from .llm.registry import registry

# Update the health check to use the router
@router.get("/health")
async def health():
    return {"ok": True}

# Update the tools endpoint to use the router
@router.get("/v1/tools")
async def list_tools():
    """List all available tools."""
    tools = registry.list_tools()
    return [{
        "name": tool.name,
        "description": tool.description,
        "parameters": tool.parameters
    } for tool in tools]

# Update the run agent endpoint
@router.post("/v1/agents/run")
async def run_agent(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Get provider from request or use default
        provider_name = request.get("provider")
        provider = registry.get_provider(provider_name)
        
        # Get tools from registry
        tools = registry.list_tools()
        
        # Create and run agent
        agent = Agent(provider=provider, tools=tools)
        result = await agent.run(request["prompt"])
        
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Add the admin router
admin_router = APIRouter(prefix="/admin", tags=["admin"])

@admin_router.post("/tools/register")
async def register_tool(
    tool_reg: ToolRegistration, 
    current_user: dict = Depends(get_current_user)
):
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # For security, we'll only allow predefined tool handlers
    if tool_reg.handler_code:
        raise HTTPException(status_code=400, detail="Dynamic code execution not allowed")
    
    tool_def = ToolDefinition(
        name=tool_reg.name,
        description=tool_reg.description,
        parameters=tool_reg.parameters,
        handler=None  # Only predefined handlers allowed for now
    )
    
    registry.register_tool(tool_def)
    return {"status": "success", "tool": tool_def.name}

@admin_router.post("/providers/register")
async def register_provider(
    provider_reg: ProviderRegistration,
    current_user: dict = Depends(get_current_user)
):
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Only allow predefined provider types for security
    if provider_reg.provider_type not in ["mock", "openai", "azure_openai"]:
        raise HTTPException(status_code=400, detail="Unsupported provider type")
    
    registry.register_provider(
        provider_reg.name,
        get_provider_class(provider_reg.provider_type),
        is_default=provider_reg.is_default
    )
    
    return {"status": "success", "provider": provider_reg.name}

# Include the admin router with a prefix
router.include_router(admin_router, prefix="/v1")

# Helper function to get provider class by type
def get_provider_class(provider_type: str):
    if provider_type == "mock":
        from .llm.providers.mock import MockProvider
        return MockProvider
    elif provider_type == "openai":
        from .llm.providers.openai import OpenAIProvider
        return OpenAIProvider
    else:
        raise ValueError(f"Unsupported provider type: {provider_type}")