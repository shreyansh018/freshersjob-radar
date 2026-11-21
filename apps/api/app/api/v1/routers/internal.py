"""Scheduler endpoints.

Celery Beat needs a long-running process, which Vercel does not provide. Vercel
Cron calls these routes with ``Authorization: Bearer $CRON_SECRET`` and the
routes enqueue the same tasks Beat used to schedule.
"""

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.core.config import settings
from app.workers.tasks import (
    expire_unconfirmed_task,
    fan_out_ingestion_task,
    source_health_task,
)

router = APIRouter(prefix="/internal", tags=["internal"])


def require_cron_secret(authorization: str | None = Header(default=None)) -> None:
    expected = settings.cron_secret
    if not expected or authorization != f"Bearer {expected}":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid cron secret")


@router.api_route("/cron/ingest", methods=["GET", "POST"], dependencies=[Depends(require_cron_secret)])
async def cron_ingest() -> dict:
    """Daily maintenance run.

    Hobby Vercel accounts only allow cron jobs that run at most once per day,
    so ingestion, freshness and source health are queued together here. On Pro,
    use the separate /cron/freshness and /cron/source-health routes to restore
    the original hourly / six-hourly schedules.
    """
    ingest = fan_out_ingestion_task.delay()
    freshness = expire_unconfirmed_task.delay()
    health = source_health_task.delay()
    return {
        "status": "queued",
        "task_ids": {
            "ingest": ingest.id,
            "freshness": freshness.id,
            "source_health": health.id,
        },
    }


@router.api_route("/cron/freshness", methods=["GET", "POST"], dependencies=[Depends(require_cron_secret)])
async def cron_freshness() -> dict:
    result = expire_unconfirmed_task.delay()
    return {"task_id": result.id, "status": "queued"}


@router.api_route("/cron/source-health", methods=["GET", "POST"], dependencies=[Depends(require_cron_secret)])
async def cron_source_health() -> dict:
    result = source_health_task.delay()
    return {"task_id": result.id, "status": "queued"}
