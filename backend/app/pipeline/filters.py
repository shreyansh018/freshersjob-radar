
import re

INDIA_LOCATION_PATTERNS = [
    r"\bindia\b",
    r"\bbengaluru\b",
    r"\bbangalore\b",
    r"\bmumbai\b",
    r"\bhyderabad\b",
    r"\bchennai\b",
    r"\bdelhi\b",
    r"\bnew delhi\b",
    r"\bnoida\b",
    r"\bgurgaon\b",
    r"\bgurugram\b",
    r"\bpune\b",
    r"\bkolkata\b",
    r"\bjaipur\b",
    r"\bkochi\b",
    r"\bcochin\b",
    r"\bcoimbatore\b",
    r"\bindore\b",
    r"\btrivandrum\b",
    r"\bthiruvananthapuram\b",
    r"\bahmedabad\b",
    r"\bchandigarh\b",
    r"\blucknow\b",
    r"\bnagpur\b",
    r"\bbhopal\b",
    r"\bpatna\b",
    r"\bvadodara\b",
    r"\bsurat\b",
    r"\bremote,? india\b",
    r"\bindia remote\b",
    r"\bremote\b.*\bindia\b",
    r"\bindia\b.*\bremote\b",
    r"\bncr\b",
]

FRESHER_PATTERNS = [
    r"\bfresher\b",
    r"\bfreshers\b",
    r"\bentry[\s-]?level\b",
    r"\bnew grad\b",
    r"\bnew graduate\b",
    r"\bgraduat(?:e|ing|ion)\b",
    r"\bgraduate trainee\b",
    r"\bjunior\b",
    r"\bassociate\b",
    r"\bintern\b",
    r"\binternship\b",
    r"\btrainee\b",
    r"\bapprentice\b",
    r"\bapprenticeship\b",
    r"\bearly career\b",
    r"\bcampus\b",
    r"\buniversity\b",
    r"\bcollege\b",
    r"\b0[\s-]?to[\s-]?1 years?\b",
    r"\b0[\s-]?to[\s-]?2 years?\b",
    r"\b0[\s-]?to[\s-]?3 years?\b",
    r"\b0[\s-]?2 years?\b",
    r"\b0[\s-]?3 years?\b",
    r"\bno experience\b",
    r"\bwithout experience\b",
    r"\bgraduate program\b",
    r"\bgraduate programme\b",
    r"\bentry talent\b",
    r"\bsoftware engineer i\b",
    r"\bengineer i\b",
    r"\banalyst i\b",
    r"\bdeveloper i\b",
    r"\bassociate engineer\b",
    r"\bassociate developer\b",
    r"\bassociate analyst\b",
    r"\bjunior engineer\b",
    r"\bjunior developer\b",
    r"\bjunior analyst\b",
    r"\bjunior designer\b",
    r"\bjunior scientist\b",
    r"\bjunior data\b",
    r"\bgraduate engineer\b",
    r"\bgraduate analyst\b",
    r"\bgraduate developer\b",
    r"\bgraduate software\b",
    r"\bentry level\b",
]

def matches_any(text: str, patterns: list[str]) -> bool:
    text = text.lower()
    return any(re.search(pattern, text) for pattern in patterns)


def is_india_job(job) -> bool:
    location = (job.location or "").lower()
    return matches_any(location, INDIA_LOCATION_PATTERNS)


def is_fresher_job(job) -> bool:
    searchable_text = " ".join([
        job.title or "",
        job.description or "",
    ])
    return matches_any(searchable_text, FRESHER_PATTERNS)


def filter_target_jobs(jobs):
    """Keep India jobs with potential early-career signals."""
    return [
        job for job in jobs
        if is_india_job(job) and is_fresher_job(job)
    ]
