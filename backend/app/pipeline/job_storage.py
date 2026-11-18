
import json
import sqlite3
from pathlib import Path

from .schemas import JobRecord

BACKEND_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BACKEND_DIR / "data"
DB_PATH = DATA_DIR / "jobs.db"


def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_jobs_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                source TEXT NOT NULL,
                source_id TEXT NOT NULL,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT DEFAULT '',
                url TEXT NOT NULL,
                posted_at TEXT,
                workplace_type TEXT,
                role_category TEXT,
                city TEXT,
                experience_level TEXT,
                job_type TEXT,
                is_fresher_friendly INTEGER,
                classification_confidence REAL,
                classification_reasoning TEXT,
                classification_error TEXT,
                ai_status TEXT DEFAULT 'pending',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (source, source_id)
            )
        """)


def save_jobs(jobs):
    initialize_jobs_db()
    saved = 0

    with get_connection() as conn:
        for job in jobs:
            data = job.model_dump(mode="json")

            conn.execute("""
                INSERT INTO jobs (
                    source, source_id, title, company, location,
                    description, url, posted_at, workplace_type,
                    role_category, city, experience_level, job_type,
                    is_fresher_friendly, classification_confidence,
                    classification_reasoning, classification_error, ai_status,
                    updated_at
                )
                VALUES (
                    :source, :source_id, :title, :company, :location,
                    :description, :url, :posted_at, :workplace_type,
                    :role_category, :city, :experience_level, :job_type,
                    :is_fresher_friendly, :classification_confidence,
                    :classification_reasoning, :classification_error, :ai_status,
                    CURRENT_TIMESTAMP
                )
                ON CONFLICT(source, source_id) DO UPDATE SET
                    title=excluded.title,
                    company=excluded.company,
                    location=excluded.location,
                    description=excluded.description,
                    url=excluded.url,
                    posted_at=excluded.posted_at,
                    workplace_type=excluded.workplace_type,
                    role_category=excluded.role_category,
                    city=excluded.city,
                    experience_level=excluded.experience_level,
                    job_type=excluded.job_type,
                    is_fresher_friendly=excluded.is_fresher_friendly,
                    classification_confidence=excluded.classification_confidence,
                    classification_reasoning=excluded.classification_reasoning,
                    classification_error=excluded.classification_error,
                    ai_status=excluded.ai_status,
                    updated_at=CURRENT_TIMESTAMP
            """, {
                **data,
                "is_fresher_friendly": (
                    int(data["is_fresher_friendly"])
                    if data["is_fresher_friendly"] is not None
                    else None
                )
            })
            saved += 1

    return saved


def search_jobs(
    keyword=None,
    city=None,
    role=None,
    company=None,
    fresher_only=True,
    limit=200,
    offset=0,
):
    initialize_jobs_db()

    conditions = []
    params = []

    if fresher_only:
        conditions.append("is_fresher_friendly = 1")

    if keyword:
        conditions.append(
            "(title LIKE ? OR company LIKE ? OR description LIKE ?)"
        )
        pattern = f"%{keyword}%"
        params.extend([pattern, pattern, pattern])

    if city:
        conditions.append("(city LIKE ? OR location LIKE ?)")
        pattern = f"%{city}%"
        params.extend([pattern, pattern])

    if role:
        conditions.append("role_category LIKE ?")
        params.append(f"%{role}%")

    if company:
        conditions.append("company LIKE ?")
        params.append(f"%{company}%")

    where_clause = (
        "WHERE " + " AND ".join(conditions)
        if conditions else ""
    )

    query = f"""
        SELECT * FROM jobs
        {where_clause}
        ORDER BY updated_at DESC
        LIMIT ? OFFSET ?
    """

    params.extend([limit, offset])

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    return [dict(row) for row in rows]


def get_job(source, source_id):
    initialize_jobs_db()

    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM jobs WHERE source=? AND source_id=?",
            (source, source_id),
        ).fetchone()

    return dict(row) if row else None


def get_job_stats():
    initialize_jobs_db()

    with get_connection() as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM jobs"
        ).fetchone()[0]

        fresher = conn.execute(
            "SELECT COUNT(*) FROM jobs WHERE is_fresher_friendly=1"
        ).fetchone()[0]

        classified = conn.execute(
            "SELECT COUNT(*) FROM jobs WHERE ai_status='success'"
        ).fetchone()[0]

        cities = conn.execute("""
            SELECT city, COUNT(*) AS count
            FROM jobs
            WHERE city IS NOT NULL AND city != ''
            GROUP BY city
            ORDER BY count DESC
        """).fetchall()

        roles = conn.execute("""
            SELECT role_category, COUNT(*) AS count
            FROM jobs
            WHERE role_category IS NOT NULL AND role_category != ''
            GROUP BY role_category
            ORDER BY count DESC
        """).fetchall()

    return {
        "total_jobs": total,
        "fresher_friendly_jobs": fresher,
        "successfully_classified": classified,
        "cities": [dict(row) for row in cities],
        "roles": [dict(row) for row in roles],
    }
