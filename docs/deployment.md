# Deploy to Vercel

The app runs as one Vercel project with two Services (`apps/web` and
`apps/api`) on a shared domain. The UI keeps calling relative `/api/v1` paths,
so the HttpOnly cookie and CSRF flow are unchanged. Docker Compose remains the
local development path.

## What Vercel does not provide

| Need | Local Docker | Vercel |
|---|---|---|
| Postgres | `postgres` container | External Postgres (Neon, Supabase, etc.) |
| Redis | `redis` container | External Redis (Upstash) for the Gemini cache/rate limit |
| Celery worker | long-running container | Vercel Queues subscriber (`app.workers.worker:app`) |
| Celery Beat | long-running container | Vercel Cron → `/api/v1/internal/cron/*` |
| Gemini budget | one process | Redis-backed shared limiter |

A full ingestion took **23 minutes** on one occasion (other runs: 26–93s).
`ingest_all` therefore only runs in Docker. On Vercel the daily cron enqueues
`ingest_one_source_task` once per enabled board, so each invocation stays well
inside the 300s Hobby function limit.

## 1. Prepare the database

Create a Postgres database on your provider, then dump the local database so
the live site shows the same real jobs (no invented data):

```powershell
# from the repo root
docker compose exec -T postgres pg_dump -U freshers -d freshersjobs -Fc > data/frj.dump
```

Use your provider's connection string to build two URLs. Note the different SSL
query parameters — asyncpg uses `ssl`, psycopg uses `sslmode`:

```dotenv
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST/DB?ssl=require
DATABASE_SYNC_URL=postgresql+psycopg://USER:PASSWORD@HOST/DB?sslmode=require
```

URL-encode any special characters in the password. Restore with a throwaway
Postgres container (no local `pg_restore` needed):

```powershell
docker run --rm -v "${PWD}/data:/data" postgres:16-alpine `
  pg_restore --clean --if-exists -h HOST -U USER -d DB /data/frj.dump
```

The dump contains the existing admin user. Replace its password before going
public (this script also promotes an existing user to admin):

```powershell
$env:DATABASE_URL = "postgresql+asyncpg://USER:PASSWORD@HOST/DB?ssl=require"
$env:ADMIN_EMAIL = "you@example.com"
$env:ADMIN_PASSWORD = "a-long-random-password"
.\.venv\Scripts\python scripts/create_admin.py
```

Do not commit `data/frj.dump` — it contains password hashes.

## 2. Configure Vercel

Create the project from the GitHub repo. Vercel reads the root `vercel.json`.
Set these Project Environment Variables for Production:

| Variable | Value |
|---|---|
| `ENVIRONMENT` | `production` |
| `DATABASE_URL` | asyncpg URL from step 1 |
| `DATABASE_SYNC_URL` | psycopg URL from step 1 |
| `REDIS_URL` | Upstash `rediss://…` URL |
| `CELERY_BROKER_URL` | `vercel://` |
| `CELERY_RESULT_BACKEND` | `vercel-runtime-cache://` |
| `GEMINI_SHARED_RATE_LIMIT` | `true` |
| `GEMINI_API_KEY` | server-side only; never in the frontend |
| `SECRET_KEY` | new random string (invalidates local sessions) |
| `CRON_SECRET` | new random string used by Vercel Cron |
| `REGISTRATION_ENABLED` | `true` for the public demo (sign-up is rate-limited to 5 attempts / 5 min); set `false` if you want an invite-only instance |
| `COOKIE_SECURE` | `true` (also derived automatically from `ENVIRONMENT`) |
| `CORS_ORIGINS` | your `https://<project>.vercel.app` URL |

`vercel.json` contains one daily Cron entry (Hobby accounts are limited to
schedules that run at most once per day). Vercel automatically sends
`Authorization: Bearer $CRON_SECRET` on each GET request:

| Schedule (UTC) | Path | Purpose |
|---|---|---|
| `0 2 * * *` | `/api/v1/internal/cron/ingest` | fan out one ingestion task per source, then expire stale jobs and check source health |

The separate `/api/v1/internal/cron/freshness` and `/cron/source-health` routes
still exist. On Pro you can add hourly and six-hourly Cron entries pointing at
them to restore the original Celery Beat cadence.

If you move to Pro and want a single large task instead of the fan-out, raise
`maxDuration` for `app/main.py` in the `api` service (up to 800s; 300s is the
Hobby maximum). The fan-out is still the safer default.

## 3. Deploy and verify

Push to the connected branch, then check the production URL:

1. `/api/v1/health` → `{"status":"ok","database":"ok","redis":"ok"}`.
2. Landing stats show the restored real jobs (`689` at cutover; daily ingestion
   grows this honestly).
3. Sign in with the admin account → navbar shows `Hi, <name>`.
4. Save a job, edit preferences, open the admin overview.
5. `POST /api/v1/internal/cron/ingest` without the secret → `401`; with the
   secret → `200` and a queued task id.
6. `vercel inspect <deployment>` lists both `services/api/fastapi` and
   `services/api/_py_subscribers/app-workers-worker__app`.
7. Browser console is clean; job detail links still go to employer sites.

## Known limitations

- Vercel Queues and Services are beta on all plans. If the subscriber fails to
  build, keep the Cron endpoints but invoke a small batch of sources directly
  from the route instead of queuing.
- Gemini Free Tier can still hit its daily quota; deterministic tagging keeps
  every job honest when that happens.
- The auth rate limiter is per function instance. Move it to Redis if the demo
  is exposed to real traffic.
- Each fanned-out source gets its own `ingestion_runs` row, so the admin
  "Last ingestion" card shows that source's counts rather than a full-cycle
  total. Aggregate rows if you need a single daily number.
