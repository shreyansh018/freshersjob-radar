import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.classifier import classify_job
from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.ingestion.dedupe import content_hash, dedupe_hash
from app.ingestion.experience import extract_experience
from app.ingestion.fetchers.factory import get_fetcher
from app.ingestion.freshness import decide_freshness
from app.ingestion.location import parse_location
from app.ingestion.normalize import normalize
from app.ingestion.relevance import score_relevance
from app.models import Classification, Company, IngestionRun, IngestionSourceRun, Job, Source
from app.models.enums import JobStatus, SourceHealth

logger = get_logger("ingestion.pipeline")


@dataclass
class SourceCounts:
    raw: int = 0
    normalized: int = 0
    candidates: int = 0
    new: int = 0
    updated: int = 0
    unchanged: int = 0
    duplicates: int = 0
    filtered_location: int = 0
    filtered_relevance: int = 0
    classified: int = 0
    ai_calls: int = 0
    failed: bool = False
    error: str | None = None
    failed_jobs: int = 0


@dataclass
class RunCounts:
    raw: int = 0
    normalized: int = 0
    candidates: int = 0
    new: int = 0
    updated: int = 0
    unchanged: int = 0
    duplicates: int = 0
    classified: int = 0
    failed_sources: int = 0

    def merge(self, counts: SourceCounts) -> None:
        self.raw += counts.raw
        self.normalized += counts.normalized
        self.candidates += counts.candidates
        self.new += counts.new
        self.updated += counts.updated
        self.unchanged += counts.unchanged
        self.duplicates += counts.duplicates
        self.classified += counts.classified
        if counts.failed:
            self.failed_sources += 1


async def ensure_company(db: AsyncSession, name: str) -> Company:
    company = (await db.execute(select(Company).where(Company.name == name))).scalar_one_or_none()
    if not company:
        company = Company(name=name)
        db.add(company)
        await db.flush()
    return company


async def load_enabled_sources(db: AsyncSession) -> list[Source]:
    rows = (await db.execute(select(Source).where(Source.enabled.is_(True)))).scalars().all()
    return list(rows)


async def ingest_source(source_id: uuid.UUID, run_id: uuid.UUID, started_at: datetime) -> SourceCounts:
    counts = SourceCounts()
    async with AsyncSessionLocal() as db:
        source = (await db.execute(select(Source).where(Source.id == source_id))).scalar_one_or_none()
        if not source:
            counts.failed = True
            counts.error = "source_not_found"
            return counts

        fetcher = get_fetcher(source.platform, source)
        fetch = await fetcher.fetch()
        counts.raw = len(fetch.raw_jobs)
        source.last_fetch_at = datetime.now(timezone.utc)
        source_run = IngestionSourceRun(
            run_id=run_id,
            source_id=source.id,
            http_status=fetch.http_status,
            duration_ms=fetch.duration_ms,
            jobs_received=counts.raw,
            error=fetch.error,
        )
        db.add(source_run)

        if fetch.error:
            counts.failed = True
            counts.error = fetch.error
            source.health_status = SourceHealth.FAILING
            source.last_error = fetch.error[:2000]
            await db.commit()
            return counts

        company = await ensure_company(db, source.name)

        for raw in fetch.raw_jobs[: settings.max_jobs_per_source]:
            normalized = normalize(raw, source.platform, source.name)
            if not normalized or not normalized.title or not normalized.application_url:
                counts.failed_jobs += 1
                continue
            counts.normalized += 1

            location = parse_location(normalized.location_text, normalized.description)
            if not location.india_eligible:
                counts.filtered_location += 1
                continue

            # Keep every genuine India posting. Seniority is a tag, not an
            # exclusion criterion: the portal serves fresher through experienced.
            relevance = score_relevance(
                normalized.title, normalized.description, normalized.employment_type_raw
            )
            experience = extract_experience(
                f"{normalized.title}\n{(normalized.description or '')[:3000]}"
            )
            counts.candidates += 1
            hash_value = dedupe_hash(
                normalized.title, source.name, location.city, normalized.application_url
            )
            sha = content_hash(normalized.title, normalized.description)

            existing = (
                await db.execute(
                    select(Job).where(
                        Job.source_id == source.id, Job.source_job_id == normalized.source_job_id
                    )
                )
            ).scalar_one_or_none()

            duplicate = (
                await db.execute(select(Job.id).where(Job.dedupe_hash == hash_value).limit(1))
            ).scalar_one_or_none()
            if duplicate and not existing:
                counts.duplicates += 1
                continue

            job_id = existing.id if existing else uuid.uuid4()
            fallback = _fallback_fields(
                normalized.title, relevance, location, normalized.employment_type_raw, experience
            )
            outcome = await classify_job(
                title=normalized.title,
                location=location.normalized_location,
                description=normalized.description,
                content_hash=sha,
            )
            fields = dict(fallback)
            classification_record: Classification | None = None
            if outcome and not outcome.error:
                result = outcome.result
                # Don't let a weak "Other" from the model override a specific
                # category the deterministic rules inferred from the title.
                ai_role = result.role_category
                heuristic_role = fields.get("role_category")
                if (
                    ai_role.value == "Other"
                    and heuristic_role is not None
                    and heuristic_role.value != "Other"
                ):
                    ai_role = heuristic_role
                fields.update(
                    role_category=ai_role,
                    experience_level=result.experience_level,
                    employment_type=result.job_type,
                    workplace_type=result.workplace_type,
                    city=result.city or location.city,
                    fresher_friendly=result.fresher_suitability,
                    skills=result.skills,
                    degree_requirements=result.degree_requirements,
                    classification_confidence=result.confidence,
                    classification_reasoning=result.reasoning,
                    classification_failed=False,
                )
                fields["experience_min"] = result.min_experience
                fields["experience_max"] = result.max_experience
                counts.classified += 1
                classification_record = Classification(
                    job_id=job_id,
                    model=outcome.model,
                    content_hash=sha,
                    result=result.model_dump(mode="json"),
                    cache_hit=outcome.cache_hit,
                    prompt_tokens=outcome.prompt_tokens,
                    completion_tokens=outcome.completion_tokens,
                    latency_ms=outcome.latency_ms,
                )
            elif outcome and outcome.error:
                fields["classification_failed"] = True
                fields["classification_confidence"] = None

            values: dict[str, Any] = dict(
                id=job_id,
                source_id=source.id,
                source_job_id=normalized.source_job_id,
                dedupe_hash=hash_value,
                content_hash=sha,
                company_id=company.id,
                title=normalized.title,
                description=normalized.description,
                original_location=normalized.location_text,
                normalized_location=location.normalized_location,
                country=location.country,
                city=fields["city"],
                state=location.state,
                workplace_type=fields["workplace_type"],
                remote_scope=location.remote_scope,
                india_eligible=True,
                employment_type=fields["employment_type"],
                department=_text(normalized.department),
                application_url=normalized.application_url,
                posted_at=normalized.posted_at,
                last_seen_at=datetime.now(timezone.utc),
                last_checked_at=datetime.now(timezone.utc),
                last_source_confirmed_at=datetime.now(timezone.utc),
                missing_count=0,
                status=JobStatus.ACTIVE,
                experience_min=fields.get("experience_min", experience.min_years),
                experience_max=fields.get("experience_max", experience.max_years),
                role_category=fields["role_category"],
                experience_level=fields["experience_level"],
                fresher_friendly=fields["fresher_friendly"],
                classification_confidence=fields.get("classification_confidence"),
                classification_reasoning=fields.get("classification_reasoning"),
                classification_source="gemini" if outcome and not outcome.error else "deterministic",
                classification_failed=fields.get("classification_failed", False),
                relevance_state=relevance.state,
                relevance_score=relevance.score,
                relevance_reasons=relevance.reasons,
                skills=fields["skills"],
                degree_requirements=fields["degree_requirements"],
                raw_source_data=normalized.raw,
            )
            if existing:
                changed = any(
                    getattr(existing, key) != value
                    for key, value in values.items()
                    if key not in {"last_seen_at", "last_checked_at", "last_source_confirmed_at", "missing_count", "status"}
                )
                for key, value in values.items():
                    setattr(existing, key, value)
                if changed:
                    counts.updated += 1
                else:
                    counts.unchanged += 1
            else:
                db.add(Job(**values))
                counts.new += 1

            # Add after the Job so the FK target is present in the same flush.
            if classification_record is not None:
                db.add(classification_record)

        # Freshness applies only after a successful fetch.
        unseen = (
            await db.execute(
                select(Job).where(Job.source_id == source.id, Job.last_seen_at < started_at)
            )
        ).scalars().all()
        now = datetime.now(timezone.utc)
        for job in unseen:
            decision = decide_freshness(
                seen_in_fetch=False,
                fetch_succeeded=True,
                current_status=job.status,
                missing_count=job.missing_count,
                last_confirmed_at=job.last_source_confirmed_at,
                now=now,
            )
            job.status = decision.status
            job.missing_count = decision.missing_count
            job.last_checked_at = now

        source.job_count = int(
            (
                await db.execute(
                    select(func.count()).select_from(Job).where(Job.source_id == source.id)
                )
            ).scalar_one()
        )
        source.health_status = SourceHealth.HEALTHY
        source.last_success_at = now
        source.last_error = None
        await db.commit()

        logger.info(
            "source_ingested",
            source=source.name,
            platform=source.platform,
            raw=counts.raw,
            new=counts.new,
            updated=counts.updated,
            duplicates=counts.duplicates,
            filtered_location=counts.filtered_location,
            filtered_relevance=counts.filtered_relevance,
        )
    return counts


async def ingest_all() -> dict:
    started_at = datetime.now(timezone.utc)
    run = IngestionRun(started_at=started_at, status="running")
    async with AsyncSessionLocal() as db:
        db.add(run)
        await db.commit()
        await db.refresh(run)
        run_id = run.id

    async with AsyncSessionLocal() as db:
        sources = await load_enabled_sources(db)

    semaphore = asyncio.Semaphore(settings.ingest_concurrency)

    async def guarded(source: Source) -> SourceCounts:
        async with semaphore:
            return await ingest_source(source.id, run_id, started_at)

    results = await asyncio.gather(*(guarded(source) for source in sources), return_exceptions=True)
    totals = RunCounts()
    for result in results:
        if isinstance(result, Exception):
            logger.error("source_task_crashed", error=str(result))
            totals.failed_sources += 1
        else:
            totals.merge(result)

    finished = datetime.now(timezone.utc)
    async with AsyncSessionLocal() as db:
        run = (await db.execute(select(IngestionRun).where(IngestionRun.id == run_id))).scalar_one_or_none()
        if run:
            run.finished_at = finished
            run.duration_ms = int((finished - started_at).total_seconds() * 1000)
            run.status = "completed" if totals.failed_sources == 0 else "completed_with_errors"
            run.raw_jobs = totals.raw
            run.normalized_jobs = totals.normalized
            run.candidate_jobs = totals.candidates
            run.classified_jobs = totals.classified
            run.new_jobs = totals.new
            run.updated_jobs = totals.updated
            run.unchanged_jobs = totals.unchanged
            run.duplicates = totals.duplicates
            run.failed_sources = totals.failed_sources
            await db.commit()

    logger.info("ingestion_completed", run_id=str(run_id), totals=totals.__dict__)
    return {"run_id": str(run_id), **totals.__dict__}


def _fallback_fields(title, relevance, location, employment_type_raw, experience) -> dict:
    from app.ingestion.fallback import deterministic_fields

    return deterministic_fields(
        title=title,
        relevance=relevance,
        location=location,
        employment_type_raw=employment_type_raw,
        experience=experience,
    )


def _text(value: Any) -> str | None:
    """Coerce unexpected ATS category objects to a string for VARCHAR columns."""
    if value is None:
        return None
    if isinstance(value, dict):
        value = value.get("name") or value.get("label") or value.get("title")
    elif isinstance(value, list) and value:
        value = value[0]
        if isinstance(value, dict):
            value = value.get("name") or value.get("label") or value.get("title")
    text = str(value).strip() if value is not None else ""
    return text[:255] or None
