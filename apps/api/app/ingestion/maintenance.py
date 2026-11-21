from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.models import Job, Source
from app.models.enums import JobStatus, SourceHealth

logger = get_logger("ingestion.maintenance")


async def expire_unconfirmed_jobs() -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.expire_after_days_unconfirmed)
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            update(Job)
            .where(Job.status != JobStatus.EXPIRED, Job.last_source_confirmed_at < cutoff)
            .values(status=JobStatus.EXPIRED)
        )
        await db.commit()
        logger.info("expired_unconfirmed_jobs", count=result.rowcount)
        return int(result.rowcount or 0)


async def mark_degraded_sources() -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=2)
    async with AsyncSessionLocal() as db:
        sources = (await db.execute(select(Source).where(Source.enabled.is_(True)))).scalars().all()
        count = 0
        for source in sources:
            if source.last_success_at is None or source.last_success_at < cutoff:
                source.health_status = SourceHealth.DEGRADED
                count += 1
        await db.commit()
        return count
