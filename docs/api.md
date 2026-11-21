# API reference

Base URL: `http://localhost:8000/api/v1` (or `http://localhost:8080/api/v1` through the web container).

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | DB + Redis health |
| GET | `/jobs` | Search: `q, company, city, location, role_category, experience_level, employment_type, workplace_type, remote, skills, posted_after, sort, page, limit` |
| GET | `/jobs/{id}` | Full detail + classification + freshness |
| GET | `/jobs/{id}/related` | Related postings |
| GET | `/stats` | Counts, categories, cities |
| GET | `/categories`, `/locations` | Filter options |
| POST | `/auth/register`, `/auth/login`, `/auth/logout` | Auth (cookie + bearer) |
| GET | `/auth/me` | Current user |
| GET/POST/DELETE | `/users/me/saved-jobs[/{job_id}]` | Saved jobs (auth) |
| GET/PUT | `/users/me/preferences` | Preferences (auth) |
| GET | `/admin/overview`, `/admin/sources`, `/admin/ingestion-runs` | Monitoring (admin) |
| POST | `/admin/ingestion/run`, `/admin/sources/{id}/toggle` | Controls (admin) |

Paginated list response: `{ "items": [...], "total": n, "page": p, "limit": l, "has_more": bool }`.

Error response: `{ "error": { "code": "...", "message": "...", "details": null } }` for app errors, or `{ "detail": "..." }` for framework validation/HTTP errors.
