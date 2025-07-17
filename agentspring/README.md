# AgentSpring Framework

This directory contains the core framework code for AgentSpring.

## Tool Registry System
AgentSpring provides a modular tool registry with production-ready tools for communication, data, web, business, media, and system operations.

### Example Usage
```python
from agentspring.tools import tool_registry
result = tool_registry.execute_tool("read_file", file_path="README.md")
print(result.result["content"])
```

See the main README for more details and available tools.

## Key Modules
- `api.py` - FastAPI integration and agent app base
- `llm.py` - LLM helpers and prompt templates
- `tasks.py` - Async task helpers and batch processing
- `models.py` - Standard Pydantic models
- `multi_tenancy.py` - Multi-tenant support
- `api_versioning.py` - API versioning utilities
- `celery_app.py` - Celery configuration

## Usage
Import AgentSpring modules in your app:

```python
from agentspring.api import FastAPIAgent
from agentspring.llm import classify
from agentspring.tasks import agentspring_task
```

See the main README for more details. 