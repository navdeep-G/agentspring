"""
Base Models and Validation for AgentSpring
"""

import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class BaseRequest(BaseModel):
    """Base request model with common fields"""

    customer_id: str = Field(
        ..., min_length=3, max_length=64, description="Customer identifier"
    )

    @field_validator("customer_id")
    @classmethod
    def customer_id_safe(cls, v):
        """Validate customer ID is alphanumeric"""
        if not v.isalnum():
            raise ValueError("customer_id must be alphanumeric")
        return v


class BaseResponse(BaseModel):
    """Base response model with common fields"""

    status: str = Field(..., description="Response status")
    timestamp: str = Field(..., description="ISO timestamp")
    processing_time: Optional[float] = Field(
        None, description="Processing time in seconds"
    )


class TextRequest(BaseRequest):
    """Request model for text processing"""

    message: str = Field(
        ..., min_length=5, max_length=2000, description="Text to process"
    )

    @field_validator("message")
    @classmethod
    def message_safe(cls, v):
        """Validate message doesn't contain unsafe content"""
        unsafe_patterns = [
            "<script",
            "</",
            "\\",
            "eval(",
            "import os",
            "rm -rf",
        ]
        if any(pattern in v for pattern in unsafe_patterns):
            raise ValueError("message contains unsafe content")
        return v


class ClassificationRequest(TextRequest):
    """Request model for classification tasks"""

    categories: Optional[List[str]] = Field(
        None, description="Available categories"
    )


class ClassificationResponse(BaseResponse):
    """Response model for classification tasks"""

    category: str = Field(..., description="Classified category")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Classification confidence"
    )
    alternatives: Optional[List[str]] = Field(
        None, description="Alternative categories"
    )


class SummarizationRequest(TextRequest):
    """Request model for summarization tasks"""

    max_length: Optional[int] = Field(
        100, ge=10, le=1000, description="Maximum summary length"
    )


class SummarizationResponse(BaseResponse):
    """Response model for summarization tasks"""

    summary: str = Field(..., description="Generated summary")
    original_length: int = Field(..., description="Original text length")
    summary_length: int = Field(..., description="Summary length")


class PriorityRequest(TextRequest):
    """Request model for priority detection"""

    priorities: Optional[List[str]] = Field(
        None, description="Available priority levels"
    )


class PriorityResponse(BaseResponse):
    """Response model for priority detection"""

    priority: str = Field(..., description="Detected priority level")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Priority confidence"
    )


class BatchRequest(BaseModel):
    """Request model for batch processing"""

    items: List[Dict[str, Any]] = Field(
        ..., min_items=1, max_items=100, description="Items to process"
    )

    @field_validator("items")
    @classmethod
    def validate_items(cls, v):
        """Validate batch items"""
        if len(v) > 100:
            raise ValueError("Batch size cannot exceed 100 items")
        return v


class BatchResponse(BaseResponse):
    """Response model for batch processing"""

    task_id: str = Field(..., description="Batch task identifier")
    total_items: int = Field(..., description="Total number of items")
    status: str = Field(..., description="Batch processing status")


class InputValidator:
    """Utility class for input validation"""

    @staticmethod
    def sanitize_text(text: str) -> str:
        """Sanitize text input"""
        # Remove potentially dangerous characters
        text = re.sub(r'[<>"\']', "", text)
        return text.strip()

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        pattern = r"^\+?1?\d{9,15}$"
        return bool(re.match(pattern, phone))

    @staticmethod
    def mask_sensitive_data(
        text: str, pattern: str = r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"
    ) -> str:
        """Mask sensitive data like credit card numbers"""
        return re.sub(pattern, "****-****-****-****", text)


class TaskResult(BaseModel):
    """Standard async task result model"""

    task_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None
    timestamp: float


class BatchResult(BaseModel):
    """Standard batch result model"""

    task_id: str
    status: str
    total_items: int
    results: List[dict]
    processing_time: Optional[float] = None
    timestamp: float


class SentimentResponse(BaseResponse):
    """Response model for sentiment analysis"""

    sentiment: str = Field(
        ..., description="Detected sentiment (positive, neutral, negative)"
    )
    confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Sentiment confidence"
    )


class ExtractionResponse(BaseResponse):
    """Response model for structured data extraction"""

    data: dict = Field(..., description="Extracted structured data")
