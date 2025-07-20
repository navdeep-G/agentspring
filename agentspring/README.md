# AgentSpring Framework

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

See the main [README](../README.md) for more details, examples, and the full roadmap. 