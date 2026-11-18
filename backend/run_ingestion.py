import asyncio

from app.pipeline.runner import run_ingestion


async def main():
    result = await run_ingestion()

    print("\n========== INGESTION REPORT ==========")
    print(f"Raw jobs: {result['raw_jobs_count']}")
    print(f"Target jobs: {result['filtered_jobs_count']}")
    print(f"Unique jobs: {result['unique_jobs_count']}")
    print(f"Successful sources: {result['successful_sources']}")
    print(f"Failed sources: {result['failed_sources']}")
    print(f"Duration: {result['duration_seconds']} seconds")

    print("\nSource details:")
    for source in result["sources"]:
        print(
            f"{source['platform']} | "
            f"{source['company']} | "
            f"{source['status']} | "
            f"{source['count']} jobs"
        )

        if source["error"]:
            print(f"  Error: {source['error']}")

    print("\nSample filtered jobs:")
    for job in result["jobs"][:15]:
        print(
            f"{job.title} | "
            f"{job.company} | "
            f"{job.location} | "
            f"{job.url}"
        )

    print("=====================================")


if __name__ == "__main__":
    asyncio.run(main())