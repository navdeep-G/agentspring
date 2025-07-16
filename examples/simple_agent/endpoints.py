"""
Simple Agent Example - Demonstrates AgentFlow's simplified API
"""
from datetime import datetime
from agentflow.api import FastAPIAgent, AuthMiddleware
from agentflow.llm import LLMHelper
from agentflow.models import TextRequest, ClassificationResponse, SummarizationResponse
from agentflow.tasks import AsyncTaskManager
from agentflow.celery_app import celery_app

# Initialize the agent with built-in functionality
agent = FastAPIAgent(title="Simple Agent", api_key_env="CUSTOMER_SUPPORT_AGENT_API_KEY")

# Initialize LLM helper
llm = LLMHelper("llama3.2")

# Initialize task manager
task_manager = AsyncTaskManager(celery_app)

@agent.app.post("/classify")
async def classify_text(request: TextRequest):
    """Classify text into categories"""
    categories = ["Infrastructure", "Account", "Billing", "Legal", "Other"]
    category = llm.classify(request.message, categories)
    
    return ClassificationResponse(
        status="success",
        timestamp=datetime.now().isoformat(),
        category=category,
        confidence=0.8
    )

@agent.app.post("/summarize")
async def summarize_text(request: TextRequest):
    """Summarize text"""
    summary = llm.summarize(request.message, max_length=100)
    
    return SummarizationResponse(
        status="success",
        timestamp=datetime.now().isoformat(),
        summary=summary,
        original_length=len(request.message),
        summary_length=len(summary)
    )

@agent.app.post("/analyze")
async def analyze_text(request: TextRequest):
    """Comprehensive text analysis"""
    # Use multiple LLM operations
    category = llm.classify(request.message, ["Infrastructure", "Account", "Billing", "Legal", "Other"])
    priority = llm.detect_priority(request.message)
    summary = llm.summarize(request.message, max_length=150)
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "analysis": {
            "category": category,
            "priority": priority,
            "summary": summary,
            "confidence": 0.8
        }
    }

# Get the FastAPI app instance
app = agent.get_app() 