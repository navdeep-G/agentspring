# Starter Agent App for AgentFlow

This directory provides a minimal template for building your own app with the AgentFlow framework.

## How to Use
1. Copy this directory and rename it (e.g., `my_custom_agent/`).
2. Implement your endpoints, tools, and business logic in `endpoints.py` (must expose a FastAPI `app`).
3. (Optional) Add templates, static files, or custom admin panels.
4. Set the environment variable:
   ```bash
   export AGENTFLOW_APP=examples.starter_agent.endpoints
   python main.py
   ```

## Minimal Workflow
- Just write your business logic—AgentFlow handles async, batch, tenant, health, and metrics with a single import or function call.
- For more advanced features, see:
  - `examples/simple_agent/` for a concise, production-ready example
  - `examples/customer_support_agent/` for a full-featured, advanced example 