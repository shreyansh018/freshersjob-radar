import uuid

from sqlalchemy import case, func, literal_column, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Company, Job, Source
from app.models.enums import JobStatus, WorkplaceType
from app.schemas.job import JobFilters

SEARCH_DOCUMENT = func.to_tsvector(
    literal_column("'english'::regconfig"),
    func.coalesce(Job.title, "") + " " + func.coalesce(Job.description, ""),
)


def _conditions(filters: JobFilters) -> list:
    conditions = [Job.status == JobStatus.ACTIVE, Job.india_eligible.is_(True)]

    if filters.q:
        terms = [term.strip() for term in filters.q.split() if term.strip()]
        if terms:
            tsquery = func.websearch_to_tsquery("english", " ".join(terms))
            clauses = [SEARCH_DOCUMENT.op("@@")(tsquery)]
            for term in terms[:5]:
                pattern = f"%{term}%"
                clauses.extend(
                    [
                        Job.title.ilike(pattern),
                        Company.name.ilike(pattern),
                        Job.skills.any(term),
                    ]
                )
            conditions.append(or_(*clauses))

    if filters.company:
        conditions.append(Company.name.ilike(f"%{filters.company.strip()}%"))
    if filters.city:
        conditions.append(Job.city.ilike(f"%{filters.city.strip()}%"))
    if filters.location:
        conditions.append(
            or_(
                Job.normalized_location.ilike(f"%{filters.location.strip()}%"),
                Job.city.ilike(f"%{filters.location.strip()}%"),
            )
        )
    if filters.role_category:
        conditions.append(Job.role_category == filters.role_category.value)
    if filters.experience_level:
        conditions.append(Job.experience_level == filters.experience_level.value)
    if filters.employment_type:
        conditions.append(Job.employment_type == filters.employment_type.value)
    if filters.workplace_type:
        conditions.append(Job.workplace_type == filters.workplace_type.value)
    if filters.remote is True:
        conditions.append(Job.workplace_type.in_([WorkplaceType.REMOTE.value, WorkplaceType.HYBRID.value]))
    if filters.remote is False:
        conditions.append(Job.workplace_type != WorkplaceType.REMOTE.value)
    if filters.skills:
        for skill in [s.strip() for s in filters.skills.split(",") if s.strip()][:8]:
            conditions.append(Job.skills.any(skill))
    if filters.posted_after:
        conditions.append(Job.posted_at >= filters.posted_after)

    return conditions


def _relevance(filters: JobFilters):
    if not filters.q:
        return case((Job.title.isnot(None), 0), else_=0)
    term = filters.q.strip().lower()
    tsquery = func.websearch_to_tsquery("english", filters.q)
    return (
        func.ts_rank(SEARCH_DOCUMENT, tsquery)
        + case((func.lower(Job.title).like(term + "%"), 10), else_=0)
        + case((func.lower(Company.name).like(term + "%"), 5), else_=0)
        + case((Job.fresher_friendly.is_(True), 2), else_=0)
    )


async def search_jobs(db: AsyncSession, filters: JobFilters) -> tuple[list[Job], int]:
    conditions = _conditions(filters)
    relevance = _relevance(filters)

    count_stmt = (
        select(func.count())
        .select_from(Job)
        .join(Company, Company.id == Job.company_id, isouter=True)
        .where(*conditions)
    )
    total = (await db.execute(count_stmt)).scalar_one()

    sort_column = {
        "relevance": relevance.desc(),
        "newest": Job.posted_at.desc().nullslast(),
        "oldest": Job.posted_at.asc().nullslast(),
    }[filters.sort]

    stmt = (
        select(Job)
        .join(Company, Company.id == Job.company_id, isouter=True)
        .options(selectinload(Job.company), selectinload(Job.source))
        .where(*conditions)
        .order_by(sort_column, Job.id.desc())
        .offset((filters.page - 1) * filters.limit)
        .limit(filters.limit)
    )
    rows = (await db.execute(stmt)).scalars().unique().all()
    return list(rows), int(total)


async def get_job(db: AsyncSession, job_id: uuid.UUID) -> Job | None:
    stmt = (
        select(Job)
        .join(Source, Source.id == Job.source_id)
        .options(selectinload(Job.company), selectinload(Job.source))
        .where(Job.id == job_id)
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def get_related_jobs(db: AsyncSession, job: Job, limit: int = 6) -> list[Job]:
    clauses = [Job.id != job.id, Job.status == JobStatus.ACTIVE, Job.india_eligible.is_(True)]
    if job.role_category:
        clauses.append(Job.role_category == job.role_category)
    elif job.city:
        clauses.append(Job.city == job.city)
    if job.skills:
        clauses.append(or_(*[Job.skills.any(skill) for skill in job.skills[:4]]))

    stmt = (
        select(Job)
        .options(selectinload(Job.company), selectinload(Job.source))
        .where(or_(*clauses))
        .order_by(Job.posted_at.desc().nullslast())
        .limit(limit)
    )
    return list((await db.execute(stmt)).scalars().unique().all())
