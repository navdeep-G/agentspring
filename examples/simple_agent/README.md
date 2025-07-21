# Simple Agent Example

This example demonstrates how **AgentSpring** makes it incredibly simple to build agentic APIs and agentic workflows.

## 🚀 Tool Registry System
AgentSpring provides a registry of production-ready tools for common tasks (file ops, email, HTTP, etc). Example:
```python
from agentspring.tools import tool_registry
result = tool_registry.execute_tool("read_file", file_path="README.md")
print(result.result["content"])
```

## 🧠 Orchestration (Agentic Workflows)
You can use AgentSpring's orchestration system to turn natural language prompts into multi-step workflows:
```python
from agentspring.orchestration import create_orchestrator
orchestrator = create_orchestrator()
result = orchestrator.execute_prompt("Read the README file and summarize its content.")
print(result)
```

## 🎯 **What This Example Shows**

- **Minimal Code**: Only ~60 lines vs 600+ lines in the full example
- **Built-in Functionality**: Health checks, metrics, authentication, error handling
- **LLM Integration**: One-liner helpers: `classify`, `summarize`, `detect_priority`
- **Standard Models**: Pre-built request/response models with validation
- **Minimal Endpoints**: Just write your business logic—add async, batch, and tenant features with a single import/function

## 📊 **Comparison**

| Feature | Full Example | Simple Example | Reduction |
|---------|-------------|----------------|-----------|
| Lines of Code | 600+ | ~60 | **90%** |
| Endpoints | 10+ | 3 | **70%** |
| Setup Time | Hours | Minutes | **95%** |

## 🚀 **How It Works**

```python
from agentspring.api import FastAPIAgent
from agentspring.llm import classify

agent = FastAPIAgent(title="Simple Agent")

@agent.app.post("/classify")
async def classify_text(request):
    return {"category": classify(request.message, ["A", "B", "C"])}
```

## 🌟 **What You Get Automatically**

- ✅ **Health Check**: `GET /health`
- ✅ **Metrics Tracking**: Automatic request/response metrics
- ✅ **Authentication**: API key validation
- ✅ **Error Handling**: Global exception handling
- ✅ **Input Validation**: XSS protection, format validation
- ✅ **Response Models**: Standardized response formats

## 🎯 **Perfect For**

- **Prototyping**: Quick proof-of-concepts
- **Simple Agents**: Basic classification/summarization
- **Learning**: Understanding AgentSpring patterns
- **Starting Point**: Building more complex agents (see `starter_agent` for a blank template)

## 📝 **Usage**

```bash
# Set the environment variable to use this example
export AGENTSPRING_APP=examples.simple_agent.endpoints
python main.py
```

See the main [README](../../README.md) for more details and advanced usage. 