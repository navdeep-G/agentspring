# AgentSpring

AgentSpring is a Python framework that provides everything you need to build, deploy, and manage agentic APIs with minimal code and maximum functionality.

## ⚠️ Note on textract and pip 24.1+
If you need to use `textract`, you must install pip<24.1 first, because pip 24.1+ no longer supports legacy setup.py install packages:

```bash
python -m pip install "pip<24.1"
pip install -r requirements.txt
```

This is required for `textract` and some other legacy packages. See the pip 24.1 release notes for details.

## 🚀 New: Comprehensive Tool Registry System

AgentSpring now includes a modular, extensible tool registry system with production-ready tools for:
- Communication (Email, SMS, Slack, Discord)
- Data & Storage (File ops, database, PDF, OCR, CSV, JSON)
- Web & Search (HTTP, download)
- Business (Calendar, CRM, user management, reports)
- Media (Audio transcription, image analysis)
- System/Admin (System info, logs, math, text, environment, shell commands, temp files)

### Example: Use a Tool Out of the Box
```python
from agentspring.tools import tool_registry
result = tool_registry.execute_tool("read_file", file_path="README.md")
if result.success:
    print(result.result["content"])
else:
    print("Error:", result.error)
```

See the [TOOL_CONFIGURATION.md](TOOL_CONFIGURATION.md) for setup and configuration details.

## Why Use AgentSpring?

### 🎯 **Efficient and Simple Codebase**
AgentSpring is built to help you create agentic APIs with clear, maintainable code. The framework emphasizes simplicity, so you can focus on your application’s logic rather than boilerplate.

```python
from agentspring.api import FastAPIAgent, standard_endpoints
from agentspring.llm import classify, summarize, detect_priority
from agentspring.tasks import agentspring_task, batch_process
from agentspring.multi_tenancy import tenant_router

agent = FastAPIAgent(title="My Agent")

@agent.app.post("/analyze")
async def analyze(request):
    category = classify(request.message, ["Tech", "Support", "Billing"])
    summary = summarize(request.message)
    return {"category": category, "summary": summary}

# Register standard async/batch endpoints and tenant management
standard_endpoints(agent.app, task_manager)
agent.app.include_router(tenant_router)

app = agent.get_app()
```

### 🚀 **Built-in Production Features**
- **Health Checks** - Automatic `/health` endpoint
- **Metrics Tracking** - Request/response metrics in Redis
- **Authentication** - API key validation
- **Error Handling** - Global exception handling
- **Input Validation** - XSS protection, format validation
- **Multi-tenancy** - Isolated tenant configurations (just add `tenant_router`)
- **API Versioning** - Backward-compatible API evolution
- **Async Processing** - Celery task management (`@agentspring_task`)
- **Batch Processing** - One-liner batch submission (`batch_process`)
- **Observability** - Request/response metrics, health checks, logging

### 🧠 **LLM Integration Made Simple**
```python
from agentspring.llm import classify, summarize, detect_priority

category = classify(text, ["Category1", "Category2"])
priority = detect_priority(text)
summary = summarize(text, max_length=100)
```

## Example Apps
- See `examples/starter_agent/` for a minimal template to start your own app.
- See `examples/simple_agent/` for a concise, production-ready example (~60 lines).
- See `examples/customer_support_agent/` for a full-featured, advanced example.

## 🎯 **Perfect For**

- **Customer Support Agents** - Classify, route, and respond to tickets
- **Content Analysis** - Summarize, categorize, and extract insights
- **Workflow Automation** - Process documents, emails, and forms
- **AI-Powered APIs** - Any LLM-based service
- **Multi-tenant SaaS** - Isolated customer environments

## 🚀 **Quick Start**

> **Note:** For development and testing, install dependencies with:
> ```bash
> pip install -r test_requirements.txt
> ```
> For production, use:
> ```bash
> pip install -r requirements.txt
> ```

### 1. **Clone & Setup**
```bash
git clone <repository>
cd enterprise_agent_api
./start.sh
```

### 2. **Create Your Agent**
```python
from agentspring.api import FastAPIAgent
from agentspring.llm import classify

agent = FastAPIAgent(title="My Agent")

@agent.app.post("/process")
async def process_text(request):
    result = classify(request.message, ["Positive", "Negative"])
    return {"sentiment": result}

app = agent.get_app()
```

### 3. **Run Your Agent**
```bash
export AGENTFLOW_APP=examples.my_agent.endpoints
./start.sh
```

### 4. **Test Your Agent**
```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key" \
  -d '{"customer_id": "user123", "message": "I love this product!"}'
```

## 📁 **Project Structure**

```
enterprise_agent_api/
├── agentflow/                 # Framework code
│   ├── api.py                # API helpers (FastAPIAgent, metrics, auth)
│   ├── llm.py                # LLM integration helpers
│   ├── models.py             # Base models and validation
│   ├── tasks.py              # Async task management
│   ├── celery_app.py         # Celery configuration
│   ├── multi_tenancy.py      # Multi-tenant support
│   └── api_versioning.py     # API versioning
├── examples/
│   ├── customer_support_agent/  # Full-featured example (advanced)
│   ├── simple_agent/           # Concise, production-ready example
│   └── starter_agent/          # Minimal template for new apps
```

## 🌟 **Examples**

### **Starter Agent** (minimal template)
- Use as a blank starting point for your own app

### **Simple Agent** (~60 lines)
- Basic classification and summarization
- Perfect for prototyping and learning
- All production features included

### **Customer Support Agent** (full-featured)
- Support ticket processing, async, batch, routing, escalation
- Complete audit logging and multi-tenancy

## 🔧 **Framework Components**

### **API Layer** (`agentflow.api`)
- `FastAPIAgent` - Base agent class with built-in functionality
- `standard_endpoints` - Register async and batch endpoints in one line
- `MetricsTracker` - Automatic request/response metrics
- `AuthMiddleware` - API key authentication
- `HealthEndpoint` - Standard health checks

### **LLM Layer** (`agentflow.llm`)
- One-liner helpers: `classify`, `summarize`, `detect_priority`, `extract_structured_data`
- `PromptTemplates` - Common prompt patterns
- `OutputParsers` - Common output parsing
- Retry logic and fallback mechanisms

### **Models Layer** (`agentflow.models`)
- `BaseRequest`/`BaseResponse` - Common request/response patterns
- `TextRequest` - Text processing requests
- `TaskResult`, `BatchResult`, `SentimentResponse`, `ExtractionResponse`
- `InputValidator` - Input sanitization and validation

### **Tasks Layer** (`agentflow.tasks`)
- `@agentspring_task` - Decorator for Celery tasks (progress, retry, result)
- `AsyncTaskManager` - Celery task management
- `batch_process` - One-liner batch submission
- Async polling helpers

### **Multi-Tenancy** (`agentflow.multi_tenancy`)
- `tenant_router` - Plug-and-play tenant management endpoints

## 🎯 **Why AgentSpring?**

### **For Developers**
- **Faster Development** - Focus on business logic, not boilerplate
- **Less Bugs** - Proven patterns and validation
- **Better Testing** - Built-in test utilities
- **Easy Scaling** - Async processing and multi-tenancy

### **For Teams**
- **Consistent APIs** - Standardized patterns across projects
- **Production Ready** - Built-in observability and monitoring
- **Easy Maintenance** - Clean, modular architecture
- **Rapid Prototyping** - Go from idea to API in minutes

### **For Businesses**
- **Faster Time to Market** - Reduce development time by 90%
- **Lower Costs** - Less code to write and maintain
- **Better Reliability** - Proven production patterns
- **Scalable Architecture** - Built for growth

## Why “AgentSpring”?

The name **AgentSpring** draws inspiration from the renowned Spring framework in the Java ecosystem, celebrated for its modularity, extensibility, and developer productivity. Just as Spring enables rapid development and flexible architecture for Java applications, AgentSpring empowers developers to build robust, modular, and scalable agentic APIs with ease.

The word “spring” also evokes ideas of growth, renewal, and dynamic action—reflecting our framework’s mission to help agentic applications flourish and respond rapidly to new challenges. With AgentSpring, you get a fresh, energetic foundation for building the next generation of intelligent, autonomous systems.

## 🏗️ Technical Architecture

AgentSpring provides a robust backend framework for building agentic APIs. The diagram below shows how your app, the AgentSpring framework, and infrastructure components interact:

```
Your Agent App (Example)
│
├── FastAPI Endpoints
├── Business Logic
└── Custom Tasks
     │
     ▼
+---------------------+
|   AgentSpring       |
|---------------------|
| - FastAPIAgent      |
| - LLM Helpers       |
| - Async Task Mgmt   |
| - Batch Processing  |
| - Multi-Tenancy     |
| - API Versioning    |
| - Models/Validation |
| - Admin/Health      |
+---------------------+
     │
     ▼
Infrastructure
├── Redis (Broker/Cache)
├── Ollama (LLM)
├── Celery Worker
└── Docker
```

**How to read this diagram:**
- **Your Agent App**: Your custom agent app, with endpoints, business logic, and tasks.
- **AgentSpring**: The framework provides API, async, LLM, multi-tenancy, versioning, and admin utilities.
- **Infrastructure**: Underlying services (Redis, Celery, Ollama, Docker) that power async, LLM, and multi-tenant features.

AgentSpring orchestrates all these layers, letting you focus on your agent’s business logic while providing production-grade infrastructure out of the box.

## 📚 **Documentation**

- [Quick Start Guide](QUICKSTART.md)
- [API Reference](docs/api.md)
- [Examples](examples/)
- [Deployment Guide](docs/deployment.md)

## 🤝 **Contributing**

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 **License**

Apache 2.0 License - see [LICENSE](LICENSE) for details.

---

**Ready to build your first agentic API?** Start with the [Starter Agent Example](examples/starter_agent/) or [Simple Agent Example](examples/simple_agent/) and see how easy it is! 🚀
