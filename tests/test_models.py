import pytest
from agentspring.models import (
    BaseRequest, BaseResponse, TextRequest, ClassificationRequest, ClassificationResponse,
    SummarizationRequest, SummarizationResponse, PriorityRequest, PriorityResponse,
    BatchRequest, BatchResponse, InputValidator, TaskResult, BatchResult, SentimentResponse, ExtractionResponse
)
from pydantic import ValidationError

def test_base_request_valid():
    req = BaseRequest(customer_id="abc123")
    assert req.customer_id == "abc123"

def test_base_request_invalid():
    with pytest.raises(ValidationError):
        BaseRequest(customer_id="bad id!")

def test_text_request_valid():
    req = TextRequest(customer_id="abc123", message="Hello world!")
    assert req.message == "Hello world!"

def test_text_request_invalid():
    with pytest.raises(ValidationError):
        TextRequest(customer_id="abc123", message="<script>alert(1)</script>")

def test_classification_response():
    resp = ClassificationResponse(status="ok", timestamp="now", category="A", confidence=0.9, alternatives=None, processing_time=None)
    assert resp.category == "A"

def test_input_validator():
    assert InputValidator.sanitize_text('<b>hi</b>') == 'bhi/b'
    assert InputValidator.validate_email('a@b.com')
    assert not InputValidator.validate_email('bad-email')
    assert InputValidator.validate_phone('+12345678901')
    masked = InputValidator.mask_sensitive_data('Card: 1234 5678 9012 3456')
    assert '****' in masked 