import asyncio
import time

from app.pipeline.greenhouse import fetch_greenhouse_jobs
from app.pipeline.sources import GREENHOUSE_SOURCES


MAX_CONCURRENCY = 5


async def ingest_greenhouse_source(source):
    return await fetch_greenhouse_jobs(
        board_token=source.board_token,
        company=source.company,
    )


async def run_ingestion():
    start_time = time.perf_counter()

    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    async def run_one(source):
        async with semaphore:
            try:
                jobs = await ingest_greenhouse_source(source)

                return {
                    "company": source.company,
                    "status": "success",
                    "count": len(jobs),
                    "jobs": jobs,
                    "error": None,
                }

            except Exception as exc:
                return {
                    "company": source.company,
                    "status": "failed",
                    "count": 0,
                    "jobs": [],
                    "error": str(exc),
                }

    results = await asyncio.gather(
        *(run_one(source) for source in GREENHOUSE_SOURCES)
    )

    all_jobs = [
        job
        for result in results
        for job in result["jobs"]
    ]

    elapsed = time.perf_counter() - start_time

    return {
        "sources": results,
        "total_jobs": len(all_jobs),
        "successful_sources": sum(
            result["status"] == "success"
            for result in results
        ),
        "failed_sources": sum(
            result["status"] == "failed"
            for result in results
        ),
        "duration_seconds": round(elapsed, 2),
        "jobs": all_jobs,
    }