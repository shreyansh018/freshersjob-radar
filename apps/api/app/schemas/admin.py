import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    platform: str
    board_identifier: str
    enabled: bool
    health_status: str
    job_count: int
    last_fetch_at: datetime | None
    last_success_at: datetime | None
    last_error: str | None


class IngestionRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    started_at: datetime
    finished_at: datetime | None
    duration_ms: int | None
    status: str
    raw_jobs: int
    candidate_jobs: int
    new_jobs: int
    updated_jobs: int
    duplicates: int
    failed_sources: int
    error: str | None


class AdminOverview(BaseModel):
    total_jobs: int
    active_jobs: int
    stale_jobs: int
    expired_jobs: int
    sources_enabled: int
    sources_failing: int
    last_ingestion_at: datetime | None
    ai_calls: int
    ai_cache_hits: int
    ai_prompt_tokens: int
    ai_completion_tokens: int
    estimated_ai_cost_usd: float
