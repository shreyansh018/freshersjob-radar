from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api_jobs import router as jobs_router
from .pipeline.job_storage import initialize_jobs_db

app = FastAPI(
    title="FreshersJob Radar API",
    description="Discover, normalize, classify and search fresher jobs in India.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

initialize_jobs_db()
app.include_router(jobs_router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "freshersjob-radar-api"}