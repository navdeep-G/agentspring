# CustomerSupportAgent (Example App for AgentSpring)

This directory contains the CustomerSupportAgent, a production-ready customer support agent built as an example app for the AgentSpring framework.

## Features Demonstrated
- Intelligent complaint classification, prioritization, summarization, and routing
- Multi-tenancy, audit logging, and observability
- Async, batch, and tenant endpoints with minimal code
- Tool registry usage (see `/tool-example` endpoint)
- Agentic orchestration (see `/orchestrate` endpoint)
- Custom and default Prometheus metrics
- API key security and RBAC
- Full-stack UI for end-to-end user interaction

## How to Use
- By default, AgentSpring loads this app.
- To run:
  ```bash
  ./start.sh
  # or
  python main.py
  ```
- To build your own app, see the `examples/starter_agent/` directory for a minimal starting point.

## Web UI

This app now uses an interactive UI powered by [H2O Wave](https://wave.h2o.ai/), implemented in `ui/wave_app.py`.

- To launch the UI, start the app normally (the Wave UI will be served automatically if using Docker Compose or the default app entrypoint).
- The UI is available at [http://localhost:10101](http://localhost:10101) by default (see your logs for confirmation).
- Features:
  - Submit support messages and see real-time analysis results
  - Run async analysis and watch task status updates live
  - Try prompt-driven agentic orchestration
  - View live Prometheus metrics

**Note:** The old static `index.html` is no longer used or needed.

## Endpoints
- `/analyze` (POST): Analyze a support message
- `/analyze_async` (POST): Async analysis (returns task ID)
- `/analyze_batch` (POST): Batch analysis
- `/tool-example` (POST): Demonstrates tool registry usage (e.g., read a file)
- `/orchestrate` (POST): Demonstrates agentic orchestration (multi-step workflow)
- `/tasks/{task_id}/status` (GET): Task status
- `/tasks/{task_id}/result` (GET): Task result
- `/metrics` (GET): Prometheus metrics
- `/ui/` (GET): Web UI

## How It Works
- All endpoints, tools, and business logic are in `endpoints.py`.
- Endpoints use AgentSpring's generic helpers:
  - LLM helpers: `classify`, `summarize`, `detect_priority`
  - Async and batch endpoints: `@agentspring_task`, `batch_process`, `standard_endpoints`
  - Tenant management: `tenant_router`
  - Tool registry for common operations
  - Orchestration for prompt-driven workflows

## Orchestration (Agentic Workflows)
You can use AgentSpring's orchestration system to automate multi-step support workflows:
```python
from agentspring.orchestration import create_orchestrator
orchestrator = create_orchestrator()
result = orchestrator.execute_prompt("Classify a support message, summarize it, and route to the right team.")
print(result)
```

See the main [README](../../README.md) for more details and advanced usage. 