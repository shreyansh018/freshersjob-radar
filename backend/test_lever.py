import asyncio

from app.pipeline.lever import fetch_lever_jobs


async def main():
    jobs = await fetch_lever_jobs(
        site="employ",
        company="Employ",
    )

    print(f"Jobs found: {len(jobs)}")

    for job in jobs[:10]:
        print(
            f"{job.title} | "
            f"{job.location} | "
            f"{job.url}"
        )


if __name__ == "__main__":
    asyncio.run(main())