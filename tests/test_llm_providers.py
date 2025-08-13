"""
Tests for LLM Providers
"""
import asyncio
import json
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest_asyncio
from tenacity import stop_after_attempt
from agentspring.llm import LLMRegistry

@pytest.fixture
def mock_response():
    """Mock response for testing"""
    response = MagicMock()
    response.status = 200
    response.json.return_value = {"response": "Test response"}
    return response

@pytest.fixture
def mock_rate_limit_response():
    """Mock rate limit response"""
    response = MagicMock()
    response.status = 429
    response.headers = {"Retry-After": "60"}
    return response

@pytest.fixture
def mock_session(mock_response):
    """Mock aiohttp session"""
    session = AsyncMock()
    session.__aenter__.return_value = session
    session.__aexit__.return_value = None
    session.post.return_value.__aenter__.return_value = mock_response
    return session


# def test_llm_registry():
#     """Test LLM registry functionality"""
#     # Test getting the default provider
#     provider = LLMRegistry.get_provider()
#     assert provider is not None
#     assert isinstance(provider, LLMRegistry._providers["ollama"])
    
    # Test listing providers
    providers = LLMRegistry.list_providers()
    assert "ollama" in providers
    
    # Test getting a non-existent provider
    with pytest.raises(ValueError) as exc_info:
        LLMRegistry.get_provider("non_existent")
    assert "Unknown LLM provider" in str(exc_info.value)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
