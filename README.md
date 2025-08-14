# AgentSpring 🚀

AgentSpring is a powerful, production-ready Python framework for building and deploying intelligent agentic applications and APIs. It combines the simplicity of traditional REST APIs with the power of large language models (LLMs) to create dynamic, intelligent workflows.

## 🌟 Key Features

### 🛠️ Core Capabilities
- **Dual-Mode Operation**: Seamlessly switch between traditional REST APIs and agentic workflows
- **Production Ready**: Built with scalability, security, and observability in mind
- **Modular Architecture**: Extensible design that grows with your needs
- **Multi-tenancy**: Built-in support for multiple tenants with isolated resources
- **Async-First**: High-performance asynchronous operations throughout

### 🤖 Agentic Features
- **Natural Language Processing**: Convert plain English into executable workflows
- **Tool Chaining**: Combine multiple tools into complex, multi-step processes
- **Context Awareness**: Maintain conversation history and state
- **Self-Healing**: Automatic error recovery and retry mechanisms

### 🏗️ Developer Experience
- **Type Annotations**: Full Python type hints for better IDE support
- **Comprehensive Testing**: Built-in testing utilities and examples
- **Detailed Logging**: Structured logs with context for easy debugging
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

## 🚀 What is AgentSpring?

AgentSpring is designed to bridge the gap between traditional software development and AI-powered applications. It provides two primary ways to build applications:

1. **Traditional APIs**: Build RESTful endpoints using FastAPIAgent for conventional request/response patterns
2. **Agentic Orchestration**: Create intelligent workflows that can understand natural language, make decisions, and execute multi-step processes

### Use Cases
- **Enterprise Automation**: Automate complex business processes with minimal code
- **AI Assistants**: Build conversational agents that can perform tasks
- **Data Processing**: Create intelligent ETL pipelines
- **Customer Support**: Implement AI-powered support systems
- **IoT Integration**: Connect and manage IoT devices with natural language


## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip (latest version)
- Redis (for production deployments)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/agentspring.git
cd agentspring

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install with all dependencies
pip install -e ".[all]"

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### Configuration

Create a `.env` file in your project root with the following variables:

```env
# Core Settings
AGENTSPRING_ENV=development  # or 'production'
LOG_LEVEL=INFO

# API Configuration
API_KEY=your-secret-key
API_PREFIX=/api/v1

# Redis Configuration (for production)
REDIS_URL=redis://localhost:6379/0

# LLM Configuration
LLM_PROVIDER=ollama  # or 'openai', 'anthropic', etc.
LLM_MODEL=llama3.2   # or 'gpt-4', 'claude-2', etc.
```

## 🧠 Agentic Orchestration

AgentSpring's orchestration engine allows you to create intelligent workflows using natural language. Here's a comprehensive example:

```python
from agentspring.orchestration import create_orchestrator, set_prompt_template
from agentspring.tools import tool_registry

# Configure the system prompt (optional but recommended)
set_prompt_template("""
You are an expert workflow orchestrator with access to the following tools:

{tools_list}

Instructions:
1. Analyze the user's request carefully
2. Break it down into discrete steps
3. For each step, specify the tool and required parameters
4. Ensure all necessary information is provided
5. Handle errors gracefully

Output format (JSON array of steps):
[
    {
        "tool": "tool_name",
        "args": {
            "param1": "value1",
            "param2": "value2"
        },
        "description": "What this step accomplishes"
    }
]

User instruction: {prompt}
""")

# Create an orchestrator instance
orchestrator = create_orchestrator(
    max_steps=10,           # Maximum number of steps before stopping
    allow_user_input=True,  # Whether to prompt for user input when needed
    verbose=True            # Print detailed execution logs
)

# Example workflow
user_prompt = """
Download the latest sales data from our S3 bucket 'monthly-sales', 
validate the data quality, generate a PDF report with key metrics,
and send it to the sales team via email.
"""

try:
    # Execute the workflow
    result = orchestrator.execute_prompt(
        user_prompt,
        context={
            "customer_id": "acme-corp",
            "user_id": "user-123",
            "priority": "high"
        },
        callbacks={
            "on_step_start": lambda step: print(f"Starting step: {step['tool']}"),
            "on_step_complete": lambda step, result: print(f"Completed: {step['tool']}")
        }
    )
    print("Workflow completed successfully!")
    print("Final result:", result)

except Exception as e:
    print(f"Workflow failed: {str(e)}")
    # Handle error (e.g., send notification, retry, etc.)
```

### Workflow Features

1. **Context Management**
   - Maintain state across steps
   - Access previous step results
   - Pass custom context variables

2. **Error Handling**
   - Automatic retries with exponential backoff
   - Custom error handlers
   - Step-specific error recovery

3. **Observability**
   - Detailed execution logs
   - Performance metrics
   - Audit trail of all actions

4. **Security**
   - Role-based access control
   - Input validation
   - Sensitive data handling

## 🧰 Tool Registry System

AgentSpring's tool registry is a powerful component that allows you to register, discover, and execute modular tools. It serves as the foundation for building agentic workflows.

### Built-in Tools

AgentSpring comes with a rich set of pre-built tools organized into categories:

1. **Communication**
   - `send_email`: Send emails with attachments
   - `send_slack_message`: Post messages to Slack
   - `make_phone_call`: Initiate phone calls (Twilio integration)
   - `send_sms`: Send text messages

2. **Data Processing**
   - `read_file`: Read files from local or remote storage
   - `write_file`: Write data to files
   - `query_database`: Execute SQL queries
   - `process_csv`: Process CSV data
   - `convert_format`: Convert between data formats (JSON, YAML, XML)

3. **Web & APIs**
   - `http_request`: Make HTTP/HTTPS requests
   - `scrape_website`: Extract data from web pages
   - `download_file`: Download files from URLs
   - `rest_api_call`: Make authenticated API calls

4. **AI & ML**
   - `generate_text`: Generate text using LLMs
   - `classify_text`: Categorize text
   - `extract_entities`: Extract named entities
   - `summarize_text`: Create summaries of text

5. **System**
   - `execute_command`: Run shell commands
   - `schedule_task`: Schedule future tasks
   - `get_system_info`: Get system information
   - `manage_processes`: Monitor and control processes

### Using the Tool Registry

```python
from agentspring.tools import tool_registry

# List all available tools
print("Available tools:", tool_registry.list_tools())

# Get tool metadata
tool_meta = tool_registry.get_tool_metadata("send_email")
print("Email tool parameters:", tool_meta["parameters"])

# Execute a tool
result = tool_registry.execute_tool(
    "send_email",
    to="team@example.com",
    subject="Daily Report",
    body="Here's your daily report.",
    attachments=["report.pdf"]
)

if result.success:
    print("Email sent successfully!")
else:
    print(f"Failed to send email: {result.error}")

# Batch execution
results = tool_registry.execute_batch([
    {"name": "read_file", "args": {"file_path": "data.json"}},
    {"name": "process_data", "args": {"data": "<<0.result>>"}},  # Reference previous result
    {"name": "write_file", "args": {"file_path": "output.json", "content": "<<1.result>>"}}
])
```

### Creating Custom Tools

1. **Basic Tool Function**

```python
from agentspring.tools import tool_registry
from pydantic import BaseModel
from typing import Optional

# Define input model
class WeatherQuery(BaseModel):
    location: str
    unit: str = "celsius"
    days: Optional[int] = 1

# Register the tool
@tool_registry.register_tool(
    name="get_weather",
    description="Get current weather or forecast for a location",
    parameters={
        "location": {"type": "string", "description": "City name or coordinates"},
        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "default": "celsius"},
        "days": {"type": "integer", "minimum": 1, "maximum": 14, "default": 1}
    },
    required=["location"]
)
async def get_weather(query: WeatherQuery) -> dict:
    """
    Get weather information for a specific location.
    
    Args:
        query: Weather query parameters
        
    Returns:
        dict: Weather data including temperature, conditions, etc.
    """
    # Implementation here
    return {
        "location": query.location,
        "temperature": 22.5,
        "unit": query.unit,
        "conditions": "Sunny",
        "forecast": []
    }
```

2. **Tool with Dependencies**

```python
from agentspring.tools import Tool, depends_on

class DatabaseTool(Tool):
    def __init__(self, db_connection):
        self.db = db_connection
    
    @depends_on("database_connection")
    async def query(self, sql: str, params: dict = None):
        """Execute a SQL query"""
        return await self.db.fetch(sql, params or {})

# Register the tool class
tool_registry.register_tool_class(DatabaseTool(db_connection))
```

### Advanced Features

1. **Tool Composition**
   - Chain multiple tools together
   - Pass outputs between tools
   - Handle errors and retries

2. **Access Control**
   - Role-based tool access
   - Rate limiting
   - Audit logging

3. **Performance**
   - Async execution
   - Caching
   - Parallel processing

4. **Monitoring**
   - Execution metrics
   - Error tracking
   - Usage analytics

For detailed configuration options, see [TOOL_CONFIGURATION.md](TOOL_CONFIGURATION.md).

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
│   ├── / # Full-featured example
```

=======

## 📝 Documentation
- [TOOL_CONFIGURATION.md](TOOL_CONFIGURATION.md): Tool registry and configuration
- [AGENTIC_ROADMAP.md](AGENTIC_ROADMAP.md): Roadmap to a fully agentic system


## Documentation & Onboarding

- Up-to-date README and quickstart guides
- API docs available at `/docs` (Swagger UI) and `/redoc`
- Create custom apps in the `agentspring/examples/` directory
- Troubleshooting and FAQ sections in the README and [TOOL_CONFIGURATION.md](TOOL_CONFIGURATION.md)

## 🏆 Why “AgentSpring”?
# Quickstart: Tenants in AgentSpring

AgentSpring supports multi-tenancy out of the box. By default, only one tenant is created:
- tenant_id: `default`
- api_key: `demo-key`

All API requests must use this tenant unless you create more via the admin API.

**Example: Submit a task and poll for status**
```sh
curl -X POST http://localhost:8000/analyze_async \
  -H "Content-Type: application/json" \
  -H "x-api-key: demo-key" \
  -H "x-role: user" \
  -d '{"customer_id": "default", "message": "My laptop is broken"}'

curl -H "x-api-key: demo-key" -H "x-role: user" \
  http://localhost:8000/tenants/default/tasks/<task_id>/status
```

To see all tenants:
```sh
curl -H "X-Admin-Key: admin-key" http://localhost:8000/tenants
```

To add more tenants, use the `/tenants` endpoint with your admin key.

---

The name **AgentSpring** draws inspiration from the renowned Spring framework in the Java ecosystem, celebrated for its modularity, extensibility, and developer productivity. Just as Spring enables rapid development and flexible architecture for Java applications, AgentSpring empowers developers to build robust, modular, and scalable agentic APIs and workflows with ease.

## Contributing

We welcome contributions! Please see `CONTRIBUTING.md` for guidelines, or open an issue to discuss your ideas.

## Advanced Usage
- See [AGENTIC_ROADMAP.md](AGENTIC_ROADMAP.md) for advanced features and future plans.
- For extending the tool registry, see [TOOL_CONFIGURATION.md](TOOL_CONFIGURATION.md).
- For orchestration engine details, see `agentspring/orchestration.py` and the framework [README](agentspring/README.md).

## Environment Variables
- `AGENTSPRING_ENV`: Application environment (development, staging, production)
- `SENTRY_DSN`: Sentry DSN for error monitoring
- `LOG_DIR`: Directory for log files
- `CELERY_BROKER_URL`: Redis URL for Celery broker
- `CELERY_RESULT_BACKEND`: Redis URL for Celery result backend
- `API_KEY`: API authentication key
- `TENANT_ID`: (if multi-tenancy is used)
- ... (see .env.example for more)

## Monitoring & Alerting
- **Sentry**: Set `SENTRY_DSN` to enable error monitoring.
- **Log Aggregation**: Forward logs to ELK, Loki, or Datadog using their agents or log shippers.

## Observability & Monitoring
- Health check: `/health`
- Readiness probe: `/readiness`
- Liveness probe: `/liveness`
- Task status: `/tasks/{task_id}/status`
- Task result: `/tasks/{task_id}/result`

## Deployment & Scalability

### Docker Compose
To start the app, Redis, and Celery workers with horizontal scaling:

```bash
docker-compose up --build --scale app=2 --scale celery_worker=2
```

- Healthchecks are configured for all services.
- Uses `.env` for configuration.

### Kubernetes Deployment

1. Create the config and secrets:
   ```bash
   kubectl apply -f k8s/configmap.yaml
   kubectl apply -f k8s/secret.yaml
   ```
2. Deploy Redis:
   ```bash
   kubectl apply -f k8s/redis-deployment.yaml
   ```
3. Deploy the API app and Celery workers:
   ```bash
   kubectl apply -f k8s/app-deployment.yaml
   kubectl apply -f k8s/celery-worker-deployment.yaml
   ```
4. Expose the API app:
   ```bash
   kubectl apply -f k8s/app-service.yaml
   ```

- The app will be available via the LoadBalancer IP.
- Readiness/liveness probes are configured for production health.
- Scale deployments by editing the `replicas` field.

## Automated Testing & CI

- All core features are covered by unit, integration, and end-to-end tests.
- CI pipeline runs linting (`flake8`), tests (`pytest`), and enforces a minimum 80% coverage threshold.

### Running Tests Locally

```bash
pip install -r requirements.txt
# Makefile 'test' target will start Redis if needed
make test
# Or manually:
pytest --cov=agentspring --cov-report=term-missing agentspring/tests/
```

### Linting

```bash
flake8 agentspring/
```

- All code must pass linting and coverage checks before merging.

## Troubleshooting & FAQ

### Docker/Kubernetes deployment issues
- **App not starting:** Check logs for missing environment variables or secrets.
- **Healthcheck failures:** Ensure Redis and Celery are healthy and reachable.
- **Redis not running:** Start Redis with `docker-compose up redis` or ensure your local Redis server is running.

### Redis/Celery connectivity
- **Task status always pending:** Make sure a Celery worker is running and connected to the same Redis instance as the app.

### API key/authentication errors
- **401 Unauthorized:** Ensure the correct `API_KEY` is set in your environment and sent as the `x-api-key` header.
- **403 Forbidden:** Check the `x-role` header and required role for the endpoint.

### Test failures
- **Coverage below threshold:** Add or improve tests for uncovered code.
- **Linting errors:** Run `flake8` and fix reported issues.
- **Redis connection errors:** Ensure Redis is running before running tests (see Makefile `test` target for automation).
- **Pytest discovers endpoint functions as tests:** Ensure endpoint function names do not start with `test_`.
- **Error response format mismatch:** Ensure the global exception handler returns JSON with `error`, `code`, and `timestamp` fields.

For more, see [TOOL_CONFIGURATION.md](TOOL_CONFIGURATION.md).

## Compliance & Auditability

- Audit trails for user actions and data changes (all POST, PUT, DELETE requests are logged)
- Data retention and privacy controls (see code stubs for extension)
- Compliance documentation and configuration in TOOL_CONFIGURATION.md

## Agentic Extensibility

- Agent orchestration via `AgentOrchestrator` (see `agentspring/orchestration.py`)
- All agent actions are logged to the audit trail
- Supports pausing, inspecting, and debugging agent runs
- Easily extensible for new agent workflows and interfaces

## Full Stack Production-like Testing

To run the full stack with all observability and monitoring tools (API, Celery, Redis, Prometheus, Grafana, Filebeat, Promtail):

```bash
docker-compose -f docker-compose.full.yml up --build
```

### Services and Ports
- **API:** http://localhost:8000
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3000 (admin/admin)
- **Redis:** localhost:6379
- **Filebeat/Promtail:** log shippers (no UI)

- Logs are available in the ./logs directory.
- Prometheus scrapes metrics from the API at /metrics.
- Grafana dashboard is pre-provisioned (import if not visible).

This setup lets you test the entire system end-to-end as it would run in production.
