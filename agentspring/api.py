"""
API Helpers for AgentSpring
"""
import os
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from fastapi import FastAPI, HTTPException, status, Header, Depends, APIRouter
from fastapi.responses import JSONResponse
import redis  # type: ignore
from agentspring.tasks import AsyncTaskManager

logger = logging.getLogger(__name__)

class MetricsTracker:
    """Track API metrics in Redis"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
        self.redis_client = redis.Redis.from_url(self.redis_url)
    
    def track_request(self, success: bool, response_time: float, endpoint: str = "unknown"):
        """Track a single request"""
        try:
            # Increment total requests
            self.redis_client.incr("metrics:total_requests")
            
            # Increment success/failure counters
            if success:
                self.redis_client.incr("metrics:successful_requests")
            else:
                self.redis_client.incr("metrics:failed_requests")
            
            # Track response time (rolling average)
            response_times_key = "metrics:response_times"
            self.redis_client.lpush(response_times_key, response_time)
            self.redis_client.ltrim(response_times_key, 0, 99)  # Keep last 100 times
            
            # Track endpoint-specific metrics
            self.redis_client.incr(f"metrics:endpoint:{endpoint}:total")
            if success:
                self.redis_client.incr(f"metrics:endpoint:{endpoint}:success")
            else:
                self.redis_client.incr(f"metrics:endpoint:{endpoint}:failed")
            
            # Track hourly metrics
            current_hour = datetime.now().strftime("%Y-%m-%d-%H")
            self.redis_client.incr(f"metrics:hourly:{current_hour}:total")
            if success:
                self.redis_client.incr(f"metrics:hourly:{current_hour}:success")
            else:
                self.redis_client.incr(f"metrics:hourly:{current_hour}:failed")
                
        except Exception as e:
            logger.error(f"Error tracking metrics: {e}")
    
    def get_average_response_time(self) -> float:
        """Calculate average response time from Redis"""
        try:
            response_times = self.redis_client.lrange("metrics:response_times", 0, -1)
            if response_times:
                times = [float(t) for t in response_times]
                return sum(times) / len(times)
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating average response time: {e}")
            return 0.0

class AuthMiddleware:
    """API Key authentication middleware"""
    
    def __init__(self, api_key_env: str = "API_KEY", default_key: str = "demo-key"):
        self.api_key = os.getenv(api_key_env, default_key)
    
    def __call__(self, x_api_key: str = Header(...)):
        if x_api_key != self.api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid API Key"
            )
        return x_api_key

class HealthEndpoint:
    """Standard health check endpoint"""
    
    def __init__(self, app: FastAPI, metrics_tracker: Optional[MetricsTracker] = None):
        self.app = app
        self.metrics_tracker = metrics_tracker
        self._setup_health_endpoint()
    
    def _setup_health_endpoint(self):
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            start_time = time.time()
            
            try:
                # Check Redis connection if metrics tracker is available
                if self.metrics_tracker:
                    self.metrics_tracker.redis_client.ping()
                
                processing_time = time.time() - start_time
                
                # Track metrics if available
                if self.metrics_tracker:
                    self.metrics_tracker.track_request(True, processing_time, "health")
                
                return {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "redis": "connected" if self.metrics_tracker else "not_configured",
                    "response_time": processing_time
                }
            except Exception as e:
                processing_time = time.time() - start_time
                
                if self.metrics_tracker:
                    self.metrics_tracker.track_request(False, processing_time, "health")
                
                raise HTTPException(status_code=503, detail="Service unhealthy")

class FastAPIAgent:
    """Base FastAPI agent class with common functionality"""
    
    def __init__(self, title: str = "AgentSpring Agent", api_key_env: str = "API_KEY"):
        self.app = FastAPI(title=title)
        self.metrics_tracker = MetricsTracker()
        self.auth_middleware = AuthMiddleware(api_key_env)
        self.health_endpoint = HealthEndpoint(self.app, self.metrics_tracker)
        
        # Setup common middleware and error handlers
        self._setup_error_handlers()
    
    def _setup_error_handlers(self):
        """Setup common error handlers"""
        
        @self.app.exception_handler(Exception)
        async def global_exception_handler(request, exc):
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "detail": str(exc),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def endpoint(self, path: str, **kwargs):
        """Decorator to add endpoints with automatic metrics tracking"""
        def decorator(func: Callable):
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    processing_time = time.time() - start_time
                    self.metrics_tracker.track_request(True, processing_time, path)
                    return result
                except Exception as e:
                    processing_time = time.time() - start_time
                    self.metrics_tracker.track_request(False, processing_time, path)
                    raise
            
            # Register the endpoint
            self.app.add_api_route(path, wrapper, **kwargs)
            return wrapper
        return decorator
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI app instance"""
        return self.app 

def standard_endpoints(app: FastAPI, task_manager: AsyncTaskManager, batch_func: Optional[Callable] = None):
    """
    Register standard async and batch endpoints to the app.
    - /task/{task_id}: Get async task status
    - /batch: Submit a batch of items (if batch_func provided)
    """
    router = APIRouter()

    @router.get("/task/{task_id}")
    async def get_task_status(task_id: str):
        return task_manager.get_task_status(task_id)

    if batch_func:
        @router.post("/batch")
        async def submit_batch(items: list):
            task_id = batch_func(items)
            return {"task_id": task_id, "status": "processing"}

    app.include_router(router) 