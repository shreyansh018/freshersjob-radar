import asyncio

from app.pipeline.runner import run_ingestion


async def main():
    result = await run_ingestion()

    print("\n========== INGESTION REPORT ==========")

    print(f"Total jobs: {result['total_jobs']}")
    print(f"Successful sources: {result['successful_sources']}")
    print(f"Failed sources: {result['failed_sources']}")
    print(f"Duration: {result['duration_seconds']} seconds")

    print("\nSource details:")

    for source in result["sources"]:
        print(
            f"{source['company']} | "
            f"{source['status']} | "
            f"{source['count']} jobs"
        )

        if source["error"]:
            print(f"  Error: {source['error']}")

    print("=====================================")


if __name__ == "__main__":
    asyncio.run(main())