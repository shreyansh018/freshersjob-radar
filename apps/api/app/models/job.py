import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import (
    EmploymentType,
    ExperienceLevel,
    JobStatus,
    RemoteScope,
    RelevanceState,
    RoleCategory,
    SourceHealth,
    WorkplaceType,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def DateTimeTz() -> DateTime:
    return DateTime(timezone=True)


def _enum(enum_cls: type[Enum]) -> SAEnum:
    return SAEnum(
        enum_cls,
        native_enum=False,
        values_callable=lambda values: [v.value for v in values],
        length=64,
    )


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    website: Mapped[str | None] = mapped_column(String(512))
    logo_url: Mapped[str | None] = mapped_column(String(512))
    industry: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTimeTz(), default=_now)

    jobs: Mapped[list["Job"]] = relationship(back_populates="company")

    __table_args__ = (UniqueConstraint("name", name="uq_companies_name"),)


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("companies.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    platform: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    board_identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    config: Mapped[dict] = mapped_column(JSONB, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fetch_interval_minutes: Mapped[int] = mapped_column(Integer, default=1440)
    last_fetch_at: Mapped[datetime | None] = mapped_column(DateTimeTz())
    last_success_at: Mapped[datetime | None] = mapped_column(DateTimeTz())
    last_error: Mapped[str | None] = mapped_column(Text)
    health_status: Mapped[SourceHealth] = mapped_column(_enum(SourceHealth), default=SourceHealth.UNKNOWN)
    job_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTimeTz(), default=_now)

    company: Mapped[Company | None] = relationship()
    jobs: Mapped[list["Job"]] = relationship(back_populates="source")

    __table_args__ = (
        UniqueConstraint("platform", "board_identifier", name="uq_sources_platform_board"),
    )


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True)
    source_job_id: Mapped[str] = mapped_column(String(255), nullable=False)
    dedupe_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    company_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("companies.id", ondelete="SET NULL"), index=True)

    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    original_location: Mapped[str | None] = mapped_column(String(512))
    normalized_location: Mapped[str | None] = mapped_column(String(512))
    country: Mapped[str | None] = mapped_column(String(100))
    city: Mapped[str | None] = mapped_column(String(120), index=True)
    state: Mapped[str | None] = mapped_column(String(120))
    workplace_type: Mapped[WorkplaceType] = mapped_column(_enum(WorkplaceType), default=WorkplaceType.UNKNOWN)
    remote_scope: Mapped[RemoteScope] = mapped_column(_enum(RemoteScope), default=RemoteScope.UNKNOWN)
    india_eligible: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    employment_type: Mapped[EmploymentType] = mapped_column(_enum(EmploymentType), default=EmploymentType.UNKNOWN)
    department: Mapped[str | None] = mapped_column(String(255))
    application_url: Mapped[str] = mapped_column(String(1024), nullable=False)

    posted_at: Mapped[datetime | None] = mapped_column(DateTimeTz(), index=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTimeTz(), default=_now)
    last_seen_at: Mapped[datetime] = mapped_column(DateTimeTz(), default=_now)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTimeTz())
    last_source_confirmed_at: Mapped[datetime | None] = mapped_column(DateTimeTz())
    missing_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[JobStatus] = mapped_column(_enum(JobStatus), default=JobStatus.ACTIVE, index=True)

    salary_min: Mapped[float | None] = mapped_column(Float)
    salary_max: Mapped[float | None] = mapped_column(Float)
    salary_currency: Mapped[str | None] = mapped_column(String(16))

    experience_min: Mapped[float | None] = mapped_column(Float)
    experience_max: Mapped[float | None] = mapped_column(Float)
    role_category: Mapped[RoleCategory | None] = mapped_column(_enum(RoleCategory), index=True)
    experience_level: Mapped[ExperienceLevel | None] = mapped_column(_enum(ExperienceLevel), index=True)
    fresher_friendly: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    classification_confidence: Mapped[float | None] = mapped_column(Float)
    classification_reasoning: Mapped[str | None] = mapped_column(Text)
    classification_source: Mapped[str | None] = mapped_column(String(32))
    classification_failed: Mapped[bool] = mapped_column(Boolean, default=False)

    relevance_state: Mapped[RelevanceState] = mapped_column(_enum(RelevanceState), default=RelevanceState.UNCERTAIN)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    relevance_reasons: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    skills: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    degree_requirements: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    raw_source_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    duplicate_of: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="SET NULL"))

    created_at: Mapped[datetime] = mapped_column(DateTimeTz(), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTimeTz(), default=_now, onupdate=_now)

    source: Mapped[Source] = relationship(back_populates="jobs")
    company: Mapped[Company | None] = relationship(back_populates="jobs")
    classifications: Mapped[list["Classification"]] = relationship(back_populates="job")

    __table_args__ = (
        UniqueConstraint("source_id", "source_job_id", name="uq_jobs_source_external"),
        Index("ix_jobs_active_posted", "status", "posted_at"),
        Index("ix_jobs_active_role", "status", "role_category"),
        Index("ix_jobs_active_city", "status", "city"),
        Index("ix_jobs_skills_gin", "skills", postgresql_using="gin"),
    )


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    started_at: Mapped[datetime] = mapped_column(DateTimeTz(), default=_now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTimeTz())
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), default="running")
    raw_jobs: Mapped[int] = mapped_column(Integer, default=0)
    normalized_jobs: Mapped[int] = mapped_column(Integer, default=0)
    candidate_jobs: Mapped[int] = mapped_column(Integer, default=0)
    classified_jobs: Mapped[int] = mapped_column(Integer, default=0)
    new_jobs: Mapped[int] = mapped_column(Integer, default=0)
    updated_jobs: Mapped[int] = mapped_column(Integer, default=0)
    unchanged_jobs: Mapped[int] = mapped_column(Integer, default=0)
    duplicates: Mapped[int] = mapped_column(Integer, default=0)
    failed_sources: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text)

    source_runs: Mapped[list["IngestionSourceRun"]] = relationship(back_populates="run")


class IngestionSourceRun(Base):
    __tablename__ = "ingestion_source_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ingestion_runs.id", ondelete="CASCADE"), index=True)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"), index=True)
    http_status: Mapped[int | None] = mapped_column(Integer)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    jobs_received: Mapped[int] = mapped_column(Integer, default=0)
    jobs_failed: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTimeTz(), default=_now)

    run: Mapped[IngestionRun] = relationship(back_populates="source_runs")
    source: Mapped[Source] = relationship()


class Classification(Base):
    __tablename__ = "classifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    model: Mapped[str] = mapped_column(String(100))
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    result: Mapped[dict] = mapped_column(JSONB, default=dict)
    cache_hit: Mapped[bool] = mapped_column(Boolean, default=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTimeTz(), default=_now)

    job: Mapped[Job] = relationship(back_populates="classifications")
