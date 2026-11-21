import asyncio
import concurrent.futures
import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.ingestion.maintenance import expire_unconfirmed_jobs, mark_degraded_sources
from app.ingestion.pipeline import SourceCounts, ingest_all, ingest_source
from app.models import IngestionRun, Source
from app.workers.celery_app import celery_app

logger = get_logger("workers.tasks")


def _run_async(coro):
    """Run a coroutine from Celery, including inside Vercel's async worker loop."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    # Vercel's Celery adapter executes tasks inside an event loop. A dedicated
    # thread gives asyncio.run() a fresh loop without blocking that loop.
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(asyncio.run, coro).result()


@celery_app.task(name="ingestion.ingest_all", bind=True, max_retries=1)
def ingest_all_task(self):
    """Full cycle. Used by local Docker; too long for a single Vercel function."""
    try:
        return _run_async(ingest_all())
    except Exception as exc:
        logger.error("ingestion_task_failed", error=str(exc))
        raise self.retry(exc=exc, countdown=60)


async def _ingest_one_source(source_id: uuid.UUID) -> dict:
    """Ingest a single board with its own run row so it fits a function timeout."""
    started_at = datetime.now(timezone.utc)
    async with AsyncSessionLocal() as db:
        run = IngestionRun(started_at=started_at, status="running")
        db.add(run)
        await db.commit()
        await db.refresh(run)
        run_id = run.id

    counts: SourceCounts = await ingest_source(source_id, run_id, started_at)

    finished = datetime.now(timezone.utc)
    async with AsyncSessionLocal() as db:
        run = await db.get(IngestionRun, run_id)
        if run:
            run.finished_at = finished
            run.duration_ms = int((finished - started_at).total_seconds() * 1000)
            run.status = "completed" if not counts.failed else "completed_with_errors"
            run.raw_jobs = counts.raw
            run.normalized_jobs = counts.normalized
            run.candidate_jobs = counts.candidates
            run.classified_jobs = counts.classified
            run.new_jobs = counts.new
            run.updated_jobs = counts.updated
            run.unchanged_jobs = counts.unchanged
            run.duplicates = counts.duplicates
            run.failed_sources = int(counts.failed)
            await db.commit()
    return counts.__dict__


@celery_app.task(name="ingestion.ingest_one_source", bind=True, max_retries=1)
def ingest_one_source_task(self, source_id: str):
    """Vercel-safe ingestion unit: one ATS board per queue invocation."""
    try:
        return _run_async(_ingest_one_source(uuid.UUID(source_id)))
    except Exception as exc:
        logger.error("source_ingestion_failed", source_id=source_id, error=str(exc))
        raise self.retry(exc=exc, countdown=60)


async def _enabled_source_ids() -> list[str]:
    async with AsyncSessionLocal() as db:
        rows = (await db.execute(select(Source.id).where(Source.enabled.is_(True)))).scalars().all()
    return [str(row) for row in rows]


@celery_app.task(name="ingestion.fan_out")
def fan_out_ingestion_task() -> dict:
    """Enqueue one task per enabled board. Called by Vercel Cron."""
    source_ids = _run_async(_enabled_source_ids())
    for source_id in source_ids:
        ingest_one_source_task.delay(source_id)
    logger.info("ingestion_fanned_out", sources=len(source_ids))
    return {"queued": len(source_ids)}


@celery_app.task(name="maintenance.expire_unconfirmed")
def expire_unconfirmed_task() -> int:
    return _run_async(expire_unconfirmed_jobs())


@celery_app.task(name="maintenance.source_health")
def source_health_task() -> int:
    return _run_async(mark_degraded_sources())
