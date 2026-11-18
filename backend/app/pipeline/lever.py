import asyncio
from datetime import datetime
from typing import Any

import httpx

from app.pipeline.schemas import JobRecord


BASE_URL = "https://api.lever.co/v0/postings"
MAX_RETRIES = 3


def normalize_lever_job(item: dict[str, Any], company: str) -> JobRecord:
    categories = item.get("categories") or {}
    location = categories.get("location") or "Unspecified"

    raw_date = item.get("createdAt")
    posted_at = None

    if raw_date:
        try:
            # Lever timestamps are often milliseconds since Unix epoch.
            if isinstance(raw_date, (int, float)):
                posted_at = datetime.fromtimestamp(raw_date / 1000)
            else:
                posted_at = datetime.fromisoformat(
                    str(raw_date).replace("Z", "+00:00")
                )
        except (ValueError, TypeError, OverflowError):
            posted_at = None

    workplace_type = item.get("workplaceType")

    return JobRecord(
        source="lever",
        source_id=str(item["id"]),
        title=item.get("text") or "Unknown title",
        company=company,
        location=location,
        description=item.get("description") or "",
        url=item.get("hostedUrl") or item.get("applyUrl"),
        posted_at=posted_at,
        workplace_type=workplace_type,
    )


async def fetch_lever_jobs(
    site: str,
    company: str,
    client: httpx.AsyncClient | None = None,
) -> list[JobRecord]:

    if not site or not site.strip():
        raise ValueError("Lever site cannot be empty")

    url = f"{BASE_URL}/{site}"
    params = {"mode": "json"}

    owns_client = client is None

    if owns_client:
        client = httpx.AsyncClient(timeout=20.0)

    assert client is not None

    try:
        for attempt in range(MAX_RETRIES):
            try:
                response = await client.get(url, params=params)

                if response.status_code == 429 or response.status_code >= 500:
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

        normalized_jobs = []

        if not isinstance(payload, list):
            return normalized_jobs

        for item in payload:
            try:
                if not item.get("id") or not (
                    item.get("hostedUrl") or item.get("applyUrl")
                ):
                    continue

                normalized_jobs.append(
                    normalize_lever_job(item, company)
                )

            except (ValueError, TypeError, KeyError):
                continue

        return normalized_jobs

    finally:
        if owns_client:
            await client.aclose()