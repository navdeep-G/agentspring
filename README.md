# AgentSpring

AgentSpring is a Python framework for building, deploying, and managing agentic APIs and agentic workflows with minimal code and maximum flexibility.

## 🚀 What is AgentSpring?
AgentSpring lets you build both:
- **Traditional APIs** using FastAPIAgent (for classic RESTful endpoints)
- **Agentic Orchestration**: Dynamically parse natural language prompts into multi-step tool workflows using LLMs and a tool registry

## ⚡ Quick Start

```bash
git clone https://github.com/navdeep-G/agentspring.git
cd agentspring
./start.sh
```
Or run directly:
```bash
python main.py
```
To run a specific example agent:
```bash
export AGENTSPRING_APP=examples..endpoints
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
├── 
│   ├── / # Full-featured example (advanced)
│   ├── /           # Concise, production-ready example
│   └── /          # Minimal template for new apps
```

<<<<<<< Updated upstream
=======
## 🌟 Custom Apps
- To start a new app, copy the minimal template from `agentspring/examples/minimal_template/`.
- For a concise, production-ready example (~60 lines), see `agentspring/examples/concise_example/`.
- For a full-featured, advanced example, see `agentspring/examples/advanced_example/`.

>>>>>>> Stashed changes
## 📝 Documentation
- [TOOL_CONFIGURATION.md](TOOL_CONFIGURATION.md): Tool registry and configuration
- [AGENTIC_ROADMAP.md](AGENTIC_ROADMAP.md): Roadmap to a fully agentic system
- [QUICKSTART.md](QUICKSTART.md): Step-by-step quick start guide

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

All endpoints are documented in the OpenAPI schema (Swagger UI).

## Error Response Format
All errors return JSON with:
```
```

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
