import asyncio
import json
import re
import time
from dataclasses import dataclass

from app.ai.cache import get_cached, set_cached
from app.ai.prompts import SCHEMA, build_prompt
from app.ai.schema import ClassificationResult
from app.ai.shared_limit import mark_quota_exhausted, quota_exhausted, wait_for_slot
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("ai.classifier")


@dataclass
class ClassificationOutcome:
    result: ClassificationResult
    cache_hit: bool
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int
    model: str
    error: str | None = None


def _extract_json(text: str) -> dict:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in model response")
    return json.loads(cleaned[start : end + 1])


def _call_gemini(prompt: str):
    from google import genai

    client = genai.Client(api_key=settings.gemini_api_key)
    return client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": SCHEMA,
            "temperature": 0,
        },
    )


# Rate limiting lives in shared_limit so local Docker and Vercel share the
# same logic while only Vercel needs the Redis-backed global budget.
_RETRY_SECONDS = re.compile(r"retry in\s+([0-9]+(?:\.[0-9]+)?)s", re.I)


def _is_rate_limit(exc: Exception) -> bool:
    text = str(exc)
    return "429" in text or "RESOURCE_EXHAUSTED" in text.lower() or "rate limit" in text.lower()


def _is_daily_quota(exc: Exception) -> bool:
    """Daily/plan quota (unlike a per-minute limit) won't recover on retry."""
    text = str(exc).lower()
    return "exceeded your current quota" in text or "check your plan and billing" in text


def _retry_delay(exc: Exception, attempt: int) -> float:
    match = _RETRY_SECONDS.search(str(exc))
    if match:
        return min(float(match.group(1)) + 0.5, 60.0)
    return min(2.0**attempt, 30.0)


async def classify_job(
    *, title: str, location: str | None, description: str | None, content_hash: str
) -> ClassificationOutcome | None:
    """Return None when AI is disabled or unavailable; callers apply deterministic fallbacks."""
    if not settings.ai_enabled or await quota_exhausted():
        return None

    cached = await get_cached(content_hash)
    if cached:
        return ClassificationOutcome(
            result=ClassificationResult.model_validate(cached),
            cache_hit=True,
            prompt_tokens=0,
            completion_tokens=0,
            latency_ms=0,
            model=settings.gemini_model,
        )

    prompt = build_prompt(title, location, description, settings.gemini_max_description_chars)
    started = time.monotonic()
    last_error: Exception | None = None
    for attempt in range(settings.gemini_rate_limit_retries + 1):
        await wait_for_slot()
        # Another invocation may have tripped the daily quota while we waited
        # for our slot; skip the call and let the deterministic fallback run.
        if await quota_exhausted():
            return None
        try:
            response = await asyncio.to_thread(_call_gemini, prompt)
            payload = _extract_json(response.text or "")
            result = ClassificationResult.model_validate(payload)
            usage = getattr(response, "usage_metadata", None)
            prompt_tokens = int(getattr(usage, "prompt_token_count", 0) or 0)
            completion_tokens = int(getattr(usage, "candidates_token_count", 0) or 0)
            latency_ms = int((time.monotonic() - started) * 1000)

            await set_cached(content_hash, result.model_dump(mode="json"))
            logger.info(
                "job_classified",
                model=settings.gemini_model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_ms=latency_ms,
                role=result.role_category.value,
                attempt=attempt + 1,
            )
            return ClassificationOutcome(
                result=result,
                cache_hit=False,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_ms=latency_ms,
                model=settings.gemini_model,
            )
        except Exception as exc:
            last_error = exc
            if _is_daily_quota(exc):
                await mark_quota_exhausted()
                logger.warning(
                    "gemini_daily_quota_exhausted",
                    message="Using deterministic tagging for the rest of this run.",
                    title=title[:120],
                )
                break
            if not _is_rate_limit(exc) or attempt >= settings.gemini_rate_limit_retries:
                break
            delay = _retry_delay(exc, attempt)
            logger.warning(
                "gemini_rate_limited",
                attempt=attempt + 1,
                retry_after_seconds=round(delay, 1),
                title=title[:120],
            )
            await asyncio.sleep(delay)

    error_text = str(last_error) if last_error else "classification failed"
    logger.warning("classification_failed", error=error_text, title=title[:120])
    return ClassificationOutcome(
        result=ClassificationResult(),
        cache_hit=False,
        prompt_tokens=0,
        completion_tokens=0,
        latency_ms=int((time.monotonic() - started) * 1000),
        model=settings.gemini_model,
        error=error_text,
    )
