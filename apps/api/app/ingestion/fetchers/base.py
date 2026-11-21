import asyncio
import random
import time
from dataclasses import dataclass, field
from typing import Any

import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("ingestion.fetchers")

USER_AGENT = "FreshersJobRadar/0.1 (+https://example.com/freshersjob-radar; public job board aggregator)"


@dataclass
class FetchResult:
    raw_jobs: list[dict[str, Any]] = field(default_factory=list)
    http_status: int | None = None
    duration_ms: int = 0
    error: str | None = None


class BaseFetcher:
    """Fetches a public, unauthenticated ATS board and returns raw records.

    Only public endpoints are used. No authentication, paywall or anti-bot
    protection is ever bypassed. Rate limiting is cooperative.
    """

    platform = "base"

    def __init__(self, source: Any):
        self.source = source
        self.board = source.board_identifier

    def build_url(self) -> str:
        raise NotImplementedError

    def parse(self, payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict) and isinstance(payload.get("jobs"), list):
            return payload["jobs"]
        return []

    async def _get_json(self, url: str) -> tuple[Any, int]:
        timeout = httpx.Timeout(settings.http_timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}) as client:
            last_error: Exception | None = None
            for attempt in range(settings.http_max_retries + 1):
                try:
                    response = await client.get(url, follow_redirects=True)
                    if response.status_code == 429:
                        retry_after = float(response.headers.get("Retry-After", "2"))
                        await asyncio.sleep(min(retry_after, 30))
                        continue
                    response.raise_for_status()
                    return response.json(), response.status_code
                except (httpx.HTTPError, ValueError) as exc:
                    last_error = exc
                    if attempt < settings.http_max_retries:
                        delay = (2**attempt) + random.uniform(0, 0.5)
                        await asyncio.sleep(delay)
            raise RuntimeError(f"fetch_failed after {settings.http_max_retries + 1} attempts: {last_error}")

    async def fetch(self) -> FetchResult:
        started = time.monotonic()
        try:
            url = self.build_url()
            payload, status = await self._get_json(url)
            jobs = self.parse(payload)
            return FetchResult(raw_jobs=jobs, http_status=status, duration_ms=int((time.monotonic() - started) * 1000))
        except Exception as exc:
            logger.warning("source_fetch_failed", platform=self.platform, board=self.board, error=str(exc))
            return FetchResult(
                error=str(exc), duration_ms=int((time.monotonic() - started) * 1000)
            )
