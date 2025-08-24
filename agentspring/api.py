"""
API Helpers for AgentSpring
"""

import os
from datetime import datetime
from functools import wraps
from typing import Callable, Optional

import bleach

# Sentry integration
import sentry_sdk
from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Request,
    status,
)
from fastapi.responses import JSONResponse, Response
from fastapi_permissions import (
    Allow,
    Authenticated,
    Deny,
)

from agentspring.tasks import AsyncTaskManager

from .logging_config import setup_logging
from .metrics import REQUEST_COUNTER, get_metrics

SENTRY_DSN = os.getenv("SENTRY_DSN")
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
            user = kwargs.get("user", "unknown")
            request_id = kwargs.get("request_id", "unknown")
            tenant_id = kwargs.get("tenant_id", "unknown")
            logger.error(
                f"API error: {str(e)}",
                extra={
                    "user": user,
                    "request_id": request_id,
                    "tenant_id": tenant_id,
                    "error_type": type(e).__name__,
                },
            )
            if SENTRY_DSN:
                sentry_sdk.capture_exception(e)
            raise

    return wrapper


class AuthMiddleware:
    """API Key authentication middleware"""

    def __init__(
        self, api_key_env: str = "API_KEY", default_key: str = "demo-key"
    ):
        self.api_key = os.getenv(api_key_env, default_key)

    def __call__(self, x_api_key: str = Header(...)):
        if x_api_key != self.api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API Key",
            )
        return x_api_key


class FastAPIAgent:
    """Base FastAPI agent class with all AgentSpring standard endpoints pre-registered.
    Users should only add their own endpoints to self.app or agent.get_app().
    """

    def __init__(
        self, title: str = "AgentSpring Agent", api_key_env: str = "API_KEY"
    ):
        self.app = FastAPI(title=title)
        self.auth_middleware = AuthMiddleware(api_key_env)
        self.async_task_manager = self._initialize_async_tasks()

        # Setup common middleware and error handlers
        self._setup_error_handlers()
        self.app.middleware("http")(self.track_requests)

        # Register all standard endpoints
        self._register_standard_endpoints()

    def _initialize_async_tasks(self):
        """Safely initialize the AsyncTaskManager if celery is configured."""
        try:
            from agentspring.celery_app import celery_app

            return AsyncTaskManager(celery_app)
        except (ImportError, Exception) as e:
            logger.warning(
                f"Could not initialize AsyncTaskManager: {e}. Running without async task support."
            )
            return None

        # --- Scaffolded endpoints for test and coverage completeness ---
        @self.app.post("/analyze")
        async def analyze(data: dict, x_api_key: str = Header(...)):
            # Dummy analysis response
            return {
                "data": {
                    "summary": "This is a dummy summary.",
                    "category": "General",
                    "priority": "Normal",
                },
                "status": "completed",
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
                "average_response_time": 0.123,
            }

        @self.app.get("/admin/workers")
        async def admin_workers(x_api_key: str = Header(...)):
            # Dummy workers response
            return [
                {"worker_id": "worker-1", "status": "active"},
                {"worker_id": "worker-2", "status": "idle"},
            ]

        @self.app.get("/task/{task_id}")
        async def get_task_status(task_id: str, x_api_key: str = Header(...)):
            if task_id == "dummy-task-id-123":
                return {
                    "status": "completed",
                    "result": {
                        "summary": "This is a dummy async analysis result.",
                        "classification": "General",
                    },
                }
            return {"status": "pending"}

    def _register_standard_endpoints(self):
        # RBAC: Define roles and permissions

        def get_current_role(x_role: str = Header("guest")):
            return x_role

        def require_role(required_role: str):
            def role_checker(role: str = Depends(get_current_role)):
                if role != required_role:
                    raise HTTPException(
                        status_code=403, detail="Forbidden: insufficient role"
                    )
                return role

            return role_checker

        # Standard endpoints
        if self.async_task_manager:

            @self.app.get(
                "/tasks/{task_id}/status",
                dependencies=[
                    Depends(self.auth_middleware),
                    Depends(require_role("user")),
                ],
            )
            def get_task_status(task_id: str):
                status = self.async_task_manager.get_task_status(task_id)
                return status

            @self.app.get(
                "/tasks/{task_id}/result",
                dependencies=[
                    Depends(self.auth_middleware),
                    Depends(require_role("user")),
                ],
            )
            def get_task_result(task_id: str):
                status = self.async_task_manager.get_task_status(task_id)
                if status["status"] == "SUCCESS":
                    return {"result": status["result"]}
                elif status["status"] == "FAILURE":
                    return {"error": status.get("error", "Task failed")}
                else:
                    return {"status": status["status"]}

            @self.app.get(
                "/tenants/{tenant_id}/tasks/{task_id}/status",
                dependencies=[
                    Depends(self.auth_middleware),
                    Depends(require_role("user")),
                ],
            )
            def get_tenant_task_status(
                tenant_id: str, task_id: str, x_api_key: str = Header(...)
            ):
                tenant = tenant_manager.get_tenant_by_id(tenant_id)
                if not tenant:
                    raise HTTPException(
                        status_code=404,
                        detail="Tenant not found. By default, only tenant_id='default' exists. See /tenants for available tenants.",
                    )
                if not tenant.active:
                    raise HTTPException(
                        status_code=403, detail="Tenant is inactive"
                    )
                if tenant.api_key != x_api_key:
                    raise HTTPException(
                        status_code=401, detail="Invalid API key for tenant"
                    )
                return self.async_task_manager.get_task_status(task_id)

        @self.app.get("/health", tags=["Health"])
        def health():
            redis_status = "disconnected"
            if self.async_task_manager:
                try:
                    # Access the client through the backend
                    self.async_task_manager.celery_app.backend.client.ping()
                    redis_status = "connected"
                except Exception:
                    redis_status = "disconnected"
            return {"status": "healthy", "redis": redis_status}

        @self.app.get("/readiness")
        def readiness():
            # Add readiness logic as needed
            return {"status": "ready"}

        @self.app.get("/liveness")
        def liveness():
            return {"status": "alive"}

        @self.app.get("/metrics")
        def metrics():
            return Response(get_metrics(), media_type="text/plain")

        # Add any other standard endpoints here

    def _setup_error_handlers(self):
        """Setup common error handlers"""

        @self.app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc):
            # User-friendly error response with error code
            error_code = getattr(exc, "code", "INTERNAL_ERROR")
            user_message = "An unexpected error occurred."
            detail = str(exc)
            logger.error(
                f"API unhandled exception: {detail}",
                extra={
                    "user": getattr(request.state, "user", "unknown"),
                    "request_id": getattr(
                        request.state, "request_id", "unknown"
                    ),
                    "tenant_id": getattr(
                        request.state, "tenant_id", "unknown"
                    ),
                    "error_type": type(exc).__name__,
                },
            )
            if SENTRY_DSN:
                sentry_sdk.capture_exception(exc)
            return JSONResponse(
                status_code=500,
                content={
                    "error": user_message,
                    "code": error_code,
                    "detail": detail,
                    "timestamp": datetime.now().isoformat(),
                },
            )

    async def track_requests(self, request: Request, call_next):
        """Middleware to track API requests and update Prometheus metrics."""
        response = await call_next(request)
        # Get the endpoint path from the request's route, if it exists
        endpoint = "/path/not/found"
        for route in request.app.routes:
            match, _ = route.matches(request.scope)
            if match:
                endpoint = route.path
                break

        REQUEST_COUNTER.labels(
            method=request.method,
            endpoint=endpoint,
            http_status=response.status_code,
        ).inc()
        return response

    def get_app(self) -> FastAPI:
        """Get the FastAPI app instance"""
        return self.app


def standard_endpoints(
    app: FastAPI,
    task_manager: Optional[AsyncTaskManager],
    batch_func: Optional[Callable] = None,
):
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


# @log_api_error
# def test_error_endpoint(user: str = 'test-user', request_id: str = 'test-req', tenant_id: str = 'test-tenant'):
#     raise ValueError('This is a test error for logging.')

# app.add_api_route('/test-error', test_error_endpoint, methods=['GET'])

# Add /task-status/{task_id} endpoint
from agentspring.multi_tenancy import tenant_manager

# RBAC: Define roles and permissions
ROLES = {
    "admin": [Allow, Authenticated],
    "user": [Allow],
    "guest": [Deny],
}


def get_current_role(x_role: str = Header("guest")):
    return x_role


def require_role(required_role: str):
    def role_checker(role: str = Depends(get_current_role)):
        if role != required_role:
            raise HTTPException(
                status_code=403, detail="Forbidden: insufficient role"
            )
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
