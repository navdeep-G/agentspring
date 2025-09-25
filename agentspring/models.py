# agentspring/models.py
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Type, Callable

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Optional[Callable] = None  # Not part of the API, for internal use

class ToolRegistration(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    handler_url: Optional[str] = None  # For remote tools
    handler_code: Optional[str] = None  # For code-defined tools

class ProviderRegistration(BaseModel):
    name: str
    provider_type: str
    config: Dict[str, Any]
    is_default: bool = False