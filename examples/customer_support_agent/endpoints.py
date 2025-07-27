"""
Refactored Customer Support Agent using AgentSpring framework components
"""
from datetime import datetime
from typing import List
from agentspring.api import FastAPIAgent, standard_endpoints
from agentspring.llm import classify, detect_priority, summarize
from agentspring.models import TextRequest
from agentspring.tasks import AsyncTaskManager, batch_process
from agentspring.celery_app import celery_app
from agentspring.multi_tenancy import get_current_tenant, tenant_router, TenantConfig
from agentspring.api_versioning import get_api_version, versioned_response
from fastapi import Depends, Request
import uuid
from agentspring.api import log_api_error
from agentspring.metrics import setup_metrics, register_custom_metric
from prometheus_client import Counter
from agentspring.tools import tool_registry
from agentspring.orchestration import create_orchestrator
from fastapi.staticfiles import StaticFiles
import os
from pydantic import BaseModel
import examples.customer_support_agent.tasks
from examples.customer_support_agent.tasks import analyze_complaint_task

# Initialize AgentSpring components
agent = FastAPIAgent(title="Customer Support Agent", api_key_env="CUSTOMER_SUPPORT_AGENT_API_KEY")
task_manager = AsyncTaskManager(celery_app)

# Example custom metric: count /analyze requests
analyze_requests_total = Counter('analyze_requests_total', 'Total /analyze requests')

def count_analyze_requests(request, response):
    if request.url.path == '/analyze':
        analyze_requests_total.inc()

register_custom_metric(count_analyze_requests)

ROUTING_MAP = {
    "Infrastructure": "DevOps Queue",
    "Account": "Customer Success",
    "Billing": "Finance Ops",
    "Legal": "Compliance",
    "Other": "General Inbox"
}
def route_ticket(category: str) -> str:
    return ROUTING_MAP.get(category, "General Support")

def check_escalation(priority: str) -> str:
    if priority.lower() in ["critical", "high"]:
        return "Escalation triggered"
    return "No escalation necessary"

@agent.app.post("/analyze")
async def analyze_complaint(
    request: TextRequest,
    tenant: TenantConfig = Depends(get_current_tenant),
    api_version: str = Depends(get_api_version)
):
    task_id = str(uuid.uuid4())
    category = classify(request.message, ["Infrastructure", "Account", "Billing", "Legal", "Other"])
    priority = detect_priority(request.message)
    summary = summarize(request.message, max_length=150)
    routed_to = route_ticket(category)
    escalation = check_escalation(priority)
    response_data = {
        "summary": summary,
        "category": category,
        "priority": priority,
        "routed_to": routed_to,
        "escalation": escalation,
        "confidence": 0.8,
        "processing_time": None,
        "task_id": task_id
    }
    return versioned_response(api_version, response_data)

@agent.app.post("/analyze_async")
async def analyze_complaint_async(
    request: TextRequest,
    tenant: TenantConfig = Depends(get_current_tenant),
    api_version: str = Depends(get_api_version)
):
    # Submit task to Celery using minimal interface
    task_id = task_manager.submit_task(analyze_complaint_task, request.message, request.customer_id)
    return {
        "task_id": task_id,
        "status": "processing",
        "message": "Complaint analysis started"
    }

@agent.app.post("/analyze_batch")
async def analyze_complaints_batch(
    requests: list[TextRequest],
    tenant: TenantConfig = Depends(get_current_tenant),
    api_version: str = Depends(get_api_version)
):
    # Use batch_process utility for batch submission
    items = [(r.message, r.customer_id) for r in requests]
    task_ids = batch_process(celery_app, analyze_complaint_task, items)
    return {
        "task_ids": task_ids,
        "status": "processing",
        "message": f"Batch analysis started for {len(requests)} complaints"
    }

@agent.app.post("/tool-example")
async def tool_example(file_path: str):
    """Demonstrate calling a tool from the registry (e.g., read a file)."""
    result = tool_registry.execute_tool("read_file", file_path=file_path)
    return {"content": result.result.get("content", "No content or file not found.")}

class OrchestrateRequest(BaseModel):
    prompt: str

@agent.app.post("/orchestrate")
async def orchestrate_workflow(request: OrchestrateRequest):
    """
    Demonstrate agentic orchestration: turn a prompt into a multi-step tool workflow.
    For example, 'Read the README file and summarize it.' will read the main project README.md and summarize its content.
    """
    orchestrator = create_orchestrator()
    result = orchestrator.execute_prompt(request.prompt)
    return {"workflow_result": result}

@agent.app.get('/test-error')
@log_api_error
def test_error_endpoint(request: Request):
    user = request.headers.get('x-user', 'test-user')
    request_id = request.headers.get('x-request-id', 'test-req')
    raise ValueError('This is a test error for logging.')

# Register tenant management endpoints
agent.app.include_router(tenant_router)

# Setup metrics (if needed)
setup_metrics(agent.app)

# Serve the UI from /ui
ui_path = os.path.join(os.path.dirname(__file__), "ui")
agent.app.mount("/ui", StaticFiles(directory=ui_path, html=True), name="ui")

# Get the FastAPI app instance (do this LAST)
app = agent.get_app()