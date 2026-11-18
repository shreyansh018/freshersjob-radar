
import asyncio
import time

from app.pipeline.greenhouse import fetch_greenhouse_jobs
from app.pipeline.lever import fetch_lever_jobs
from app.pipeline.sources import GREENHOUSE_SOURCES, LEVER_SOURCES
from app.pipeline.filters import filter_target_jobs
from app.pipeline.dedup import deduplicate_jobs


MAX_CONCURRENCY = 5


async def run_ingestion():
    start_time = time.perf_counter()
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    # Combine all configured sources into one list.
    source_configs = [
        ("greenhouse", source)
        for source in GREENHOUSE_SOURCES
    ] + [
        ("lever", source)
        for source in LEVER_SOURCES
    ]

    # Fetch jobs from one source.
    async def run_one(platform, source):
        async with semaphore:
            try:
                if platform == "greenhouse":
                    jobs = await fetch_greenhouse_jobs(
                        board_token=source.board_token,
                        company=source.company,
                    )

                elif platform == "lever":
                    jobs = await fetch_lever_jobs(
                        site=source.site,
                        company=source.company,
                    )

                else:
                    raise ValueError(
                        f"Unsupported platform: {platform}"
                    )

                return {
                    "company": source.company,
                    "platform": platform,
                    "status": "success",
                    "count": len(jobs),
                    "jobs": jobs,
                    "error": None,
                }

            except Exception as exc:
                return {
                    "company": source.company,
                    "platform": platform,
                    "status": "failed",
                    "count": 0,
                    "jobs": [],
                    "error": str(exc),
                }

    # Run all sources concurrently.
    results = await asyncio.gather(
        *(
            run_one(platform, source)
            for platform, source in source_configs
        )
    )

    # Collect all successfully fetched raw jobs.
    raw_jobs = [
        job
        for result in results
        for job in result["jobs"]
    ]

    # Filter for India-based fresher opportunities.
    filtered_jobs = filter_target_jobs(raw_jobs)

    # Remove duplicates.
    unique_jobs = deduplicate_jobs(filtered_jobs)

    # Calculate execution time.
    elapsed = time.perf_counter() - start_time

    return {
        "sources": results,
        "raw_jobs_count": len(raw_jobs),
        "filtered_jobs_count": len(filtered_jobs),
        "unique_jobs_count": len(unique_jobs),
        "total_jobs": len(unique_jobs),
        "successful_sources": sum(
            result["status"] == "success"
            for result in results
        ),
        "failed_sources": sum(
            result["status"] == "failed"
            for result in results
        ),
        "duration_seconds": round(elapsed, 2),
        "jobs": unique_jobs,
    }
