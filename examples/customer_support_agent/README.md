# CustomerSupportAgent (Example App for AgentSpring)

This directory contains the CustomerSupportAgent, a production-ready customer support agent built as an example app for the AgentSpring framework.

## Features
- Intelligent complaint classification, prioritization, summarization, and routing
- Multi-tenancy, audit logging, and observability
- Minimal code: async, batch, and tenant endpoints are registered with a single import or function call
- Use of the tool registry for common tasks (file reading, email, etc)
- **Agentic Orchestration**: Can be extended to use prompt-driven, multi-step workflows

## Note
This example is for backend API use only. AgentSpring itself is a backend server framework and does not provide a UI by default.

## How to Use
- By default, AgentSpring loads this app.
- To run:
  ```bash
  ./start.sh
  # or
  python main.py
  ```
- To build your own app, see the `examples/starter_agent/` directory for a minimal starting point.

## How It Works
- All endpoints, tools, and business logic are in `endpoints.py`.
- Endpoints use AgentSpring's generic helpers:
  - One-liner LLM helpers: `classify`, `summarize`, `detect_priority`
  - Async and batch endpoints: `@agentspring_task`, `batch_process`, `standard_endpoints`
  - Tenant management: `tenant_router`
  - Tool registry for common operations

## Orchestration (Agentic Workflows)
You can use AgentSpring's orchestration system to automate multi-step support workflows:
```python
from agentspring.orchestration import create_orchestrator
orchestrator = create_orchestrator()
result = orchestrator.execute_prompt("Classify a support message, summarize it, and route to the right team.")
print(result)
```

See the main [README](../../README.md) for more details and advanced usage. 