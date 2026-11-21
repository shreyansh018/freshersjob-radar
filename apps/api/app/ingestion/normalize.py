import html
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class NormalizedJob:
    source_job_id: str
    company_name: str
    company_website: str | None
    title: str
    description: str | None
    location_text: str | None
    application_url: str
    department: str | None
    employment_type_raw: str | None
    workplace_type_raw: str | None
    posted_at: datetime | None
    updated_at: datetime | None
    raw: dict[str, Any]


def strip_html(value: str | None) -> str | None:
    if not value:
        return None
    text = re.sub(r"<script[^>]*>.*?</script>", " ", value, flags=re.I | re.S)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def parse_date(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, (int, float)):
        seconds = value / 1000 if value > 10_000_000_000 else value
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    text = str(value).strip()
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError:
        return None


def _first(value: Any) -> Any:
    if isinstance(value, list) and value:
        return value[0]
    return value


def _name(value: Any) -> str | None:
    """Reduce ATS category objects to a plain string for VARCHAR columns."""
    value = _first(value)
    if isinstance(value, dict):
        value = value.get("name") or value.get("label") or value.get("title")
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _location_name(value: Any) -> str | None:
    if isinstance(value, dict):
        value = value.get("name")
    return str(value).strip() if value else None


def normalize(raw: dict[str, Any], platform: str, source_name: str) -> NormalizedJob | None:
    try:
        if platform == "greenhouse":
            location = _location_name(raw.get("location"))
            return NormalizedJob(
                source_job_id=str(raw["id"]),
                company_name=source_name,
                company_website=None,
                title=str(raw.get("title", "")).strip(),
                description=strip_html(raw.get("content")),
                location_text=location,
                application_url=raw.get("absolute_url") or "",
                department=_name(raw.get("departments")),
                employment_type_raw=None,
                workplace_type_raw=location,
                posted_at=parse_date(raw.get("first_published")),
                updated_at=parse_date(raw.get("updated_at")),
                raw=raw,
            )

        if platform == "lever":
            categories = raw.get("categories") or {}
            return NormalizedJob(
                source_job_id=str(raw["id"]),
                company_name=source_name,
                company_website=None,
                title=str(raw.get("text", "")).strip(),
                description=strip_html(raw.get("descriptionPlain") or raw.get("description")),
                location_text=categories.get("location"),
                application_url=raw.get("hostedUrl") or "",
                department=categories.get("department"),
                employment_type_raw=categories.get("commitment"),
                workplace_type_raw=categories.get("location"),
                posted_at=parse_date(raw.get("createdAt")),
                updated_at=None,
                raw=raw,
            )

        if platform == "ashby":
            location = raw.get("location") or raw.get("locationName")
            if isinstance(location, dict):
                location = location.get("name")
            return NormalizedJob(
                source_job_id=str(raw.get("jobId") or raw.get("id") or ""),
                company_name=source_name,
                company_website=raw.get("companyWebsite"),
                title=str(raw.get("title", "")).strip(),
                description=strip_html(raw.get("descriptionPlain") or raw.get("descriptionHtml")),
                location_text=location,
                application_url=raw.get("jobUrl") or raw.get("applyUrl") or "",
                department=_name(raw.get("department")),
                employment_type_raw=raw.get("employmentType"),
                workplace_type_raw=raw.get("workplaceType") or location,
                posted_at=parse_date(raw.get("publishedAt")),
                updated_at=None,
                raw=raw,
            )

        if platform == "workable":
            location = raw.get("location") or {}
            return NormalizedJob(
                source_job_id=str(raw.get("id") or raw.get("shortcode") or ""),
                company_name=source_name,
                company_website=None,
                title=str(raw.get("title", "")).strip(),
                description=strip_html(raw.get("description")),
                location_text=str(location.get("str") or location.get("city") or "") or None,
                application_url=raw.get("url") or "",
                department=_name(raw.get("department")),
                employment_type_raw=raw.get("employment_type") or raw.get("employmentType"),
                workplace_type_raw=raw.get("telecommuting"),
                posted_at=parse_date(raw.get("published_on") or raw.get("created_at")),
                updated_at=None,
                raw=raw,
            )

        if platform == "smartrecruiters":
            location = raw.get("location") or {}
            city = location.get("city")
            return NormalizedJob(
                source_job_id=str(raw.get("id") or ""),
                company_name=source_name,
                company_website=None,
                title=str((raw.get("name") or "")).strip(),
                description=strip_html(raw.get("description")),
                location_text=", ".join(filter(None, [city, location.get("country")])) or None,
                application_url=(raw.get("apply") or {}).get("url") or raw.get("ref") or "",
                department=_name(raw.get("department")),
                employment_type_raw=(raw.get("type") or {}).get("label"),
                workplace_type_raw=raw.get("workplaceType"),
                posted_at=parse_date(raw.get("createdOn") or raw.get("releasedOn")),
                updated_at=parse_date(raw.get("updatedOn")),
                raw=raw,
            )
    except (KeyError, TypeError, AttributeError):
        return None

    return None
