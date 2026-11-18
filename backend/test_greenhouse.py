import httpx
import pytest

from app.pipeline.greenhouse import fetch_greenhouse_jobs


@pytest.mark.asyncio
async def test_fetch_greenhouse_jobs_normalizes_data():
    mock_payload = {
        "jobs": [
            {
                "id": 123,
                "title": "Software Engineer Intern",
                "absolute_url": "https://example.com/job/123",
                "updated_at": "2026-11-18T10:00:00Z",
                "location": {"name": "Bengaluru"},
                "content": "Python internship",
            }
        ]
    }

    async def handler(request):
        return httpx.Response(200, json=mock_payload)

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as client:
        jobs = await fetch_greenhouse_jobs(
            board_token="test-board",
            company="Test Company",
            client=client,
        )

    assert len(jobs) == 1
    assert jobs[0].title == "Software Engineer Intern"
    assert jobs[0].company == "Test Company"
    assert jobs[0].location == "Bengaluru"
    assert jobs[0].source_id == "123"


@pytest.mark.asyncio
async def test_skips_malformed_jobs():
    mock_payload = {
        "jobs": [
            {
                "id": 123,
                "title": "Valid Job",
                "absolute_url": "https://example.com/job/123",
                "location": {"name": "Bengaluru"},
            },
            {
                "title": "Missing ID",
                "location": {"name": "Delhi"},
            },
        ]
    }

    async def handler(request):
        return httpx.Response(200, json=mock_payload)

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as client:
        jobs = await fetch_greenhouse_jobs(
            board_token="test-board",
            company="Test Company",
            client=client,
        )

    assert len(jobs) == 1
    assert jobs[0].title == "Valid Job"


@pytest.mark.asyncio
async def test_invalid_board_returns_http_error():
    async def handler(request):
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(httpx.HTTPStatusError):
            await fetch_greenhouse_jobs(
                board_token="invalid-board",
                company="Test Company",
                client=client,
            )