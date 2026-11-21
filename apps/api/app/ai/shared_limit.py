"""Shared Gemini rate limiting.

Locally a single process handles every call, so an in-process lock is enough.
On Vercel each invocation is a separate process; the Redis-backed path gives
all invocations one budget instead of one budget per function instance.

The Redis path is a sliding window implemented with ``SET ... PX NX``: the key
lives for exactly the configured minimum interval, so a new call can only be
reserved after the previous reservation expires. A daily-quota flag is stored
with a TTL so a throttled deployment stops making pointless calls.
"""

import asyncio
import time

from redis.asyncio import from_url

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("ai.shared_limit")

_SLOT_KEY = "frj:gemini:slot"
_QUOTA_KEY = "frj:gemini:quota_exhausted"
_QUOTA_TTL_SECONDS = 6 * 60 * 60

_local_lock = asyncio.Lock()
_local_last_call = 0.0
_local_quota_exhausted = False


async def _local_slot() -> None:
    global _local_last_call
    async with _local_lock:
        wait = settings.gemini_min_interval_seconds - (time.monotonic() - _local_last_call)
        if wait > 0:
            await asyncio.sleep(wait)
        _local_last_call = time.monotonic()


async def wait_for_slot() -> None:
    """Reserve the next Gemini call slot across all invocations."""
    if not settings.gemini_shared_rate_limit:
        await _local_slot()
        return

    client = from_url(settings.redis_url)
    interval_ms = max(1, int(settings.gemini_min_interval_seconds * 1000))
    try:
        while True:
            # SET ... PX NX is supported by every redis-py version we target;
            # psetex() here has no nx parameter.
            acquired = await client.set(_SLOT_KEY, "1", px=interval_ms, nx=True)
            if acquired:
                return
            await asyncio.sleep(1)
    except Exception as exc:  # Redis outage must not block ingestion entirely
        logger.warning("shared_rate_limit_fallback", error=str(exc))
        await _local_slot()
    finally:
        await client.aclose()


async def quota_exhausted() -> bool:
    if not settings.gemini_shared_rate_limit:
        return _local_quota_exhausted
    client = from_url(settings.redis_url)
    try:
        return bool(await client.get(_QUOTA_KEY))
    except Exception as exc:
        logger.warning("shared_quota_flag_read_failed", error=str(exc))
        return _local_quota_exhausted
    finally:
        await client.aclose()


async def mark_quota_exhausted() -> None:
    global _local_quota_exhausted
    _local_quota_exhausted = True
    if not settings.gemini_shared_rate_limit:
        return
    client = from_url(settings.redis_url)
    try:
        await client.setex(_QUOTA_KEY, _QUOTA_TTL_SECONDS, "1")
    except Exception as exc:
        logger.warning("shared_quota_flag_write_failed", error=str(exc))
    finally:
        await client.aclose()
