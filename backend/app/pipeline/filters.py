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
    r"\bcoimbatore\b",
    r"\bindore\b",
    r"\btrivandrum\b",
    r"\bahmedabad\b",
    r"\bremote,? india\b",
]

FRESHER_PATTERNS = [
    r"\bfresher\b",
    r"\bfreshers\b",
    r"\bentry[\s-]?level\b",
    r"\bentry level\b",
    r"\bnew grad\b",
    r"\bgraduate\b",
    r"\bgraduating\b",
    r"\bgraduate trainee\b",
    r"\bjunior\b",
    r"\bassociate\b",
    r"\bintern\b",
    r"\binternship\b",
    r"\btrainee\b",
    r"\b0[\s-]?to[\s-]?1 years?\b",
    r"\b0[\s-]?to[\s-]?2 years?\b",
    r"\b0[\s-]?2 years?\b",
    r"\bno experience\b",
    r"\bearly career\b",
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
    """Keep jobs matching our initial India + fresher heuristic."""

    return [
        job for job in jobs
        if is_india_job(job) and is_fresher_job(job)
    ]