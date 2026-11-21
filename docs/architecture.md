# Architecture

## Components

| Component | Tech | Role |
|---|---|---|
| Web | React + Vite + TypeScript + Tailwind + shadcn-style UI | Search UI, filters, saved jobs, admin view |
| API | FastAPI + Pydantic v2 + SQLAlchemy 2.0 async | REST API, validation, auth, admin |
| Database | PostgreSQL 16 | Jobs, sources, companies, runs, users, AI usage |
| Broker/cache | Redis 7 | Celery broker/results, classification cache |
| Workers | Celery (worker + beat) | Ingestion, classification, freshness, health |
| AI | Google Gemini via `google-genai` | Structured role/level/skills/city classification |

## Flow

```
Public ATS boards
  -> fetchers (httpx, retry/backoff, per-source isolation)
  -> normalize -> India eligibility -> relevance screening
  -> dedupe -> Gemini classification (content-hash cached)
  -> PostgreSQL upsert -> freshness -> FastAPI -> React
```

## Key design rules

1. **No fabricated data.** Only public postings; no seed jobs.
2. **Source-driven.** Adding an ATS board is a DB row + optional adapter, not a pipeline rewrite.
3. **Deterministic first.** Location, experience and relevance are code, not AI.
4. **Auditable.** Relevance reasons, classification reasoning, source links and freshness timestamps are stored.
5. **Cautious freshness.** A failed fetch never expires a job. Only repeated successful misses mark stale/expired.
6. **Bounded AI spend.** Content-hash cache, description truncation, token metering.

## Database

`apps/api/app/models/` holds SQLAlchemy models; Alembic revision `0001_initial` creates the schema and indexes (FTS `to_tsvector`, trigram on title/company/city, GIN on skills).

## Schedules (Celery Beat)

| Task | Cadence | Queue |
|---|---|---|
| `ingestion.ingest_all` | daily (86,400s) | ingestion |
| `maintenance.expire_unconfirmed` | hourly | maintenance |
| `maintenance.source_health` | every 6h | maintenance |
