from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False
    )

    environment: str = "local"
    secret_key: str = "change-me-in-production"
    cors_origins: str = "http://localhost:8080"

    postgres_user: str = "freshers"
    postgres_password: str = "freshers_password"
    postgres_db: str = "freshersjobs"
    database_url: str = "postgresql+asyncpg://freshers:freshers_password@postgres:5432/freshersjobs"
    database_sync_url: str = "postgresql+psycopg://freshers:freshers_password@postgres:5432/freshersjobs"

    redis_url: str = "redis://redis:6379/1"
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/2"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    gemini_max_description_chars: int = 12000
    # Free-tier Gemini allows ~5 generate_content requests/minute. Space calls
    # out slightly beyond that and retry throttled requests with backoff.
    gemini_min_interval_seconds: float = 13.0
    gemini_rate_limit_retries: int = 3
    # On Vercel every invocation is a separate process, so the in-process
    # limiter cannot enforce a shared budget. Redis-backed throttling keeps all
    # invocations under the same free-tier quota.
    gemini_shared_rate_limit: bool = False

    # Shared secret for the internal cron endpoints (Vercel Cron sends it as a
    # bearer token). Empty disables them locally.
    cron_secret: str = ""
    # Public demo can leave registration open; a public deployment should set
    # this to false and provision accounts out of band.
    registration_enabled: bool = True
    # Override cookie Secure flag; defaults on when environment is production.
    cookie_secure: bool | None = None

    ingest_concurrency: int = 8
    http_timeout_seconds: int = 15
    http_max_retries: int = 3
    max_jobs_per_source: int = 1000

    stale_after_misses: int = 3
    expire_after_days_unconfirmed: int = 14
    new_job_days: int = 3

    access_token_expire_minutes: int = 60 * 24 * 7

    @property
    def is_production(self) -> bool:
        return self.environment.strip().lower() in {"production", "prod"}

    @property
    def cookie_secure_enabled(self) -> bool:
        if self.cookie_secure is not None:
            return self.cookie_secure
        return self.is_production

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def ai_enabled(self) -> bool:
        return bool(self.gemini_api_key and self.gemini_api_key not in {"your_gemini_api_key_here", "changeme"})


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
