from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Integer, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.metering import estimate_cost_usd
from app.db.session import get_db
from app.models import Classification, IngestionRun, Job, Source, User
from app.models.enums import JobStatus, SourceHealth
from app.schemas.admin import AdminOverview, IngestionRunOut, SourceOut
from app.services.auth_service import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


def _count_scalar(rows) -> int:
    return int(rows.scalar_one() or 0)


@router.get("/overview", response_model=AdminOverview)
async def overview(db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)) -> AdminOverview:
    async def count(stmt) -> int:
        return _count_scalar(await db.execute(stmt))

    last_run = (await db.execute(select(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(1))).scalar_one_or_none()
    ai_rows = (
        await db.execute(
            select(
                func.count().label("calls"),
                func.coalesce(func.sum(Classification.prompt_tokens), 0),
                func.coalesce(func.sum(Classification.completion_tokens), 0),
                func.coalesce(func.sum(func.cast(Classification.cache_hit, Integer)), 0),
            )
        )
    ).one()

    return AdminOverview(
        total_jobs=await count(select(func.count()).select_from(Job)),
        active_jobs=await count(select(func.count()).select_from(Job).where(Job.status == JobStatus.ACTIVE.value)),
        stale_jobs=await count(select(func.count()).select_from(Job).where(Job.status == JobStatus.STALE.value)),
        expired_jobs=await count(select(func.count()).select_from(Job).where(Job.status == JobStatus.EXPIRED.value)),
        sources_enabled=await count(select(func.count()).select_from(Source).where(Source.enabled.is_(True))),
        # Disabled boards that failed validation are expected to stay failing;
        # only count enabled sources so this is an actionable alert.
        sources_failing=await count(
            select(func.count()).select_from(Source).where(
                Source.enabled.is_(True), Source.health_status == SourceHealth.FAILING.value
            )
        ),
        last_ingestion_at=last_run.started_at if last_run else None,
        ai_calls=int(ai_rows[0]),
        ai_prompt_tokens=int(ai_rows[1]),
        ai_completion_tokens=int(ai_rows[2]),
        ai_cache_hits=int(ai_rows[3]),
        estimated_ai_cost_usd=estimate_cost_usd(int(ai_rows[1]), int(ai_rows[2])),
    )


@router.get("/sources", response_model=list[SourceOut])
async def sources(db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)) -> list[SourceOut]:
    rows = (await db.execute(select(Source).order_by(Source.name))).scalars().all()
    return [SourceOut.model_validate(row) for row in rows]


@router.get("/ingestion-runs", response_model=list[IngestionRunOut])
async def ingestion_runs(db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)) -> list[IngestionRunOut]:
    rows = (await db.execute(select(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(50))).scalars().all()
    return [IngestionRunOut.model_validate(row) for row in rows]


@router.post("/ingestion/run")
async def trigger_ingestion(_: User = Depends(require_admin)) -> dict:
    from app.core.config import settings
    from app.workers.tasks import fan_out_ingestion_task, ingest_all_task

    # A full cycle takes ~23 minutes at worst; Vercel Functions cap at 300-800s.
    # Fan out one task per board there, keep the single task in local Docker.
    task = fan_out_ingestion_task.delay() if settings.is_production else ingest_all_task.delay()
    return {"task_id": task.id, "status": "queued", "mode": "fan_out" if settings.is_production else "full"}


@router.post("/sources/{source_id}/toggle")
async def toggle_source(
    source_id: str, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)
) -> dict:
    import uuid

    source = (await db.execute(select(Source).where(Source.id == uuid.UUID(source_id)))).scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    source.enabled = not source.enabled
    await db.commit()
    return {"source_id": source_id, "enabled": source.enabled}
