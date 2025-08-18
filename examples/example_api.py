import uvicorn
from fastapi import FastAPI, Request
from agentspring.tools import tool_registry
from agentspring.metrics import REQUEST_COUNTER, get_metrics
from fastapi.responses import Response

# Create a minimal FastAPI app
app = FastAPI()

# Define a simple tool for testing
@tool_registry.register(name="hello_world", description="A simple tool that returns a greeting.")
def hello_world(name: str = "World") -> dict:
    return {"message": f"Hello, {name}!"}

# Add a test endpoint to trigger the tool
@app.post("/test-greeting")
def test_greeting(data: dict):
    name = data.get("name", "World")
    result = tool_registry.execute_tool(name="hello_world", kwargs={"name": name})
    return result.result

# Add the metrics tracking middleware
@app.middleware("http")
async def track_requests(request: Request, call_next):
    response = await call_next(request)
    REQUEST_COUNTER.labels(
        method=request.method,
        endpoint=request.url.path,
        http_status=response.status_code
    ).inc()
    return response

# Add the /metrics endpoint
@app.get("/metrics")
def metrics():
    return Response(get_metrics(), media_type="text/plain")

# Add a basic health endpoint
@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

