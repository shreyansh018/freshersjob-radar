import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import EmploymentType, ExperienceLevel, JobStatus, RoleCategory, WorkplaceType


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CompanyMini(ORMModel):
    id: uuid.UUID
    name: str
    logo_url: str | None = None
    website: str | None = None


class SourceMini(ORMModel):
    id: uuid.UUID
    name: str
    platform: str


class JobSummary(ORMModel):
    id: uuid.UUID
    title: str
    company: CompanyMini | None = None
    source: SourceMini | None = None
    normalized_location: str | None = None
    city: str | None = None
    country: str | None = None
    workplace_type: WorkplaceType = WorkplaceType.UNKNOWN
    employment_type: EmploymentType = EmploymentType.UNKNOWN
    experience_level: ExperienceLevel | None = None
    role_category: RoleCategory | None = None
    fresher_friendly: bool = False
    status: JobStatus = JobStatus.ACTIVE
    posted_at: datetime | None = None
    first_seen_at: datetime
    last_checked_at: datetime | None = None
    skills: list[str] = Field(default_factory=list)
    application_url: str
    is_new: bool = False
    recently_verified: bool = False


class JobDetail(JobSummary):
    description: str | None = None
    original_location: str | None = None
    state: str | None = None
    department: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    salary_currency: str | None = None
    experience_min: float | None = None
    experience_max: float | None = None
    classification_confidence: float | None = None
    classification_reasoning: str | None = None
    classification_source: str | None = None
    degree_requirements: list[str] = Field(default_factory=list)
    last_seen_at: datetime | None = None
    last_source_confirmed_at: datetime | None = None


class PaginatedJobs(BaseModel):
    items: list[JobSummary]
    total: int
    page: int
    limit: int
    has_more: bool


class JobFilters(BaseModel):
    q: str | None = Field(default=None, max_length=200)
    company: str | None = None
    location: str | None = None
    city: str | None = None
    role_category: RoleCategory | None = None
    experience_level: ExperienceLevel | None = None
    employment_type: EmploymentType | None = None
    workplace_type: WorkplaceType | None = None
    remote: bool | None = None
    skills: str | None = None
    posted_after: date | None = None
    sort: str = Field(default="relevance", pattern="^(relevance|newest|oldest)$")
    page: int = Field(default=1, ge=1, le=10000)
    limit: int = Field(default=20, ge=1, le=100)


class CategoryCount(BaseModel):
    name: str
    count: int


class StatsResponse(BaseModel):
    total_active_jobs: int
    fresher_friendly_jobs: int
    internships: int
    new_jobs_today: int
    companies: int
    cities: int
    role_categories: list[CategoryCount]
    top_cities: list[CategoryCount]
