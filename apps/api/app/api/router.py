from fastapi import APIRouter

from app.api.v1.routers import admin, auth, health, internal, jobs, stats, users

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(jobs.router)
api_router.include_router(stats.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(admin.router)
api_router.include_router(internal.router)
