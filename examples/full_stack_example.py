"""
AgentSpring Full Stack Example: Batch Complaint Analysis and Summary

Capabilities Demonstrated:
- ✅ Agentic orchestration (natural language prompt → dynamic tool plan)
- ✅ Tool registry (plug-and-play, extensible tools)
- ✅ Step-by-step execution and result passing
- ✅ Data I/O (CSV, file writing)
- ✅ Extensibility (add your own tools, swap orchestrators)
- ✅ Async/batch task processing (Celery/Redis, see below)
- ✅ API error handling, logging, and authentication (see API example)
- ✅ Monitoring endpoints (health, readiness, liveness)

To run: Place a 'complaints.csv' file in the working directory with at least an 'issue' column (already provided).

---

Why is this agentic, not just function calling?
------------------------------------------------
- The agent interprets your **natural language goal** ("Hey agent, could you look through...?") and dynamically creates a plan of tool invocations.
- It manages dependencies between steps (output from one tool is passed as input to the next).
- You can change the prompt, add tools, or swap orchestrators, and the agent adapts—no need to rewrite the workflow manually.
- This enables autonomy, flexibility, and reasoning, unlike hardcoded function pipelines.

---

API, Error Handling, Logging, Monitoring
----------------------------------------
- AgentSpring's FastAPIAgent app provides:
    - **API key/RBAC authentication** (via @require_api_key)
    - **Structured error handling** (via @log_api_error)
    - **Structured JSON logging** (with context)
    - **Monitoring endpoints**: `/health`, `/readiness`, `/liveness`
- See the commented API example below for how to use these features in your own app.
"""

from agentspring.orchestration import create_orchestrator
from agentspring.tools import tool_registry

from examples import custom_tools

tool_registry.register(custom_tools.llm_summarize_issues)
tool_registry.register(custom_tools.write_summary)
tool_registry.register(custom_tools.read_csv)
tool_registry.register(custom_tools.print_csv_head)

# 1. Agentic Orchestration: Parse prompt into tool plan
orchestrator = create_orchestrator()

user_instruction = "Return the top 5 rows of the following file: examples/complaints.csv."

orchestrator.execute_prompt(user_instruction)