# Simple Agent Example

This example demonstrates how **AgentFlow** makes it incredibly simple to build agentic APIs.

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
from agentflow.api import FastAPIAgent
from agentflow.llm import classify

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
- **Learning**: Understanding AgentFlow patterns
- **Starting Point**: Building more complex agents (see `starter_agent` for a blank template)

## 📝 **Usage**

```bash
# Set the environment variable to use this example
export AGENTFLOW_APP=examples.simple_agent.endpoints

# Start the server
./start.sh
```

## 🔗 **API Endpoints**

- `POST /classify` - Classify text into categories
- `POST /summarize` - Summarize text
- `POST /analyze` - Comprehensive text analysis
- `GET /health` - Health check (automatic)

This example proves that **AgentFlow** makes building agentic APIs as simple as possible while maintaining all the production-ready features! 