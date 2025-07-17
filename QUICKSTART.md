# 🚀 Quick Start Guide

Get AgentSpring running in under 5 minutes!

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

## Step 3: Use a Tool Out of the Box
AgentSpring provides a registry of production-ready tools. For example, to read a file:

```python
from agentspring.tools import tool_registry
result = tool_registry.execute_tool("read_file", file_path="README.md")
print(result.result["content"])
```

See the README for more tool examples and categories.

## Step 4: Verify It's Working

Wait about 2-3 minutes for everything to start, then check:

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

## Step 5: Test the API

### Quick Test (Recommended)
```bash
python test_quickstart.py
```

This will run comprehensive tests to verify everything is working correctly.

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

# View specific service logs
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f ollama
```

## 🛑 Stop the Services

```bash
docker-compose down
```

## 🧪 Run Tests

```bash
# Run comprehensive test suite
python test_scenarios.py

# Run unit tests
python -m pytest tests/
```

## 🔧 Troubleshooting

### Docker not running
```bash
# Start Docker Desktop first, then run:
./start.sh
```

### Port conflicts
If you get port conflicts, check what's using the ports:
```bash
# Check what's using port 8000
lsof -i :8000

# Check what's using port 5555
lsof -i :5555
```

### Models not loading
If the LLM models aren't loading properly:
```bash
# Pull models manually
docker-compose exec ollama ollama pull llama3.2
docker-compose exec ollama ollama pull mistral
```

### Services not healthy
Check service status:
```bash
docker-compose ps
```

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the [API documentation](http://localhost:8000/docs) for all endpoints
- Check out the [Flower dashboard](http://localhost:5555) for task monitoring
- Run the test suite to verify everything is working

## 🆘 Need Help?

- Check the logs: `docker-compose logs -f`
- Verify Docker is running: `docker info`
- Ensure ports are available: `lsof -i :8000`
- Restart everything: `docker-compose down && ./start.sh` 