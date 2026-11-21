"""Disable candidate boards that returned 404 or zero postings in validation.

Run after `check_sources.py`. Keeps the registry honest without deleting
provenance for jobs already ingested from these sources.
"""

import asyncio
import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1] / "apps" / "api"
if (API_DIR / "app").exists():
    sys.path.insert(0, str(API_DIR))

from sqlalchemy import func, update

from app.db.session import AsyncSessionLocal
from app.models import Source

# Boards validated as unreachable (404) or permanently empty.
DEAD_BOARDS = {
    "atlassian", "asana", "razorpay", "anthropic", "ramp", "reddit", "canva",
    "quora", "notion", "snowflake", "postman", "browserstack", "chargebee",
    "freshworks", "zoho", "meesho", "cred", "zepto", "pulsus",
    "sap", "vercel", "cognizant", "infosys", "wipro", "hcltechnologies",
    "techmahindra", "accenture", "ibm",
    "paypal", "ebay", "hashicorp", "splunk", "servicenow", "workday", "adobe",
    "intuit", "uber", "zoom", "miro", "retool", "coursera",
}


async def main() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            update(Source)
            .where(func.lower(Source.board_identifier).in_(DEAD_BOARDS))
            .values(enabled=False, last_error="disabled: 404 or empty in validation")
        )
        await db.commit()
    print(f"Disabled {result.rowcount} dead source boards.")


if __name__ == "__main__":
    asyncio.run(main())
