"""Run one ingestion cycle using the mounted host source tree.

    docker compose run --rm -v "${PWD}:/repo" -w /repo api python scripts/run_ingestion.py
"""

import asyncio
import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1] / "apps" / "api"
if (API_DIR / "app").exists():
    sys.path.insert(0, str(API_DIR))

from app.ingestion.pipeline import ingest_all


if __name__ == "__main__":
    print(asyncio.run(ingest_all()))
