"""Recompute deterministic role and seniority tags from stored postings.

Use after improving inference rules so existing jobs are retagged without a
full re-ingest. AI labels are kept unless they fall back to a weak default.
"""

import asyncio
import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1] / "apps" / "api"
if (API_DIR / "app").exists():
    sys.path.insert(0, str(API_DIR))

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.ingestion.experience import extract_experience
from app.ingestion.fallback import infer_level, infer_role
from app.ingestion.relevance import score_relevance
from app.models import Classification, Job
from app.models.enums import ExperienceLevel

EARLY_LEVELS = {ExperienceLevel.INTERNSHIP, ExperienceLevel.FRESHER, ExperienceLevel.ENTRY_LEVEL}


async def main() -> None:
    async with AsyncSessionLocal() as db:
        jobs = list((await db.execute(select(Job).where(Job.status == "active"))).scalars().all())
        ai_job_ids = set((await db.execute(select(Classification.job_id))).scalars().all())
        roles_changed = levels_changed = friendly_changed = 0
        for job in jobs:
            is_ai = job.id in ai_job_ids

            new_role = infer_role(job.title)
            current_role = job.role_category.value if job.role_category else None
            if (not is_ai and job.role_category != new_role) or (
                is_ai and current_role == "Other" and new_role.value != "Other"
            ):
                job.role_category = new_role
                roles_changed += 1

            relevance = score_relevance(job.title, job.description, None)
            experience = extract_experience(f"{job.title}\n{(job.description or '')[:3000]}")
            new_level = infer_level(job.title, relevance, experience)
            current_level = job.experience_level.value if job.experience_level else None

            # AI labels are authoritative unless they are missing/Unknown.
            should_update = not is_ai or (current_level in {None, "Unknown"} and new_level.value != "Unknown")
            if should_update:
                if job.experience_level != new_level:
                    job.experience_level = new_level
                    levels_changed += 1
                new_friendly = new_level in EARLY_LEVELS or relevance.state.value in {"strong", "possible"}
                if job.fresher_friendly != new_friendly:
                    job.fresher_friendly = new_friendly
                    friendly_changed += 1

        await db.commit()
    print(
        f"Refreshed {len(jobs)} active jobs: "
        f"{roles_changed} role tags, {levels_changed} seniority tags, "
        f"{friendly_changed} fresher-friendly flags changed."
    )


if __name__ == "__main__":
    asyncio.run(main())
