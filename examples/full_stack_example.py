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

# 1. Direct pipeline: always read CSV, summarize, write summary (no LLM/plan)
from custom_tools import read_csv, summarize_issues, write_summary

print("\n=== Sample CSV Contents ===")
with open("complaints.csv") as f:
    print(f.read())

print("\n=== Step-by-Step Execution ===")
# Step 1: Read CSV
csv_result = read_csv("complaints.csv")
print("Step 1: read_csv ->", csv_result)
# Step 2: LLM summarize issues
all_issues = [row["issue"] for row in csv_result["data"] if "issue" in row]
from custom_tools import llm_summarize_issues
summary_result = llm_summarize_issues(all_issues)
print("Step 2: llm_summarize_issues ->", summary_result)
# Step 3: Write summary
write_result = write_summary(summary_result["summary"], "summary.txt")
print("Step 3: write_summary ->", write_result)

print("\n=== Final Results ===")
print({
    "read_csv": csv_result,
    "llm_summarize_issues": summary_result,
    "write_summary": write_result
})
exit(0)

print("\n=== Sample CSV Contents ===")
with open("complaints.csv") as f:
    print(f.read())

print("\n=== Tool Plan ===")
import pprint
pprint.pprint(plan)

# 2. Execute the Plan (Sync)
results = {}
print("\n=== Step-by-Step Execution ===")
# plan is now a ToolChain object; use plan.steps for execution
# Enhanced: resolve {var} references in parameters using previous results
context = {}
for idx, step in enumerate(plan.steps, 1):
    print(f"\nStep {idx}: {step.tool_name} with args: {step.parameters}")
    resolved_args = {}
    for k, v in step.parameters.items():
        if isinstance(v, str) and v.startswith("{") and v.endswith("}"):
            var_name = v.strip("{}")
            # For known keys, extract the right value from previous tool result dicts
            if var_name in results:
                prev = results[var_name]
                # If previous result is a dict with a key matching the param, use it
                if isinstance(prev, dict):
                    # Special-case: if param expects rows or summary, extract those
                    if k == "rows" and "data" in prev:
                        # Special-case: pass only the data list
                        print(f"[DEBUG] Passing data to {step.tool_name}: {prev['data']}")
                        resolved_args[k] = prev["data"]
                    elif k == "summary" and "summary" in prev:
                        resolved_args[k] = prev["summary"]
                    else:
                        # fallback to the whole dict
                        resolved_args[k] = prev
                else:
                    resolved_args[k] = prev
            elif var_name in context:
                resolved_args[k] = context[var_name]
            else:
                resolved_args[k] = None
        else:
            resolved_args[k] = v
    print(f"[DEBUG] Calling {step.tool_name} with: {resolved_args}")
    result = tool_registry.execute_tool(step.tool_name, **resolved_args)
    print(f"Result: {result.result}")
    results[step.tool_name] = result.result
    # Also update context for chained variable passing
    if isinstance(result.result, dict):
        context.update(result.result)

print("\n=== Final Results ===")
pprint.pprint(results)
if (
    "write_summary" in results
    and isinstance(results["write_summary"], dict)
    and "file" in results["write_summary"]
):
    print(f"\n=== Summary written to: {results['write_summary']['file']} ===")
    with open(results['write_summary']['file'], "r") as f:
        print(f.read())
else:
    print("[ERROR] write_summary tool did not produce a file. Result was:", results.get("write_summary"))

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
