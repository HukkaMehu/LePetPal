"""
Celery application configuration for background tasks.
"""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "dog_monitor",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.clip_processor"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=240,  # 4 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)
