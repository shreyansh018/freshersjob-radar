from fastapi import APIRouter, Depends
from redis.asyncio import from_url
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health(db: AsyncSession = Depends(get_db)) -> dict:
    result = {"status": "ok", "database": "ok", "redis": "ok"}
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover - exercised only when DB is down
        result["status"] = "degraded"
        result["database"] = f"error: {type(exc).__name__}"

    client = from_url(settings.redis_url)
    try:
        await client.ping()
    except Exception as exc:  # pragma: no cover
        result["status"] = "degraded"
        result["redis"] = f"error: {type(exc).__name__}"
    finally:
        await client.aclose()

    return result
