from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.models import Job
from app.schemas.job import JobDetail, JobSummary


def _flags(job: Job) -> tuple[bool, bool]:
    now = datetime.now(timezone.utc)
    is_new = bool(job.first_seen_at and job.first_seen_at >= now - timedelta(days=settings.new_job_days))
    verified = bool(
        job.last_source_confirmed_at
        and job.last_source_confirmed_at >= now - timedelta(days=1)
    )
    return is_new, verified


def to_summary(job: Job) -> JobSummary:
    result = JobSummary.model_validate(job)
    result.is_new, result.recently_verified = _flags(job)
    return result


def to_detail(job: Job) -> JobDetail:
    result = JobDetail.model_validate(job)
    result.is_new, result.recently_verified = _flags(job)
    return result
