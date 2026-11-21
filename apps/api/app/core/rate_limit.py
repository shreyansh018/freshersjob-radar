"""Small in-process rate limiter for auth endpoints.

For multi-instance production deployments replace this with a Redis-backed limiter.
"""

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

_hits: dict[str, deque[float]] = defaultdict(deque)


def rate_limit(request: Request, key: str, limit: int = 10, window_seconds: int = 60) -> None:
    identity = request.client.host if request.client else "unknown"
    bucket = f"{key}:{identity}"
    now = time.time()
    queue = _hits[bucket]
    while queue and queue[0] < now - window_seconds:
        queue.popleft()
    if len(queue) >= limit:
        raise HTTPException(status_code=429, detail="Too many requests. Try again shortly.")
    queue.append(now)
