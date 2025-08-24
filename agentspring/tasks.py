"""
Task Processing Helpers for AgentSpring
"""

import asyncio
import logging
import time
import uuid
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

from celery import (
    Celery,  # type: ignore
    shared_task,
)
from pydantic import BaseModel

from agentspring.task_base import (
    AsyncTaskManager,
    agentspring_task,
    batch_process,
)

logger = logging.getLogger(__name__)


class AsyncTaskManager:
    """Manage async task processing with Celery"""

    def __init__(self, celery_app: Celery):
        self.celery_app = celery_app

    def submit_task(self, task_func: Callable, *args, **kwargs) -> str:
        """Submit a task and return task ID"""
        try:
            task = task_func.delay(*args, **kwargs)
            return task.id
        except Exception as e:
            logger.error(f"Failed to submit task: {e}")
            raise

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status and result"""
        try:
            task = self.celery_app.AsyncResult(task_id)
            result = {
                "task_id": task_id,
                "status": task.status,
                "result": task.result if task.ready() else None,
            }
            return result
        except Exception as e:
            logger.error(f"Failed to get task status: {e}")
            return {"task_id": task_id, "status": "ERROR", "error": str(e)}

    def wait_for_task(
        self, task_id: str, timeout: int = 300
    ) -> Dict[str, Any]:
        """Wait for task completion with timeout"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = self.get_task_status(task_id)
            if result["status"] in ["SUCCESS", "FAILURE"]:
                return result
            time.sleep(1)

        return {
            "task_id": task_id,
            "status": "TIMEOUT",
            "error": f"Task timed out after {timeout} seconds",
        }

    async def wait_for_task_async(
        self, task_id: str, timeout: int = 300
    ) -> Dict[str, Any]:
        """Async wait for task completion with timeout (non-blocking)."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = self.get_task_status(task_id)
            if result["status"] in ["SUCCESS", "FAILURE"]:
                return result
            await asyncio.sleep(1)
        return {
            "task_id": task_id,
            "status": "TIMEOUT",
            "error": f"Task timed out after {timeout} seconds",
        }

    async def wait_for_tasks_async(
        self, task_ids: List[str], timeout: int = 300
    ) -> List[Dict[str, Any]]:
        """Async wait for multiple tasks concurrently."""
        tasks = [
            self.wait_for_task_async(task_id, timeout) for task_id in task_ids
        ]
        return await asyncio.gather(*tasks)


class BatchProcessor:
    """Process multiple items in batch"""

    def __init__(self, celery_app: Celery, batch_task_func: Callable):
        self.celery_app = celery_app
        self.batch_task_func = batch_task_func

    def submit_batch(self, items: List[Dict[str, Any]]) -> str:
        """Submit a batch of items for processing"""
        try:
            task = self.batch_task_func.delay(items)
            return task.id
        except Exception as e:
            logger.error(f"Failed to submit batch: {e}")
            raise

    def process_batch_sync(
        self, items: List[Dict[str, Any]], processor_func: Callable
    ) -> List[Dict[str, Any]]:
        """Process batch synchronously (for small batches)"""
        results = []
        for item in items:
            try:
                result = processor_func(item)
                results.append(
                    {"item": item, "result": result, "status": "success"}
                )
            except Exception as e:
                results.append(
                    {"item": item, "error": str(e), "status": "failed"}
                )
        return results


class TaskResult(BaseModel):
    """Standard task result model"""

    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None
    timestamp: float = time.time()


class BatchResult(BaseModel):
    """Standard batch result model"""

    task_id: str
    status: str
    total_items: int
    results: List[Dict[str, Any]]
    processing_time: Optional[float] = None
    timestamp: float = time.time()


def agentspring_task(
    max_retries: int = 3, progress_steps: Optional[list] = None
):
    """
    Decorator for Celery tasks to handle retries, progress, and standardized results.
    Usage:
        @celery_app.task(bind=True, name="my_task")
        @agentspring_task(max_retries=3)
        def my_task(self, ...):
            ...
    """

    def decorator(task_func):
        @wraps(task_func)
        def wrapper(self, *args, **kwargs):
            start_time = time.time()
            task_id = getattr(self.request, "id", str(uuid.uuid4()))
            try:
                # Progress: initial state
                if progress_steps:
                    self.update_state(
                        state="PROGRESS",
                        meta={
                            "task_id": task_id,
                            "status": progress_steps[0],
                            "current": 0,
                            "total": len(progress_steps),
                        },
                    )
                else:
                    self.update_state(
                        state="PROGRESS",
                        meta={
                            "task_id": task_id,
                            "status": "processing",
                            "current": 0,
                            "total": 100,
                        },
                    )

                # Retry logic
                for attempt in range(max_retries):
                    try:
                        result = task_func(self, *args, **kwargs)
                        processing_time = time.time() - start_time
                        return TaskResult(
                            task_id=task_id,
                            status="completed",
                            result=result,
                            processing_time=processing_time,
                            timestamp=time.time(),
                        ).model_dump()
                    except Exception as e:
                        if attempt == max_retries - 1:
                            raise e
                        logger.warning(
                            f"Task {task_func.__name__} failed, attempt {attempt + 1}/{max_retries}: {e}"
                        )
                        time.sleep(2**attempt)
            except Exception as e:
                processing_time = time.time() - start_time
                logger.error(f"Task {task_func.__name__} failed: {e}")
                return TaskResult(
                    task_id=task_id,
                    status="failed",
                    error=str(e),
                    processing_time=processing_time,
                    timestamp=time.time(),
                ).model_dump()

        return wrapper

    return decorator


def batch_process(
    celery_app: Celery,
    single_task_func: Callable,
    items: List[Any],
    wait: bool = False,
    timeout: int = 300,
) -> List[Any]:
    """
    Submit a batch of items to a single-item Celery task. Returns a list of task IDs or results if wait=True.
    Example:
        task_ids = batch_process(celery_app, analyze_complaint_task, complaints)
        results = batch_process(celery_app, analyze_complaint_task, complaints, wait=True)
    """
    task_ids = []
    for item in items:
        task = (
            single_task_func.delay(*item)
            if isinstance(item, (list, tuple))
            else single_task_func.delay(item)
        )
        task_ids.append(task.id)
    if not wait:
        return task_ids
    # Wait for all tasks to complete
    results = []
    for task_id in task_ids:
        result = AsyncTaskManager(celery_app).wait_for_task(
            task_id, timeout=timeout
        )
        results.append(result)
    return results


@shared_task(bind=True, name="test_error_task")
def test_error_task(self, user="test-user"):
    raise RuntimeError("This is a test error for logging.")


@shared_task(name="celery_health_check")
def celery_health_check():
    return {"status": "ok"}
