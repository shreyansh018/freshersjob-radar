from app.pipeline.filters import is_india_job, is_fresher_job
from app.pipeline.dedup import deduplicate_jobs
from app.pipeline.schemas import JobRecord


def make_job(
    title="Software Engineer Intern",
    company="Test Company",
    location="Bengaluru",
    source="greenhouse",
    source_id="123",
    description="Python internship for students",
    url="https://example.com/job/123",
):
    return JobRecord(
        source=source,
        source_id=source_id,
        title=title,
        company=company,
        location=location,
        description=description,
        url=url,
    )


def test_india_location_matches():
    job = make_job(location="Bengaluru, India")
    assert is_india_job(job)


def test_us_location_does_not_match():
    job = make_job(location="Los Angeles, CA")
    assert not is_india_job(job)


def test_internship_matches_fresher_filter():
    job = make_job(title="Software Engineer Intern")
    assert is_fresher_job(job)


def test_senior_job_does_not_match_fresher_filter():
    job = make_job(
        title="Senior Software Engineer",
        description="Requires 8 years of experience",
    )
    assert not is_fresher_job(job)


def test_deduplicates_identical_jobs():
    job1 = make_job(source_id="123")
    job2 = make_job(source_id="456")

    result = deduplicate_jobs([job1, job2])

    assert len(result) == 1


def test_keeps_different_jobs():
    job1 = make_job(source_id="123")
    job2 = make_job(
        title="Data Analyst Intern",
        source_id="456",
    )

    result = deduplicate_jobs([job1, job2])

    assert len(result) == 2