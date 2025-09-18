import os
from celery import Celery
from .config import settings
celery_app = Celery("agentspring", broker=os.getenv("CELERY_BROKER_URL", settings.REDIS_URL), backend=os.getenv("CELERY_RESULT_BACKEND", settings.REDIS_URL))
celery_app.conf.update(task_serializer="json", result_serializer="json", accept_content=["json"], task_time_limit=180, worker_prefetch_multiplier=1)
