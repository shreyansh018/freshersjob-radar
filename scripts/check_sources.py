"""Probe every enabled source and print a coverage report.

Use this before claiming a job count. It only reads public endpoints.
"""

import asyncio
import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1] / "apps" / "api"
if (API_DIR / "app").exists():
    sys.path.insert(0, str(API_DIR))

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.ingestion.fetchers.factory import get_fetcher
from app.ingestion.location import parse_location
from app.ingestion.normalize import normalize
from app.models import Source


async def check(source: Source) -> dict:
    fetcher = get_fetcher(source.platform, source)
    result = await fetcher.fetch()
    india_posts = 0
    for raw in result.raw_jobs:
        normalized = normalize(raw, source.platform, source.name)
        if not normalized:
            continue
        location = parse_location(normalized.location_text, normalized.description)
        if location.india_eligible:
            india_posts += 1
    return {
        "source": source.name,
        "platform": source.platform,
        "board": source.board_identifier,
        "received": len(result.raw_jobs),
        "india_posts": india_posts,
        "error": result.error,
    }


async def main() -> None:
    async with AsyncSessionLocal() as db:
        sources = list((await db.execute(select(Source).where(Source.enabled.is_(True)))).scalars().all())
    results = await asyncio.gather(*(check(source) for source in sources))
    print(f"{'SOURCE':22} {'PLATFORM':16} {'RAW':>6} {'INDIA':>6}  ERROR")
    total_raw = total_india = 0
    for row in sorted(results, key=lambda item: item["india_posts"], reverse=True):
        print(
            f"{row['source'][:22]:22} {row['platform'][:16]:16} "
            f"{row['received']:6} {row['india_posts']:6}  {(row['error'] or '')[:60]}"
        )
        total_raw += row["received"]
        total_india += row["india_posts"]
    print(f"\nTOTAL raw={total_raw} india_eligible={total_india} sources={len(results)}")


if __name__ == "__main__":
    asyncio.run(main())
