import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.session import get_db
from app.schemas.job import JobDetail, JobFilters, PaginatedJobs
from app.services.job_service import to_detail, to_summary
from app.services.search_service import get_job, get_related_jobs, search_jobs

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=PaginatedJobs)
async def list_jobs(
    filters: JobFilters = Depends(),
    db: AsyncSession = Depends(get_db),
) -> PaginatedJobs:
    jobs, total = await search_jobs(db, filters)
    return PaginatedJobs(
        items=[to_summary(job) for job in jobs],
        total=total,
        page=filters.page,
        limit=filters.limit,
        has_more=(filters.page * filters.limit) < total,
    )


@router.get("/{job_id}", response_model=JobDetail)
async def job_detail(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> JobDetail:
    job = await get_job(db, job_id)
    if not job:
        raise AppError(404, "job_not_found", "Job not found")
    return to_detail(job)


@router.get("/{job_id}/related", response_model=list[JobDetail])
async def related_jobs(
    job_id: uuid.UUID,
    limit: int = Query(default=6, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
) -> list[JobDetail]:
    job = await get_job(db, job_id)
    if not job:
        raise AppError(404, "job_not_found", "Job not found")
    jobs = await get_related_jobs(db, job, limit)
    return [to_detail(item) for item in jobs]
