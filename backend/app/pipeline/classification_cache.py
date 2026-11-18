import hashlib
import json
import sqlite3
from pathlib import Path

# backend/data/classification_cache.db
BACKEND_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BACKEND_DIR / "data"
DB_PATH = DATA_DIR / "classification_cache.db"


def _get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def get_cache_key(job) -> str:
    """Generate a stable key based on job identity and content."""
    content = {
        "source": job.source,
        "source_id": job.source_id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "description": job.description,
    }

    serialized = json.dumps(content, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def initialize_cache():
    with _get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS classification_cache (
                cache_key TEXT PRIMARY KEY,
                result_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def get_cached_classification(job):
    key = get_cache_key(job)

    with _get_connection() as conn:
        row = conn.execute(
            """
            SELECT result_json
            FROM classification_cache
            WHERE cache_key = ?
            """,
            (key,),
        ).fetchone()

    if row:
        return json.loads(row[0])

    return None


def save_classification(job, result: dict):
    key = get_cache_key(job)

    with _get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO classification_cache
            (cache_key, result_json)
            VALUES (?, ?)
            """,
            (key, json.dumps(result)),
        )


def get_cache_stats():
    initialize_cache()

    with _get_connection() as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM classification_cache"
        ).fetchone()[0]

    return {"cached_classifications": total}