"""Celery subscriber entrypoint used by Vercel Queues.

Vercel imports this module at build time, reads every queue declared on the
Celery app, and compiles a private queue-triggered function for it. Local
Docker keeps running `celery worker` against the same app.
"""

from app.workers.celery_app import celery_app as app

__all__ = ["app"]
