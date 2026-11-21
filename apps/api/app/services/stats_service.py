from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Job
from app.models.enums import EmploymentType, JobStatus, RoleCategory
from app.schemas.job import CategoryCount, StatsResponse


async def get_stats(db: AsyncSession) -> StatsResponse:
    active = JobStatus.ACTIVE.value

    async def count(*conditions) -> int:
        stmt = select(func.count()).select_from(Job).where(*conditions)
        return int((await db.execute(stmt)).scalar_one())

    total_active = await count(Job.status == active)
    fresher = await count(Job.status == active, Job.fresher_friendly.is_(True))
    internships = await count(Job.status == active, Job.employment_type == EmploymentType.INTERNSHIP.value)

    today = datetime.now(timezone.utc) - timedelta(days=1)
    new_today = await count(Job.status == active, Job.first_seen_at >= today)

    # Count only companies that actually have a live posting, not every
    # candidate board in the source registry.
    companies = int(
        (
            await db.execute(
                select(func.count(func.distinct(Job.company_id))).where(Job.status == active)
            )
        ).scalar_one()
    )

    city_rows = (
        await db.execute(
            select(Job.city, func.count().label("count"))
            .where(Job.status == active, Job.city.isnot(None))
            .group_by(Job.city)
            .order_by(func.count().desc())
            .limit(12)
        )
    ).all()
    cities = [CategoryCount(name=row[0], count=row[1]) for row in city_rows]

    role_rows = (
        await db.execute(
            select(Job.role_category, func.count().label("count"))
            .where(Job.status == active, Job.role_category.isnot(None))
            .group_by(Job.role_category)
            .order_by(func.count().desc())
        )
    ).all()
    roles = [
        CategoryCount(name=(row[0].value if isinstance(row[0], RoleCategory) else str(row[0])), count=row[1])
        for row in role_rows
    ]

    return StatsResponse(
        total_active_jobs=total_active,
        fresher_friendly_jobs=fresher,
        internships=internships,
        new_jobs_today=new_today,
        companies=companies,
        cities=len(cities),
        role_categories=roles,
        top_cities=cities,
    )


async def get_locations(db: AsyncSession) -> list[CategoryCount]:
    rows = (
        await db.execute(
            select(Job.city, func.count().label("count"))
            .where(Job.status == JobStatus.ACTIVE.value, Job.city.isnot(None))
            .group_by(Job.city)
            .order_by(func.count().desc())
            .limit(100)
        )
    ).all()
    return [CategoryCount(name=row[0], count=row[1]) for row in rows]


async def get_categories(db: AsyncSession) -> list[CategoryCount]:
    rows = (
        await db.execute(
            select(Job.role_category, func.count().label("count"))
            .where(Job.status == JobStatus.ACTIVE.value, Job.role_category.isnot(None))
            .group_by(Job.role_category)
            .order_by(func.count().desc())
        )
    ).all()
    return [
        CategoryCount(name=(row[0].value if isinstance(row[0], RoleCategory) else str(row[0])), count=row[1])
        for row in rows
    ]


async def new_job_cutoff() -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=settings.new_job_days)
