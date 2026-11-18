from datetime import datetime
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