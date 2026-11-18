import asyncio
import time

from app.pipeline.greenhouse import fetch_greenhouse_jobs
from app.pipeline.lever import fetch_lever_jobs
from app.pipeline.sources import GREENHOUSE_SOURCES, LEVER_SOURCES
from app.pipeline.filters import filter_target_jobs
from app.pipeline.dedup import deduplicate_jobs
from app.pipeline.classifier import classify_job


MAX_SOURCE_CONCURRENCY = 5
MAX_AI_CONCURRENCY = 3


async def run_ingestion():
    start_time = time.perf_counter()

    source_semaphore = asyncio.Semaphore(MAX_SOURCE_CONCURRENCY)
    ai_semaphore = asyncio.Semaphore(MAX_AI_CONCURRENCY)

    source_configs = [
        ("greenhouse", source)
        for source in GREENHOUSE_SOURCES
    ] + [
        ("lever", source)
        for source in LEVER_SOURCES
    ]

    # STEP 1: FETCH

    print(
        f"\n[START] Fetching jobs from {len(source_configs)} sources...",
        flush=True,
    )

    async def run_one(platform, source):
        async with source_semaphore:
            print(
                f"[FETCH START] {platform} | {source.company}",
                flush=True,
            )

            source_start = time.perf_counter()

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

                elapsed = round(
                    time.perf_counter() - source_start, 2
                )

                print(
                    f"[FETCH DONE] {source.company} | "
                    f"{len(jobs)} jobs | {elapsed}s",
                    flush=True,
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
                print(
                    f"[FETCH ERROR] {source.company} | {exc}",
                    flush=True,
                )

                return {
                    "company": source.company,
                    "platform": platform,
                    "status": "failed",
                    "count": 0,
                    "jobs": [],
                    "error": str(exc),
                }

    source_results = await asyncio.gather(
        *(
            run_one(platform, source)
            for platform, source in source_configs
        )
    )

    raw_jobs = [
        job
        for result in source_results
        for job in result["jobs"]
    ]

    print(
        f"[DONE] Collected {len(raw_jobs)} raw jobs.",
        flush=True,
    )

    # STEP 2: FILTER

    filtered_jobs = filter_target_jobs(raw_jobs)

    print(
        f"[FILTER DONE] {len(filtered_jobs)} jobs passed.",
        flush=True,
    )

    # STEP 3: DEDUP

    unique_jobs = deduplicate_jobs(filtered_jobs)

    print(
        f"[DEDUP DONE] {len(unique_jobs)} unique jobs.",
        flush=True,
    )

    # STEP 4: CLASSIFY

    total_to_classify = len(unique_jobs)
    completed_count = 0

    print(
        f"[AI] Classifying {total_to_classify} jobs...",
        flush=True,
    )

    async def classify_one(job):
        nonlocal completed_count

        async with ai_semaphore:
            job_start = time.perf_counter()

            print(
                f"[AI START] {job.company} | {job.title}",
                flush=True,
            )

            try:
                result = await asyncio.to_thread(
                    classify_job,
                    job,
                )

                job.role_category = result.role_category
                job.city = result.city
                job.experience_level = result.experience_level
                job.job_type = result.job_type
                job.is_fresher_friendly = (
                    result.is_fresher_friendly
                )
                job.classification_confidence = (
                    result.confidence
                )
                job.classification_reasoning = (
                    result.reasoning
                )

                job.classification_error = None
                job.ai_status = "success"

                elapsed = round(
                    time.perf_counter() - job_start, 2
                )

                completed_count += 1

                print(
                    f"[AI DONE {completed_count}/"
                    f"{total_to_classify}] {job.title} | "
                    f"Fresher-friendly: "
                    f"{job.is_fresher_friendly} | "
                    f"{elapsed}s",
                    flush=True,
                )

                return {
                    "job": job,
                    "status": "success",
                    "error": None,
                }

            except Exception as exc:
                job.ai_status = "failed"
                job.classification_error = str(exc)

                elapsed = round(
                    time.perf_counter() - job_start, 2
                )

                completed_count += 1

                print(
                    f"[AI ERROR {completed_count}/"
                    f"{total_to_classify}] {job.title} | "
                    f"{exc} | {elapsed}s",
                    flush=True,
                )

                return {
                    "job": job,
                    "status": "failed",
                    "error": str(exc),
                }

    if unique_jobs:
        classification_results = await asyncio.gather(
            *(classify_one(job) for job in unique_jobs)
        )
    else:
        classification_results = []

    classified_jobs = [
        result["job"]
        for result in classification_results
    ]

    # STEP 5: FINAL FILTER

    final_jobs = [
        job
        for job in classified_jobs
        if (
            job.ai_status == "failed"
            or job.is_fresher_friendly is True
        )
    ]

    ai_success_count = sum(
        result["status"] == "success"
        for result in classification_results
    )

    ai_failure_count = sum(
        result["status"] == "failed"
        for result in classification_results
    )

    ai_rejected_count = sum(
        result["status"] == "success"
        and result["job"].is_fresher_friendly is False
        for result in classification_results
    )

    # STEP 6: REPORT DATA

    elapsed = round(
        time.perf_counter() - start_time, 2
    )

    print(
        "\n[COMPLETE] Ingestion pipeline finished.",
        flush=True,
    )

    return {
        "sources": source_results,
        "raw_jobs_count": len(raw_jobs),
        "filtered_jobs_count": len(filtered_jobs),
        "unique_jobs_count": len(unique_jobs),
        "ai_success_count": ai_success_count,
        "ai_failure_count": ai_failure_count,
        "ai_rejected_count": ai_rejected_count,
        "total_jobs": len(final_jobs),
        "successful_sources": sum(
            result["status"] == "success"
            for result in source_results
        ),
        "failed_sources": sum(
            result["status"] == "failed"
            for result in source_results
        ),
        "duration_seconds": elapsed,
        "jobs": final_jobs,
    }