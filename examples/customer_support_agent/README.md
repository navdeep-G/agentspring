# CustomerSupportAgent (Example App for AgentSpring)

This directory contains the CustomerSupportAgent, a production-ready customer support agent built as an example app for the AgentSpring framework.

## Features
- Intelligent complaint classification, prioritization, summarization, and routing
- Multi-tenancy, audit logging, and observability
- Minimal code: async, batch, and tenant endpoints are registered with a single import or function call

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
- The app is loaded by AgentSpring via the `AGENTSPRING_APP` environment var 