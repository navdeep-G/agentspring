# AgentSpring Framework

> **Note:** This README is for framework contributors and advanced users. For general usage, setup, and high-level documentation, see the [main README](../README.md).


> **Start here if new:**
> - [Main README](../README.md) — Overview, setup, and project structure
> - [Quickstart Guide](../QUICKSTART.md) — Fast onboarding and usage

> **Note:** This README is for framework contributors and advanced users. For general usage, setup, and high-level documentation, see the above links.

This directory contains the core framework code for AgentSpring.

## Core Modules
AgentSpring provides both traditional API and agentic orchestration capabilities:
- **api.py** - FastAPI integration and agent app base (FastAPIAgent)
- **orchestration.py** - Agentic orchestration engine (LLM-driven tool chaining)
- **tools/** - Modular tool registry (communication, data, system, business, etc)
- **llm.py** - LLM helpers and prompt templates
- **models.py** - Standard Pydantic models
- **tasks.py** - Async task helpers and batch processing
- **multi_tenancy.py** - Multi-tenant support
- **api_versioning.py** - API versioning
- **cli.py** - CLI for scaffolding new apps

## Example Usage

### Use a Tool from the Registry
```python
from agentspring.tools import tool_registry
result = tool_registry.execute_tool("read_file", file_path="README.md")
print(result.result["content"])
```

### Use Agentic Orchestration
```python
from agentspring.orchestration import create_orchestrator, set_prompt_template

set_prompt_template("""
You are an expert workflow orchestrator. Given a user instruction, output a JSON list of tool steps.
Only use these tools: {tools_list}
User instruction: {prompt}
""")

orchestrator = create_orchestrator()
user_prompt = "Download the latest sales data, validate it, generate a report, and notify analytics."
result = orchestrator.execute_prompt(user_prompt)
print(result)
```

### Advanced: Tool Chaining & Custom Workflows
```python
from agentspring.orchestration import create_orchestrator
from agentspring.tools import tool_registry

orchestrator = create_orchestrator()
user_prompt = "Read the latest log file, summarize errors, and send a Slack alert if any critical errors are found."
plan = orchestrator.parse_prompt(user_prompt)
for step in plan:
    tool_result = tool_registry.execute_tool(step["tool"], **step["args"])
    print(tool_result)
```

See the main [README](../README.md) for more details, examples, and the full roadmap. 

## Centralized Error Handling & Structured Logging

- All API endpoints and background tasks use centralized error handling and structured, JSON-formatted logs.
- Logs include context: user, request/task ID, and error type.
- Logs are stored in `logs/agentspring.log` with automatic rotation (max 10MB, 5 backups).

### Usage
- To add context to logs, pass `user` and `request_id` (for API) or `user` and `task_id` (for Celery) in the `extra` argument of logger calls.
- API endpoints can use the `@log_api_error` decorator to automatically log uncaught exceptions with context.
- Celery task failures are automatically logged with context.

### Log Retention
- The system keeps up to 5 rotated log files, each up to 10MB.
- Old logs are automatically deleted.

### Log Format
- Logs are in JSON for easy searching and parsing.

---

## How to Extend the Framework
- Add new tools to `agentspring/tools/` and register them with the tool registry.
- Add new orchestration strategies in `orchestration.py`.
- Extend models and validation in `models.py`.
- See [TOOL_CONFIGURATION.md](../TOOL_CONFIGURATION.md) for environment variables and security practices.
- For onboarding, see the [Quickstart Guide](../QUICKSTART.md).