import asyncio

from app.pipeline.runner import run_ingestion


async def main():
    report = await run_ingestion()

    print("\n========== INGESTION REPORT ==========\n")

    print(f"Raw jobs: {report['raw_jobs_count']}")
    print(f"Target jobs: {report['filtered_jobs_count']}")
    print(f"Unique jobs: {report['unique_jobs_count']}")

    print(f"AI classified successfully: {report['ai_success_count']}")
    print(f"AI classification failed: {report['ai_failure_count']}")
    print(f"AI rejected as not fresher-friendly: {report['ai_rejected_count']}")

    print(f"Final jobs: {report['total_jobs']}")
    print(f"Successful sources: {report['successful_sources']}")
    print(f"Failed sources: {report['failed_sources']}")
    print(f"Duration: {report['duration_seconds']} seconds")

    print("\nSource details:")

    for source in report["sources"]:
        print(
            f"{source['platform']} | "
            f"{source['company']} | "
            f"{source['status']} | "
            f"{source['count']} jobs"
        )

        if source["error"]:
            print(f"  Error: {source['error']}")

    print("\nSample AI-classified jobs:")

    for job in report["jobs"][:15]:
        print("-" * 60)

        print(f"Title: {job.title}")
        print(f"Company: {job.company}")
        print(f"Original location: {job.location}")
        print(f"AI city: {job.city}")
        print(f"Role: {job.role_category}")
        print(f"Experience: {job.experience_level}")
        print(f"Job type: {job.job_type}")
        print(f"Fresher friendly: {job.is_fresher_friendly}")
        print(f"AI status: {job.ai_status}")
        print(f"Confidence: {job.classification_confidence}")

        if job.classification_error:
            print(f"AI ERROR DETAILS: {job.classification_error}")

        print(f"URL: {job.url}")

    print("\n=====================================\n")


if __name__ == "__main__":
    asyncio.run(main())