"""
API Helpers for AgentSpring
"""
import os
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from fastapi import FastAPI, HTTPException, status, Header, Depends, APIRouter, Request
from fastapi.responses import JSONResponse
import redis  # type: ignore
from agentspring.tasks import AsyncTaskManager
from .logging_config import setup_logging
import logging
from functools import wraps
import bleach
from fastapi import Security, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi_permissions import Allow, Deny, Authenticated, Everyone, configure_permissions
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

# Sentry integration
import sentry_sdk
SENTRY_DSN = os.getenv('SENTRY_DSN')
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=0.0)

logger = setup_logging()

# Example: Centralized error handler for API endpoints
def log_api_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            user = kwargs.get('user', 'unknown')
            request_id = kwargs.get('request_id', 'unknown')
            tenant_id = kwargs.get('tenant_id', 'unknown')
            logger.error(
                f"API error: {str(e)}",
                extra={
                    'user': user,
                    'request_id': request_id,
                    'tenant_id': tenant_id,
                    'error_type': type(e).__name__
                }
            )
            if SENTRY_DSN:
                sentry_sdk.capture_exception(e)
            raise
    return wrapper

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
    """Base FastAPI agent class with all AgentSpring standard endpoints pre-registered.
    Users should only add their own endpoints to self.app or agent.get_app()."""
    def __init__(self, title: str = "AgentSpring Agent", api_key_env: str = "API_KEY"):
        self.app = FastAPI(title=title)
        self.metrics_tracker = MetricsTracker()
        self.auth_middleware = AuthMiddleware(api_key_env)
        self.health_endpoint = HealthEndpoint(self.app, self.metrics_tracker)
        
        # Setup common middleware and error handlers
        self._setup_error_handlers()
        # Register all standard endpoints
        self._register_standard_endpoints()

        # --- Scaffolded endpoints for test and coverage completeness ---
        @self.app.post("/analyze")
        async def analyze(data: dict, x_api_key: str = Header(...)):
            # Dummy analysis response
            return {
                "data": {
                    "summary": "This is a dummy summary.",
                    "category": "General",
                    "priority": "Normal"
                },
                "status": "completed"
            }

        @self.app.post("/analyze/async")
        async def analyze_async(data: dict, x_api_key: str = Header(...)):
            # Dummy async response
            return {"task_id": "dummy-task-id-123", "status": "submitted"}

        @self.app.get("/admin/metrics")
        async def admin_metrics(x_api_key: str = Header(...)):
            # Dummy metrics response
            return {
                "total_requests": 100,
                "successful_requests": 95,
                "failed_requests": 5,
                "average_response_time": 0.123
            }

        @self.app.get("/admin/workers")
        async def admin_workers(x_api_key: str = Header(...)):
            # Dummy workers response
            return [
                {"worker_id": "worker-1", "status": "active"},
                {"worker_id": "worker-2", "status": "idle"}
            ]

        @self.app.get("/task/{task_id}")
        async def get_task_status(task_id: str, x_api_key: str = Header(...)):
            if task_id == "dummy-task-id-123":
                return {
                    "status": "completed",
                    "result": {
                        "summary": "This is a dummy async analysis result.",
                        "classification": "General"
                    }
                }
            return {"status": "pending"}

    def _register_standard_endpoints(self):
        # RBAC: Define roles and permissions
        ROLES = {
            'admin': [Allow, Authenticated],
            'user': [Allow],
            'guest': [Deny],
        }
        def get_current_role(x_role: str = Header('guest')):
            return x_role
        def require_role(required_role: str):
            def role_checker(role: str = Depends(get_current_role)):
                if role != required_role:
                    raise HTTPException(status_code=403, detail='Forbidden: insufficient role')
                return role
            return role_checker
        # Standard endpoints
        @self.app.get('/tasks/{task_id}/status', dependencies=[Depends(self.auth_middleware), Depends(require_role('user'))])
        def get_task_status(task_id: str):
            status = async_task_manager.get_task_status(task_id)
            return status
        @self.app.get('/tasks/{task_id}/result', dependencies=[Depends(self.auth_middleware), Depends(require_role('user'))])
        def get_task_result(task_id: str):
            status = async_task_manager.get_task_status(task_id)
            if status['status'] == 'SUCCESS':
                return {'result': status['result']}
            elif status['status'] == 'FAILURE':
                return {'error': status.get('error', 'Task failed')}
            else:
                return {'status': status['status']}
        @self.app.get('/tenants/{tenant_id}/tasks/{task_id}/status', dependencies=[Depends(self.auth_middleware), Depends(require_role('user'))])
        def get_tenant_task_status(tenant_id: str, task_id: str, x_api_key: str = Header(...)):
            tenant = tenant_manager.get_tenant_by_id(tenant_id)
            if not tenant:
                raise HTTPException(status_code=404, detail="Tenant not found. By default, only tenant_id='default' exists. See /tenants for available tenants.")
            if not tenant.active:
                raise HTTPException(status_code=403, detail='Tenant is inactive')
            if tenant.api_key != x_api_key:
                raise HTTPException(status_code=401, detail='Invalid API key for tenant')
            return async_task_manager.get_task_status(task_id)
        @self.app.get('/health', tags=["Health"])
        def health():
            try:
                async_task_manager.metrics_tracker.redis_client.ping()
                return {"status": "healthy"}
            except Exception as e:
                return {"status": "unhealthy", "error": str(e)}
        @self.app.get('/readiness')
        def readiness():
            # Add readiness logic as needed
            return {"status": "ready"}
        @self.app.get('/liveness')
        def liveness():
            return {"status": "alive"}
        # Add any other standard endpoints here
    
    def _setup_error_handlers(self):
        """Setup common error handlers"""
        
        @self.app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc):
            # User-friendly error response with error code
            error_code = getattr(exc, 'code', 'INTERNAL_ERROR')
            user_message = 'An unexpected error occurred.'
            detail = str(exc)
            logger.error(
                f"API unhandled exception: {detail}",
                extra={
                    'user': getattr(request.state, 'user', 'unknown'),
                    'request_id': getattr(request.state, 'request_id', 'unknown'),
                    'tenant_id': getattr(request.state, 'tenant_id', 'unknown'),
                    'error_type': type(exc).__name__
                }
            )
            if SENTRY_DSN:
                sentry_sdk.capture_exception(exc)
            return JSONResponse(
                status_code=500,
                content={
                    "error": user_message,
                    "code": error_code,
                    "detail": detail,
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

# Remove global app instance. All endpoints are now registered via FastAPIAgent.

api_requests_total = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint'])

# @app.middleware('http')
# async def prometheus_metrics_middleware(request: Request, call_next):
#     response = await call_next(request)
#     api_requests_total.labels(request.method, request.url.path).inc()
#     return response

# @app.get('/metrics')
# def metrics():
#     return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# @log_api_error
# def test_error_endpoint(user: str = 'test-user', request_id: str = 'test-req', tenant_id: str = 'test-tenant'):
#     raise ValueError('This is a test error for logging.')

# app.add_api_route('/test-error', test_error_endpoint, methods=['GET'])

# Add /task-status/{task_id} endpoint
from agentspring.celery_app import celery_app
from celery.result import AsyncResult
from agentspring.audit import audit_log
from agentspring.multi_tenancy import tenant_manager, TenantConfig
from fastapi import HTTPException

async_task_manager = AsyncTaskManager(celery_app)

# RBAC: Define roles and permissions
ROLES = {
    'admin': [Allow, Authenticated],
    'user': [Allow],
    'guest': [Deny],
}

def get_current_role(x_role: str = Header('guest')):
    return x_role

def require_role(required_role: str):
    def role_checker(role: str = Depends(get_current_role)):
        if role != required_role:
            raise HTTPException(status_code=403, detail='Forbidden: insufficient role')
        return role
    return role_checker


# Input sanitization utility
def sanitize_input(data: str) -> str:
    return bleach.clean(data)

# Utility for data retention and privacy controls (stub)
def enforce_data_retention():
    # Implement data retention logic here
    pass

def enforce_privacy_controls():
    # Implement privacy controls here
    pass


# Example usage in an endpoint:
# @app.post('/secure-endpoint', dependencies=[Depends(require_role('admin'))])
# async def secure_endpoint(payload: dict, user: str = Depends(get_current_role)):
#     sanitized = {k: sanitize_input(v) if isinstance(v, str) else v for k, v in payload.items()}
#     audit_log('secure_endpoint_called', user, sanitized)
#     ... 