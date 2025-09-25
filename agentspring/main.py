# agentspring/main.py (update)
from fastapi import FastAPI
from .api import router
from .llm.registry import registry
from .llm.providers.mock import MockProvider

app = FastAPI()

# Register built-in providers
registry.register_provider("mock", MockProvider, is_default=True)

# Include the main router (which includes all API routes)
app.include_router(router)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}