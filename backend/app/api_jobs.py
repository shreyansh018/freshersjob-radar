
from fastapi import APIRouter, Query

from .pipeline.job_storage import (
    search_jobs,
    get_job,
    get_job_stats,
)

router = APIRouter(prefix="/api", tags=["Jobs"])


@router.get("/jobs")
def list_jobs(
    keyword: str | None = None,
    city: str | None = None,
    role: str | None = None,
    company: str | None = None,
    fresher_only: bool = True,
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    results = search_jobs(
        keyword=keyword,
        city=city,
        role=role,
        company=company,
        fresher_only=fresher_only,
        limit=limit,
        offset=offset,
    )

    return {
        "count": len(results),
        "jobs": results,
    }


@router.get("/jobs/{source}/{source_id}")
def job_detail(source: str, source_id: str):
    result = get_job(source, source_id)

    if not result:
        return {"error": "Job not found"}

    return result


@router.get("/stats")
def stats():
    return get_job_stats()
