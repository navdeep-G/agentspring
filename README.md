# AgentSpring

AgentSpring is a Python framework for building, deploying, and managing agentic APIs and agentic workflows with minimal code and maximum flexibility.

## 🚀 What is AgentSpring?
AgentSpring lets you build both:
- **Traditional APIs** using FastAPIAgent (for classic RESTful endpoints)
- **Agentic Orchestration**: Dynamically parse natural language prompts into multi-step tool workflows using LLMs and a tool registry

## ⚡ Quick Start

```bash
git clone <repository>
cd agentspring
./start.sh
```
Or run directly:
```bash
python main.py
```
To run a specific example agent:
```bash
export AGENTSPRING_APP=examples.customer_support_agent.endpoints
python main.py
```

## 🧠 Agentic Orchestration Example
AgentSpring supports prompt-driven, multi-step workflows:

```python
from agentspring.orchestration import create_orchestrator, set_prompt_template

# (Optional) Set a custom prompt template for your domain
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

## 🛠️ Tool Registry System
AgentSpring provides a modular tool registry with production-ready tools for communication, data, web, business, media, and system operations.

```python
from agentspring.tools import tool_registry
result = tool_registry.execute_tool("read_file", file_path="README.md")
print(result.result["content"])
```

See [TOOL_CONFIGURATION.md](TOOL_CONFIGURATION.md) for setup and configuration details.

## 🎯 Why Use AgentSpring?
- **Agentic Orchestration**: Turn natural language into multi-step workflows
- **Traditional APIs**: Use FastAPIAgent for classic REST endpoints
- **Production Ready**: Health checks, metrics, authentication, error handling, multi-tenancy, async, batch, and more
- **Extensible**: Register your own tools, customize prompt templates, and build domain-specific agents
- **See the [AGENTIC_ROADMAP.md](AGENTIC_ROADMAP.md) for the vision and roadmap**

## 📁 Project Structure
```
agentspring/
├── agentspring/                # Framework code
│   ├── api.py                  # API helpers (FastAPIAgent, metrics, auth)
│   ├── orchestration.py        # Agentic orchestration engine
│   ├── tools/                  # Tool registry (communication, data, system, etc)
│   ├── llm.py                  # LLM integration helpers
│   ├── models.py               # Base models and validation
│   ├── tasks.py                # Async task management
│   ├── celery_app.py           # Celery configuration
│   ├── multi_tenancy.py        # Multi-tenant support
│   └── api_versioning.py       # API versioning
├── examples/
│   ├── customer_support_agent/ # Full-featured example (advanced)
│   ├── simple_agent/           # Concise, production-ready example
│   └── starter_agent/          # Minimal template for new apps
```

## 🌟 Example Apps
- See `examples/starter_agent/` for a minimal template to start your own app.
- See `examples/simple_agent/` for a concise, production-ready example (~60 lines).
- See `examples/customer_support_agent/` for a full-featured, advanced example.

## 📝 Documentation
- [TOOL_CONFIGURATION.md](TOOL_CONFIGURATION.md): Tool registry and configuration
- [AGENTIC_ROADMAP.md](AGENTIC_ROADMAP.md): Roadmap to a fully agentic system
- [QUICKSTART.md](QUICKSTART.md): Step-by-step quick start guide

## 🏆 Why “AgentSpring”?
The name **AgentSpring** draws inspiration from the renowned Spring framework in the Java ecosystem, celebrated for its modularity, extensibility, and developer productivity. Just as Spring enables rapid development and flexible architecture for Java applications, AgentSpring empowers developers to build robust, modular, and scalable agentic APIs and workflows with ease.
