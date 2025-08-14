# 🛠️ Tool Configuration Guide

This document provides comprehensive guidance on configuring and managing tools in AgentSpring, including environment setup, security best practices, and advanced customization options.

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install agentspring[tools]
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start Using Tools**
   ```python
   from agentspring.tools import tool_registry
   
   # List available tools
   print(tool_registry.list_tools())
   ```

## 🔧 Environment Variables

### Core Configuration
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AGENTSPRING_ENV` | No | `development` | Runtime environment: `development`, `staging`, or `production` |
| `LOG_LEVEL` | No | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `LOG_DIR` | No | `logs` | Directory for log files |

### API & Authentication
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_KEY` | Yes | - | Secret key for API authentication |
| `API_PREFIX` | No | `/api/v1` | Base path for API endpoints |
| `CORS_ORIGINS` | No | `*` | Comma-separated list of allowed origins |

### Database & Cache
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDIS_URL` | No | `redis://localhost:6379/0` | Redis connection URL |
| `POSTGRES_DSN` | No | - | PostgreSQL connection string |
| `CACHE_TTL` | No | `3600` | Default cache TTL in seconds |

### LLM Integration
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LLM_PROVIDER` | No | `openai` | LLM provider: `openai`, `anthropic`, `local` |
| `OPENAI_API_KEY` | Conditional | - | Required if using OpenAI |
| `ANTHROPIC_API_KEY` | Conditional | - | Required if using Anthropic |
| `LLM_MODEL` | No | `gpt-4` | Default model to use |
| `EMBEDDING_MODEL` | No | `text-embedding-ada-002` | Model for embeddings |

### Monitoring & Observability
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SENTRY_DSN` | No | - | Sentry DSN for error tracking |
| `PROMETHEUS_PORT` | No | `8001` | Port for Prometheus metrics |
| `METRICS_PREFIX` | No | `agentspring_` | Prefix for all metrics |

## 🔒 Security Best Practices

### Authentication & Authorization

1. **API Authentication**
   - Always use HTTPS in production
   - Rotate API keys regularly
   - Implement rate limiting
   ```python
   # Example: Rate limiting configuration
   from fastapi import FastAPI, Request
   from fastapi.middleware import Middleware
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app = FastAPI(middleware=[Middleware(SlowAPIMiddleware)])
   app.state.limiter = limiter
   app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
   ```

2. **Role-Based Access Control (RBAC)**
   - Use `x-role` header for role specification
   - Default roles: `admin`, `user`, `guest`
   - Custom roles can be defined in configuration
   ```yaml
   # Example role configuration
   roles:
     admin:
       permissions: ["*"]
     user:
       permissions: ["read", "write"]
     guest:
       permissions: ["read"]
   ```

3. **Input Validation**
   - All inputs are validated using Pydantic models
   - HTML/JS injection prevention with Bleach
   - Maximum length and size limits
   ```python
   from pydantic import BaseModel, constr, conint
   
   class UserInput(BaseModel):
       username: constr(min_length=3, max_length=50, strip_whitespace=True)
       age: conint(gt=0, lt=120)
       bio: str = ""
   ```

### Secure Configuration

1. **Secrets Management**
   - Never commit secrets to version control
   - Use environment-specific secret managers
   - Rotate secrets regularly
   ```bash
   # Example: Using python-dotenv with .gitignore
   echo ".env" >> .gitignore
   echo "SECRET_KEY=your-secret-key" > .env
   ```

2. **Network Security**
   - Enable CORS only for trusted origins
   - Use HTTP security headers
   - Implement request timeouts
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://trusted-domain.com"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

## 🛠️ Tool Development Guide

### Creating a New Tool

1. **Basic Tool Structure**
   ```python
   from agentspring.tools import tool_registry, Tool
   from pydantic import BaseModel, Field
   from typing import Optional, List, Dict, Any
   
   class WeatherQuery(BaseModel):
       location: str = Field(..., description="City name or coordinates")
       days: int = Field(1, ge=1, le=14, description="Forecast days")
       units: str = Field("metric", regex="^(metric|imperial)$")
   
   @tool_registry.register_tool(
       name="get_weather",
       description="Get weather forecast for a location",
       category="weather",
       version="1.0.0",
       requires_approval=False,
       rate_limit="10/minute"
   )
   async def get_weather(query: WeatherQuery) -> Dict[str, Any]:
       """
       Get weather forecast for a specific location.
       
       Args:
           query: Weather query parameters
           
       Returns:
           Dict containing weather data
       """
       # Implementation here
       return {
           "location": query.location,
           "forecast": [],
           "units": query.units
       }
   ```

2. **Tool Configuration**
   - **Name**: Unique identifier (snake_case)
   - **Description**: Clear, concise tool purpose
   - **Category**: Grouping for related tools
   - **Version**: Semantic versioning (MAJOR.MINOR.PATCH)
   - **Rate Limiting**: Requests per time period
   - **Approval**: Whether tool requires manual approval

### Testing Tools

1. **Unit Tests**
   ```python
   import pytest
   from agentspring.tools import tool_registry
   
   @pytest.mark.asyncio
   async def test_get_weather():
       result = await tool_registry.execute_tool(
           "get_weather",
           location="London",
           days=3,
           units="metric"
       )
       assert result.success
       assert "forecast" in result.result
       assert len(result.result["forecast"]) == 3
   ```

2. **Integration Tests**
   ```python
   @pytest.mark.integration
   async def test_weather_workflow():
       # Test complete workflow using the tool
       pass
   ```

## 🚦 Performance Optimization

### Caching

1. **Tool Result Caching**
   ```python
   from agentspring.cache import cache
   
   @cache(ttl=3600)  # Cache for 1 hour
   async def expensive_operation(param: str) -> dict:
       # Expensive computation here
       return {"result": param.upper()}
   ```

2. **Cache Invalidation**
   ```python
   from agentspring.cache import invalidate_cache
   
   async def update_data(key: str, value: Any):
       # Update data
       await invalidate_cache(f"prefix:{key}")
   ```

### Parallel Execution

```python
from agentspring.tasks import parallel_map

async def process_items(items):
    results = await parallel_map(
        process_item,  # Your processing function
        items,         # List of items to process
        max_concurrent=5  # Maximum parallel executions
    )
    return results
```

## 📊 Monitoring & Logging

### Structured Logging

```python
import structlog

logger = structlog.get_logger()

async def process_data(data):
    logger.info("processing_data", 
        data_size=len(data),
        user_id=current_user.id,
        tags=["data_processing"]
    )
    # Processing logic
```

### Metrics Collection

```python
from agentspring.metrics import counter, histogram

@counter("api_requests_total", "Total API requests", ["endpoint", "status"])
@histogram("request_duration_seconds", "Request duration in seconds", ["endpoint"])
async def handle_request(endpoint: str):
    start_time = time.time()
    # Handle request
    duration = time.time() - start_time
    return {"status": "success", "duration": duration}
```

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      redis:
        image: redis
        ports:
          - 6379:6379
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[test]"
      - name: Run tests
        run: |
          pytest --cov=agentspring --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## 📚 Additional Resources

- [API Documentation](https://docs.agentspring.dev/api)
- [Tutorials](https://docs.agentspring.dev/tutorials)
- [Community Forum](https://community.agentspring.dev)
- [GitHub Issues](https://github.com/agentspring/agentspring/issues)