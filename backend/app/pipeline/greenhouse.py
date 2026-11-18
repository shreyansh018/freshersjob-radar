import asyncio
from datetime import datetime
from typing import Any

import httpx

from app.pipeline.schemas import JobRecord


BASE_URL = "https://boards-api.greenhouse.io/v1/boards"
MAX_RETRIES = 3


def normalize_job(item: dict[str, Any], company: str) -> JobRecord:
    """Convert a Greenhouse record into our standard job schema."""

    location = item.get("location") or {}
    raw_date = item.get("updated_at")

    posted_at = None
    if raw_date:
        try:
            posted_at = datetime.fromisoformat(
                raw_date.replace("Z", "+00:00")
            )
        except (ValueError, TypeError, AttributeError):
            posted_at = None

    return JobRecord(
        source="greenhouse",
        source_id=str(item["id"]),
        title=item.get("title") or "Unknown title",
        company=company,
        location=location.get("name") or "Unspecified",
        description=item.get("content") or "",
        url=item["absolute_url"],
        posted_at=posted_at,
    )


async def fetch_greenhouse_jobs(
    board_token: str,
    company: str,
    client: httpx.AsyncClient | None = None,
) -> list[JobRecord]:
    """
    Fetch published jobs and normalize them.

    Supports an injected HTTP client for deterministic testing.
    """

    if not board_token or not board_token.strip():
        raise ValueError("board_token cannot be empty")

    url = f"{BASE_URL}/{board_token}/jobs"
    params = {"content": "true"}

    owns_client = client is None

    if owns_client:
        client = httpx.AsyncClient(timeout=20.0)

    assert client is not None

    try:
        for attempt in range(MAX_RETRIES):
            try:
                response = await client.get(url, params=params)

                if response.status_code == 429:
                    if attempt == MAX_RETRIES - 1:
                        response.raise_for_status()

                    await asyncio.sleep(2 ** attempt)
                    continue

                if response.status_code >= 500:
                    if attempt == MAX_RETRIES - 1:
                        response.raise_for_status()

                    await asyncio.sleep(2 ** attempt)
                    continue

                response.raise_for_status()
                payload = response.json()
                break

            except httpx.TimeoutException:
                if attempt == MAX_RETRIES - 1:
                    raise

                await asyncio.sleep(2 ** attempt)

            except httpx.TransportError:
                if attempt == MAX_RETRIES - 1:
                    raise

                await asyncio.sleep(2 ** attempt)

        else:
            return []

        jobs = payload.get("jobs", [])

        normalized_jobs = []

        for item in jobs:
            try:
                if not item.get("id") or not item.get("absolute_url"):
                    continue

                normalized_jobs.append(
                    normalize_job(item, company)
                )

            except (ValueError, TypeError, KeyError):
                continue

        return normalized_jobs

    finally:
        if owns_client:
            await client.aclose()