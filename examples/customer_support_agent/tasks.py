"""
Celery tasks for distributed LLM processing in SupportFlow Agent
"""
import json
import time
from typing import Dict, Any, Optional
from agentspring.celery_app import celery_app, logger
from agentspring.tasks import agentspring_task, batch_process, AsyncTaskManager
from agentspring.llm import classify, detect_priority, summarize
from agentspring.models import TaskResult
from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComplaintAnalysis(BaseModel):
    """Structured output for complaint analysis"""
    classification: str = Field(description="Category of the complaint (e.g., billing, technical, service)")
    priority: str = Field(description="Priority level (low, medium, high, critical)")
    summary: str = Field(description="Brief summary of the complaint")
    suggested_action: str = Field(description="Recommended action to resolve the complaint")
    department: str = Field(description="Department that should handle this complaint")
    escalation_needed: bool = Field(description="Whether this complaint needs escalation")
    sentiment: str = Field(description="Customer sentiment (positive, neutral, negative)")

class ComplaintAnalysisResult(BaseModel):
    """Result model for complaint analysis"""
    task_id: str
    status: str
    result: Optional[ComplaintAnalysis] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None
    timestamp: float

@celery_app.task(bind=True, name="analyze_complaint")
@agentspring_task()
def analyze_complaint_task(self, complaint_text: str, customer_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Celery task to analyze customer complaints using LLM (minimal version)
    """
    # Use one-liner helpers
    category = classify(complaint_text, ["Infrastructure", "Account", "Billing", "Legal", "Other"])
    priority = detect_priority(complaint_text)
    summary = summarize(complaint_text, max_length=150)
    # Example routing/escalation logic (could be moved to agentspring)
    routed_to = {
        "Infrastructure": "DevOps Queue",
        "Account": "Customer Success",
        "Billing": "Finance Ops",
        "Legal": "Compliance",
        "Other": "General Inbox"
    }.get(category, "General Support")
    escalation = "Escalation triggered" if priority.lower() in ["critical", "high"] else "No escalation necessary"
    return {
        "summary": summary,
        "category": category,
        "priority": priority,
        "routed_to": routed_to,
        "escalation": escalation,
        "confidence": 0.8,
        "customer_id": customer_id
    }

@celery_app.task(bind=True, name="batch_analyze_complaints")
@agentspring_task()
def batch_analyze_complaints_task(self, complaints: list) -> Dict[str, Any]:
    """
    Celery task to analyze multiple complaints in batch (minimal version)
    """
    # Use batch_process utility to submit all complaints to analyze_complaint_task
    # This is a Celery task, so we can just return the list of task IDs
    task_manager = AsyncTaskManager(celery_app)
    # Each complaint should be a tuple/list of args for analyze_complaint_task
    task_ids = []
    for complaint in complaints:
        # complaint is expected to be a dict with 'text' and 'customer_id'
        args = [complaint.get("text", ""), complaint.get("customer_id")]
        task_id = analyze_complaint_task.delay(*args).id
        task_ids.append(task_id)
    return {
        "task_ids": task_ids,
        "total_complaints": len(complaints),
        "status": "queued"
    } 