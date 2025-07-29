# 🚀 Quick Start Guide

Get AgentSpring running in under 5 minutes!

## ⚠️ Note on textract
`textract` is currently broken on PyPI due to dependency metadata (see https://github.com/deanmalmgren/textract/issues/360). It is not included in requirements.txt. If you need it, install manually:

```bash
pip install --no-deps textract==1.6.4
pip install extract-msg==0.28.7
```

## Prerequisites
- **Python 3.8+**
- **Docker Desktop** (for full stack)
- **Git** (to clone the repository)

## Step 1: Clone and Navigate
```bash
git clone <your-repo-url>
cd agentspring
```

## Step 2: Start Everything
```bash
./start.sh
```
Or run directly (ensure Redis is running):
```bash
python main.py
```

> **Tip:** If you see Redis connection errors, start Redis with `docker-compose up redis` or ensure your local Redis server is running.
## Step 3: Use a Tool Out of the Box
AgentSpring provides a registry of production-ready tools. For example, to read a file:

```python
from agentspring.tools import tool_registry
result = tool_registry.execute_tool("read_file", file_path="README.md")
print(result.result["content"])
```

## Step 4: Try Agentic Orchestration
You can use natural language to orchestrate multi-step workflows:

```python
from agentspring.orchestration import create_orchestrator
orchestrator = create_orchestrator()
result = orchestrator.execute_prompt("Read the README file, summarize it, and send the summary to Slack.")
print(result)
```

## Step 5: Verify It's Working

Wait about 2-3 minutes for everything to start, then check:

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

## Step 6: Test the API

### Quick Test (Recommended)
```bash
make test
```
This will automatically start Redis (if needed) and run all tests. You can also run:
```bash
pytest --cov=agentspring --cov-report=term-missing agentspring/tests/
```

### Manual Test
```bash
# Test a complaint analysis
curl -X POST "http://localhost:8000/analyze" \
  -H "X-API-Key: demo-key" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST123",
    "message": "My account is locked and I need immediate access!"
  }'
```

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **API** | http://localhost:8000 | Main API server |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health Check** | http://localhost:8000/health | System health status |
| **Flower Dashboard** | http://localhost:5555 | Task monitoring dashboard |
| **Ollama** | http://localhost:11434 | LLM model management |

## 🛠️ Starting a New App
- To start your own agentic app, copy the minimal template from `agentspring/examples/minimal_template/`.
- For a concise, production-ready example, see `agentspring/examples/concise_example/`.
- For a full-featured, advanced example, see `agentspring/examples/advanced_example/`.

## 🔑 Authentication

Use this API key for testing:
```
demo-key
```
Include it in the `X-API-Key` header with all requests.

## 📊 Monitoring

```bash
# View all logs
docker-compose logs -f
```

See the main [README](README.md) for more details, troubleshooting, and advanced usage.

## 🛟 Troubleshooting
- **Redis connection errors:** Make sure Redis is running before starting the app or running tests.
- **Test failures:** Ensure all dependencies are installed, Redis is running, and endpoint function names do not start with `test_`.
- **Error response format mismatch:** Ensure the global exception handler returns JSON with `error`, `code`, and `timestamp` fields (see test examples).
- **Other issues:** See the [TOOL_CONFIGURATION.md](TOOL_CONFIGURATION.md) and [README.md](README.md) FAQ sections.