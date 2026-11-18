from datetime import datetime
from typing import Literal

from pydantic import BaseModel, HttpUrl


class JobRecord(BaseModel):
    source: str
    source_id: str
    title: str
    company: str
    location: str
    description: str = ""
    url: HttpUrl
    posted_at: datetime | None = None
    workplace_type: str | None = None

    # AI classification fields
    role_category: str | None = None
    city: str | None = None

    experience_level: Literal[
        "Internship",
        "Entry Level",
        "Experienced",
        "Unknown",
    ] | None = None

    job_type: Literal[
        "Internship",
        "Full-time",
        "Part-time",
        "Contract",
        "Unknown",
    ] | None = None

    is_fresher_friendly: bool | None = None
    classification_confidence: float | None = None
    classification_reasoning: str | None = None

    # Error tracking
    classification_error: str | None = None

    ai_status: str = "pending"