import json

from redis.asyncio import from_url

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("ai.cache")
CACHE_PREFIX = "frj:classification:"
CACHE_TTL_SECONDS = 30 * 24 * 60 * 60


async def get_cached(content_hash: str) -> dict | None:
    if not settings.ai_enabled:
        return None
    client = from_url(settings.redis_url)
    try:
        raw = await client.get(f"{CACHE_PREFIX}{content_hash}")
        return json.loads(raw) if raw else None
    except Exception as exc:
        logger.warning("classification_cache_read_failed", error=str(exc))
        return None
    finally:
        await client.aclose()


async def set_cached(content_hash: str, payload: dict) -> None:
    if not settings.ai_enabled:
        return
    client = from_url(settings.redis_url)
    try:
        await client.setex(f"{CACHE_PREFIX}{content_hash}", CACHE_TTL_SECONDS, json.dumps(payload))
    except Exception as exc:
        logger.warning("classification_cache_write_failed", error=str(exc))
    finally:
        await client.aclose()
