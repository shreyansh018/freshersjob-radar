from fastapi import FastAPI

from .api_jobs import router as jobs_router
from .pipeline.job_storage import initialize_jobs_db

app = FastAPI(
    title="FreshersJob Radar API",
    description="Discover, normalize, classify and search fresher jobs in India.",
    version="0.2.0",
)

# Initialize persistent storage
initialize_jobs_db()

# Register jobs API
app.include_router(jobs_router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Lightweight health endpoint for deployment checks."""
    return {"status": "ok", "service": "freshersjob-radar-api"}