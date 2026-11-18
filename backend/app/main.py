from fastapi import FastAPI

app = FastAPI(
    title="FreshersJob Radar API",
    description="Discover, normalize, classify and search fresher jobs in India.",
    version="0.1.0",
)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Lightweight health endpoint for deployment checks."""
    return {"status": "ok", "service": "freshersjob-radar-api"}
