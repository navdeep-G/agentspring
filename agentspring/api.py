# agentspring/api.py
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Dict, Any, Optional, List
import json
import uuid

# Create FastAPI app
app = FastAPI(
    title="AgentSpring API",
    description="API for AgentSpring framework",
    version="0.1.0"
)

# Initialize the router
router = APIRouter()

# API key header
API_KEY_HEADER = "X-API-Key"

# Import the Agent class
from .agent import Agent

# Add the auth import
from .auth import get_current_user

# Import models
from .models import ToolRegistration, ProviderRegistration

@router.get("/health", response_model=Dict[str, str])
async def health():
    """Health check endpoint."""
    return {"status": "ok"}

@router.get("/tools", response_model=List[Dict[str, Any]])
async def list_tools():
    """List all available tools."""
    # This is a placeholder - implement actual tool listing
    return []

@router.post("/run")
async def run_agent(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Run an agent with the given input."""
    # This is a placeholder - implement actual agent execution
    return {"result": "Agent execution result"}

# Admin router
admin_router = APIRouter(prefix="/admin", tags=["admin"])

@admin_router.post("/tools/register")
async def register_tool(
    tool_reg: ToolRegistration, 
    current_user: dict = Depends(get_current_user)
):
    """Register a new tool."""
    # This is a placeholder - implement actual tool registration
    return {"status": "Tool registered successfully"}

@admin_router.post("/providers/register")
async def register_provider(
    provider_reg: ProviderRegistration,
    current_user: dict = Depends(get_current_user)
):
    """Register a new provider."""
    # This is a placeholder - implement actual provider registration
    return {"status": "Provider registered successfully"}

# Include routers
app.include_router(router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")

def get_app():
    """
    Get the FastAPI application.
    This is used by ASGI servers like uvicorn.
    """
    return app