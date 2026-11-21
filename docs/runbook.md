# Runbook

## First run

1. `cp .env.example .env` and set `GEMINI_API_KEY`.
2. `docker compose up -d --build`
3. `python scripts/seed_sources.py` (from repo root, host Python with deps installed) or run it inside the API container:
   `docker compose exec api python /app/../scripts/seed_sources.py` — simpler: `docker compose run --rm api python scripts/seed_sources.py` after copying scripts into the image, or run from host with a venv.
4. `docker compose run --rm -v "${PWD}:/repo" -w /repo api python scripts/run_ingestion.py`
5. `python scripts/check_sources.py` to validate coverage.

## Common commands

```bash
docker compose logs -f api worker beat       # follow logs
docker compose restart worker                # apply code changes to worker
docker compose exec api alembic upgrade head # apply migrations
docker compose exec api pytest               # unit tests
docker compose exec api pytest -k api        # API tests (needs RUN_DB_TESTS=1)
docker compose down -v                       # full reset (deletes DB volume)
```

## Failure handling

| Symptom | Check |
|---|---|
| No jobs appear | Source coverage (`check_sources.py`), ingestion run counts, `sources.last_error` |
| API 500 on search | Alembic applied? `docker compose exec api alembic current` |
| AI tags are "Unknown" | `GEMINI_API_KEY` valid? `classification_failed` column in DB |
| Celery tasks never run | Redis health, worker logs, queue names |
| Jobs not expiring | `last_source_confirmed_at`; freshness only reacts to successful fetches |

## Adding a source

1. Add adapter in `apps/api/app/ingestion/fetchers/` if the platform is new.
2. Register it in `fetchers/factory.py`.
3. Insert a `sources` row (via `seed_sources.py` pattern or admin/DB).
4. Run `check_sources.py` and confirm India eligibility yield.
