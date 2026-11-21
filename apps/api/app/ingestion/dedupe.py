import hashlib
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "gclid", "fbclid", "ref", "source", "tracking",
}

STOP_WORDS = {
    "a", "an", "the", "and", "or", "of", "for", "in", "at", "to", "with",
    "role", "position", "opening", "job",
}

STEMS = {
    "engineering": "engineer",
    "engineers": "engineer",
    "development": "develop",
    "developer": "develop",
    "developers": "develop",
    "interns": "intern",
    "manager": "manager",
}


def canonical_url(url: str | None) -> str:
    if not url:
        return ""
    parts = urlsplit(url.strip())
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if k.lower() not in TRACKING_PARAMS]
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, urlencode(sorted(query)), ""))


def content_hash(title: str, description: str | None) -> str:
    normalized = f"{title.strip().lower()}::{(description or '').strip().lower()}"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9+#]+", text.lower())
    normalised = (STEMS.get(word, word) for word in words)
    return {word for word in normalised if word not in STOP_WORDS and len(word) > 2}


def dedupe_hash(title: str, company: str, city: str | None, url: str | None) -> str:
    canonical = canonical_url(url)
    if canonical:
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    payload = f"{company.strip().lower()}|{title.strip().lower()}|{(city or '').strip().lower()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def similar_title(a: str, b: str, threshold: float = 0.85) -> bool:
    first, second = _tokens(a), _tokens(b)
    if not first or not second:
        return False
    intersection = len(first & second)
    union = len(first | second)
    return (intersection / union) >= threshold
