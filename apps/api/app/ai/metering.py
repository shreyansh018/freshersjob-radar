"""Cost estimation.

Pricing is a configurable approximation. Verify against the current Gemini
price sheet before publishing a cost report. Values are USD per 1M tokens.
"""

from app.core.config import settings

PRICING_USD_PER_1M: dict[str, tuple[float, float]] = {
    "gemini-3.8-flash": (0.30, 2.50),
    "gemini-3.7-flash": (0.30, 2.50),
    "gemini-3.6-flash": (0.30, 2.50),
    "gemini-3.5-flash": (0.30, 2.50),
    "gemini-2.5-flash": (0.30, 2.50),
    "gemini-2.0-flash": (0.10, 0.40),
    "gemini-1.5-flash": (0.075, 0.30),
}


def estimate_cost_usd(prompt_tokens: int, completion_tokens: int, model: str | None = None) -> float:
    model = model or settings.gemini_model
    prompt_rate, completion_rate = PRICING_USD_PER_1M.get(model, (0.30, 2.50))
    return (prompt_tokens * prompt_rate + completion_tokens * completion_rate) / 1_000_000
