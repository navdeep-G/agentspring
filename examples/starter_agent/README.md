# Starter Agent App for AgentSpring

This directory provides a minimal template for building your own app with the AgentSpring framework.

## How to Use
1. Copy this directory and rename it (e.g., `my_custom_agent/`).
2. Implement your endpoints, tools, and business logic in `endpoints.py` (must expose a FastAPI `app`).
3. (Optional) Add templates, static files, or custom admin panels.
4. Set the environment variable:
   ```bash
   export AGENTSPRING_APP=examples.starter_agent.endpoints
   python main.py
   ```

## Extending with Tools
AgentSpring provides a registry of production-ready tools for common tasks. Example:
```python
from agentspring.tools import tool_registry
result = tool_registry.execute_tool("read_file", file_path="README.md")
print(result.result["content"])
```

## Orchestration (Agentic Workflows)
You can also use AgentSpring's orchestration system to turn natural language prompts into multi-step workflows:
```python
from agentspring.orchestration import create_orchestrator
orchestrator = create_orchestrator()
result = orchestrator.execute_prompt("Read the README file and summarize its content.")
print(result)
```

See the main [README](../../README.md) for more details and advanced usage. 