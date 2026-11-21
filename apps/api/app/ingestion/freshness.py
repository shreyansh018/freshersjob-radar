from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.models.enums import JobStatus


@dataclass
class FreshnessDecision:
    status: JobStatus
    missing_count: int
    should_confirm: bool


def decide_freshness(
    *,
    seen_in_fetch: bool,
    fetch_succeeded: bool,
    current_status: JobStatus,
    missing_count: int,
    last_confirmed_at: datetime | None,
    now: datetime | None = None,
) -> FreshnessDecision:
    """A failed fetch must never expire a job; only successful observations count."""
    now = now or datetime.now(timezone.utc)

    if not fetch_succeeded:
        return FreshnessDecision(current_status, missing_count, False)

    if seen_in_fetch:
        return FreshnessDecision(JobStatus.ACTIVE, 0, True)

    next_missing = missing_count + 1
    if next_missing >= settings.stale_after_misses:
        return FreshnessDecision(JobStatus.STALE, next_missing, False)

    if last_confirmed_at and last_confirmed_at < now - timedelta(days=settings.expire_after_days_unconfirmed):
        return FreshnessDecision(JobStatus.EXPIRED, next_missing, False)

    return FreshnessDecision(current_status if current_status != JobStatus.ACTIVE else JobStatus.ACTIVE, next_missing, False)
