"""
Celery configuration for distributed task processing
"""
import os
from celery import Celery
from celery.utils.log import get_task_logger
from agentspring.logging_config import setup_logging
import logging
import socket

# Sentry integration
import sentry_sdk
SENTRY_DSN = os.getenv('SENTRY_DSN')
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=0.0)

# Check if Redis is running before starting Celery
BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
try:
    sock = socket.create_connection(('localhost', 6379), timeout=2)
    sock.close()
except Exception:
    raise RuntimeError('Redis server is not running on localhost:6379. Please start Redis to use Celery.')

CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

celery_app = Celery('agentspring', broker=BROKER_URL, backend=CELERY_RESULT_BACKEND)
celery_app.conf.update(
    imports=['agentspring.tasks']
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hour
)

logger = setup_logging()

from celery import signals

@signals.task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, einfo=None, **other):
    user = kwargs.get('user', 'unknown') if kwargs else 'unknown'
    logger.error(
        f"Celery task error: {str(exception)}",
        extra={
            'user': user,
            'request_id': task_id,
            'error_type': type(exception).__name__
        }
    )
    if SENTRY_DSN:
        sentry_sdk.capture_exception(exception) 
