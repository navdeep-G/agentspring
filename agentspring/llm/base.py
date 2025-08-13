"""
Base LLM Provider Interface

This module defines the base classes and interfaces for LLM providers.
"""
import asyncio
import functools
import inspect
import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, Optional, TypeVar, Union

from pydantic import BaseModel, Field
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)

T = TypeVar('T')

class RateLimitConfig(BaseModel):
    """Configuration for rate limiting"""
    requests_per_minute: int = 60
    max_concurrent: int = 10
    retry_after: int = 60  # seconds to wait when rate limited

class ProviderConfig(BaseModel):
    """Base configuration for LLM providers"""
    timeout: int = Field(30, description="Request timeout in seconds")
    max_retries: int = Field(3, description="Maximum number of retries on failure")
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    validate_input: bool = Field(True, description="Validate input before processing")
    
    class Config:
        extra = "allow"  # Allow provider-specific configs

class LLMError(Exception):
    """Base exception for LLM provider errors"""
    def __init__(self, message: str, status_code: int = 500, **kwargs):
        self.status_code = status_code
        self.details = kwargs
        super().__init__(message)

class RateLimitError(LLMError):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str, retry_after: int = 60, **kwargs):
        super().__init__(message, status_code=429, retry_after=retry_after, **kwargs)
        self.retry_after = retry_after

class LLMProvider(ABC):
    """Base class for LLM providers with built-in error handling and retries"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize with provider configuration"""
        self.config = ProviderConfig(**(config or {}))
        self._semaphore = asyncio.Semaphore(self.config.rate_limit.max_concurrent)
        self._last_request_time = 0
        self._request_count = 0
        self._rate_limit_reset = time.time()
        
        # Initialize logging context
        self.logger = logging.getLogger(f"llm.provider.{self.__class__.__name__.lower()}")
    
    def _log_request(self, method: str, **kwargs) -> None:
        """Log request details"""
        self.logger.debug(
            "LLM request",
            extra={
                "method": method,
                "provider": self.__class__.__name__,
                **{k: v for k, v in kwargs.items() if not isinstance(v, (bytes, str)) or len(str(v)) < 100}
            }
        )
    
    def _log_response(self, method: str, response: Any, **kwargs) -> None:
        """Log response details"""
        self.logger.debug(
            "LLM response",
            extra={
                "method": method,
                "provider": self.__class__.__name__,
                "response_type": type(response).__name__,
                **kwargs
            }
        )
    
    def _handle_error(self, error: Exception, method: str, **kwargs) -> None:
        """Handle and log errors"""
        error_type = error.__class__.__name__
        error_msg = str(error)
        
        self.logger.error(
            f"LLM {method} failed: {error_type} - {error_msg}",
            exc_info=error,
            extra={
                "provider": self.__class__.__name__,
                "error_type": error_type,
                **kwargs
            }
        )
        
        if isinstance(error, RateLimitError):
            self._rate_limit_reset = time.time() + error.retry_after
            raise RateLimitError(
                f"Rate limit exceeded. Retry after {error.retry_after} seconds",
                retry_after=error.retry_after
            ) from error
            
        raise LLMError(f"LLM {method} failed: {error_msg}") from error
    
    def _validate_input(self, prompt: str, **kwargs) -> None:
        """Validate input before processing"""
        if not self.config.validate_input:
            return
            
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt must be a non-empty string")
            
        if len(prompt) > 1000000:  # 1M characters
            raise ValueError("Prompt is too long")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type()
    )
    async def _rate_limited_call(self, func: callable, *args, **kwargs) -> Any:
        """Execute a function with rate limiting"""
        async with self._semaphore:
            # Check rate limit
            now = time.time()
            if now > self._rate_limit_reset:
                self._request_count = 0
                self._rate_limit_reset = now + 60  # Reset counter after 1 minute
            
            # Calculate minimum time between requests to respect rate limit
            min_interval = 60.0 / self.config.rate_limit.requests_per_minute
            elapsed = now - self._last_request_time
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
            
            # Execute the function
            try:
                self._last_request_time = time.time()
                self._request_count += 1
                
                if inspect.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(
                        None, functools.partial(func, *args, **kwargs)
                    )
            except Exception as e:
                self._handle_error(e, func.__name__, **kwargs)
    
    @abstractmethod
    async def generate_async(self, prompt: str, **kwargs) -> str:
        """Generate text asynchronously"""
        pass
    
    @abstractmethod
    async def stream_async(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream text asynchronously"""
        pass
    
    # Synchronous wrappers for backward compatibility
    def generate(self, prompt: str, **kwargs) -> str:
        """Synchronous wrapper for generate_async"""
        try:
            self._validate_input(prompt, **kwargs)
            self._log_request("generate", prompt=prompt[:100] + '...' if len(prompt) > 100 else prompt, **kwargs)
            
            # Run the async function in the event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an event loop, create a new one
                new_loop = asyncio.new_event_loop()
                try:
                    result = new_loop.run_until_complete(
                        self._rate_limited_call(self.generate_async, prompt, **kwargs)
                    )
                finally:
                    new_loop.close()
            else:
                result = loop.run_until_complete(
                    self._rate_limited_call(self.generate_async, prompt, **kwargs)
                )
                
            self._log_response("generate", result)
            return result
        except Exception as e:
            self._handle_error(e, "generate", prompt=prompt, **kwargs)
    
    def stream(self, prompt: str, **kwargs) -> Any:
        """Synchronous wrapper for stream_async"""
        class SyncStreamWrapper:
            def __init__(self, async_gen):
                self.async_gen = async_gen
                self._loop = asyncio.new_event_loop()
                self._queue = asyncio.Queue()
                self._task = self._loop.create_task(self._run())
            
            async def _run(self):
                try:
                    async for chunk in self.async_gen:
                        await self._queue.put((None, chunk))
                    await self._queue.put((None, StopIteration))
                except Exception as e:
                    await self._queue.put((e, None))
            
            def __iter__(self):
                return self
            
            def __next__(self):
                if not self._task.done() and self._queue.empty():
                    # Process events until we get a result
                    self._loop.run_until_complete(asyncio.wait([self._queue.get()], timeout=30))
                
                if not self._queue.empty():
                    error, result = self._queue.get_nowait()
                    if error:
                        raise error
                    if result is StopIteration:
                        raise StopIteration
                    return result
                
                # If we get here, the queue is empty but the task isn't done
                if self._task.done():
                    try:
                        self._task.result()  # This will raise any exceptions
                    except Exception as e:
                        raise LLMError(f"Streaming error: {str(e)}") from e
                    raise StopIteration
                
                raise TimeoutError("Timeout waiting for next chunk")
            
            def __del__(self):
                if not self._task.done():
                    self._task.cancel()
                self._loop.close()
        
        try:
            self._validate_input(prompt, **kwargs)
            self._log_request("stream", prompt=prompt[:100] + '...' if len(prompt) > 100 else prompt, **kwargs)
            
            # Run the async function in the event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an event loop, create a new one
                new_loop = asyncio.new_event_loop()
                try:
                    async_gen = self._rate_limited_call(self.stream_async, prompt, **kwargs)
                    return SyncStreamWrapper(async_gen)
                except Exception as e:
                    new_loop.close()
                    raise
            else:
                async_gen = loop.run_until_complete(
                    self._rate_limited_call(self.stream_async, prompt, **kwargs)
                )
                return SyncStreamWrapper(async_gen)
                
        except Exception as e:
            self._handle_error(e, "stream", prompt=prompt, **kwargs)
