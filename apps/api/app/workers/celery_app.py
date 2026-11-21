from celery import Celery
from kombu import Queue

from app.core.config import settings
from app.workers.beat import beat_schedule

celery_app = Celery(
    "freshersjobs",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    beat_schedule=beat_schedule,
    # Declared explicitly: Vercel builds Celery subscribers by introspecting
    # queues at import time. Local Redis workers use the same declarations.
    task_queues=(Queue("ingestion"), Queue("maintenance")),
    task_default_queue="maintenance",
    worker_prefetch_multiplier=1,
    # A task that crashes should be redelivered instead of silently lost.
    task_acks_late=True,
)
