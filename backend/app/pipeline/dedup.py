import re
from urllib.parse import urlparse


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def deduplicate_jobs(jobs):
    """
    Deduplicate by source ID and then by normalized
    company + title + location.
    """

    seen_source_ids = set()
    seen_fingerprints = set()
    unique_jobs = []

    for job in jobs:
        source_key = (
            job.source.lower(),
            str(job.source_id),
        )

        fingerprint = (
            normalize_text(job.company),
            normalize_text(job.title),
            normalize_text(job.location),
        )

        if source_key in seen_source_ids:
            continue

        if fingerprint in seen_fingerprints:
            continue

        seen_source_ids.add(source_key)
        seen_fingerprints.add(fingerprint)

        unique_jobs.append(job)

    return unique_jobs