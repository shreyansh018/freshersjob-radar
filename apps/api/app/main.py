from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.errors import AppError, app_error_handler
from app.core.logging import configure_logging, get_logger
from app.core.security import tokens_match

logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("api_started", environment=settings.environment, ai_enabled=settings.ai_enabled)
    yield
    logger.info("api_stopped")


app = FastAPI(
    title="FreshersJob Radar API",
    version="0.1.0",
    description="Real India fresher jobs from public ATS sources, classified and searchable.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)


@app.middleware("http")
async def csrf_protection(request: Request, call_next):
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        uses_cookie = bool(request.cookies.get("frj_token"))
        has_bearer = request.headers.get("Authorization", "").lower().startswith("bearer ")
        if uses_cookie and not has_bearer:
            cookie_csrf = request.cookies.get("csrf_token")
            header_csrf = request.headers.get("X-CSRF-Token")
            if not tokens_match(header_csrf, cookie_csrf):
                return JSONResponse(status_code=403, content={"detail": "CSRF token missing or invalid"})
    return await call_next(request)


app.include_router(api_router)
