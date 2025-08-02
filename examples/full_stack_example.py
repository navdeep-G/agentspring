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

tool_registry.register(custom_tools.read_csv)
tool_registry.register(custom_tools.llm_summarize_issues)
tool_registry.register(custom_tools.write_summary)

# 1. Agentic Orchestration: Parse prompt into tool plan
orchestrator = create_orchestrator()
prompt = (
  "Can you look at the complaints in the CSV file at 'examples/complaints.csv', "
  "summarize the key issues, and save the summary to a file?"
)

results = orchestrator.execute_prompt(prompt)
# print("\n=== Sample CSV Contents ===")
# with open("complaints.csv") as f:
#     print(f.read())

# print("\n=== Tool Plan ===")
# import pprint
# pprint.pprint(plan)

print(results)

# 2. Execute the Plan (Sync)
# results = {}
# print("\n=== Step-by-Step Execution ===")
# for idx, step in enumerate(plan, 1):
#     print(f"\nStep {idx}: {step['tool']} with args: {step['args']}")
#     args = {
#         k: (results[v[8:]] if isinstance(v, str) and v.startswith("<result_of_") else v)
#         for k, v in step["args"].items()
#     }
#     result = tool_registry.execute_tool(step["tool"], **args)
#     print(f"Result: {result.result}")
#     results[step["tool"]] = result.result

# print("\n=== Final Results ===")
# pprint.pprint(results)
# if "write_summary" in results:
#     print(f"\n=== Summary written to: {results['write_summary'].get('file')} ===")
#     with open(results['write_summary'].get('file'), "r") as f:
#         print(f.read())

# 3. (Optional) Async/batch usage
# from agentspring.tasks import batch_process
# from celery import Celery
# celery_app = Celery(broker="redis://localhost:6379/0")
# task_ids = batch_process(celery_app, tool_registry._tools["read_csv"], ["complaints1.csv", "complaints2.csv"], wait=False)
# print("Batch task IDs:", task_ids)

# 4. (Optional) FastAPI API Example: Error Handling, Logging, Auth, Monitoring
# ----------------------------------------------------------
# from fastapi import FastAPI, Request
# from agentspring.api import FastAPIAgent, require_api_key, log_api_error
# app = FastAPIAgent()
#
# @app.post("/analyze_complaints")
# @require_api_key(role="user")  # Enforces API key and role-based access
# @log_api_error                  # Logs exceptions and returns structured error responses
# async def analyze_complaints(request: Request):
#     data = await request.json()
#     plan = orchestrator.parse_prompt(
#         f"Hey agent, analyze complaints in {data['file_path']} and summarize top issues."
#     )
#     results = {}
#     for step in plan:
#         args = {k: (results[v[8:]] if isinstance(v, str) and v.startswith("<result_of_") else v)
#                 for k, v in step["args"].items()}
#         result = tool_registry.execute_tool(step["tool"], **args)
#         results[step["tool"]] = result.result
#     return {"result": results}
#
# # Monitoring endpoints available out of the box:
# #   GET /health      -> Health check
# #   GET /readiness   -> Readiness probe
# #   GET /liveness    -> Liveness probe
# # All logs are structured JSON and include user/request context.
#     file_path = data["file_path"]
#     plan = orchestrator.parse_prompt(
#         f"Read '{file_path}', summarize issues, and send to Slack."
#     )
#     results = {}
#     for step in plan:
#         args = {k: (results[v[8:]] if isinstance(v, str) and v.startswith("<result_of_") else v)
#                 for k, v in step["args"].items()}
#         result = tool_registry.execute_tool(step["tool"], **args)
#         results[step["tool"]] = result.result
#     return {"result": results}
