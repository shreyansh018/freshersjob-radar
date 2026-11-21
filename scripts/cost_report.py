"""Report measured Gemini spend and estimated USD per 1,000 classified posts."""

import sys
from datetime import datetime, timezone
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1] / "apps" / "api"
if (API_DIR / "app").exists():
    sys.path.insert(0, str(API_DIR))

from sqlalchemy import Integer, func, select

from app.ai.metering import estimate_cost_usd
from app.core.config import settings
from app.db.session import SyncSessionLocal
from app.models import Classification

REPORT_PATH = Path(__file__).resolve().parents[1] / "docs" / "cost.md"


def main() -> None:
    with SyncSessionLocal() as db:
        row = db.execute(
            select(
                func.count().label("calls"),
                func.coalesce(func.sum(Classification.prompt_tokens), 0),
                func.coalesce(func.sum(Classification.completion_tokens), 0),
                func.coalesce(func.sum(func.cast(Classification.cache_hit, Integer)), 0),
            )
        ).one()
    calls, prompt_tokens, completion_tokens, cache_hits = (int(value) for value in row)
    cost = estimate_cost_usd(prompt_tokens, completion_tokens)
    billable_calls = max(calls - cache_hits, 0)
    per_1000 = (cost / billable_calls * 1000) if billable_calls else 0.0

    content = "\n".join(
        [
            "# Gemini cost report",
            "",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            f"Model: `{settings.gemini_model}`",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            f"| Classification records | {calls} |",
            f"| Cache hits | {cache_hits} |",
            f"| Billable calls | {billable_calls} |",
            f"| Prompt tokens | {prompt_tokens:,} |",
            f"| Completion tokens | {completion_tokens:,} |",
            f"| Estimated AI cost (USD) | ${cost:.4f} |",
            f"| Estimated cost per 1,000 posts (USD) | ${per_1000:.4f} |",
            "",
            "Prices are configurable approximations in `app/ai/metering.py`.",
            "Verify against the current Gemini price sheet before publishing.",
            "Infrastructure cost (Postgres/Redis/hosting) is reported separately.",
            "",
        ]
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(content, encoding="utf-8")
    print(content)


if __name__ == "__main__":
    main()
