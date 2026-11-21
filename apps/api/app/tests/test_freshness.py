from datetime import datetime, timedelta, timezone

from app.ingestion.freshness import decide_freshness
from app.models.enums import JobStatus


def _now():
    return datetime.now(timezone.utc)


def test_fetch_failure_never_expires():
    decision = decide_freshness(
        seen_in_fetch=False,
        fetch_succeeded=False,
        current_status=JobStatus.ACTIVE,
        missing_count=9,
        last_confirmed_at=_now() - timedelta(days=90),
    )
    assert decision.status == JobStatus.ACTIVE
    assert decision.should_confirm is False


def test_repeated_successful_misses_make_job_stale():
    decision = decide_freshness(
        seen_in_fetch=False,
        fetch_succeeded=True,
        current_status=JobStatus.ACTIVE,
        missing_count=2,
        last_confirmed_at=_now(),
    )
    assert decision.status == JobStatus.STALE


def test_seen_job_is_confirmed_and_reset():
    decision = decide_freshness(
        seen_in_fetch=True,
        fetch_succeeded=True,
        current_status=JobStatus.STALE,
        missing_count=4,
        last_confirmed_at=None,
    )
    assert decision.status == JobStatus.ACTIVE
    assert decision.missing_count == 0
    assert decision.should_confirm is True
