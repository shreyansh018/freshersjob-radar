import re
from dataclasses import dataclass

RANGE_PATTERNS = [
    re.compile(r"(\d+(?:\.\d+)?)\s*(?:-|to|–)\s*(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?|yoe)", re.I),
    re.compile(r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\s*(?:of\s+)?experience", re.I),
]
FRESHER_PATTERN = re.compile(
    r"\b(freshers?|fresh graduate|new graduate|0\s*(?:-|to)?\s*1\s*(?:year|yr)|campus hire|entry level)\b", re.I
)
MIN_ONLY_PATTERN = re.compile(r"(?:min(?:imum)?\s*)?(\d+)\s*\+\s*(?:years?|yrs?)", re.I)


@dataclass
class ExperienceInfo:
    min_years: float | None
    max_years: float | None
    explicit: bool
    evidence: str | None


def extract_experience(text: str | None) -> ExperienceInfo:
    if not text:
        return ExperienceInfo(None, None, False, None)

    for pattern in RANGE_PATTERNS:
        match = pattern.search(text)
        if match:
            first = float(match.group(1))
            if len(match.groups()) >= 2 and match.group(2):
                return ExperienceInfo(first, float(match.group(2)), True, match.group(0))
            return ExperienceInfo(first, first, True, match.group(0))

    match = MIN_ONLY_PATTERN.search(text)
    if match:
        value = float(match.group(1))
        return ExperienceInfo(value, None, True, match.group(0))

    match = FRESHER_PATTERN.search(text)
    if match:
        return ExperienceInfo(0.0, 1.0, True, match.group(0))

    return ExperienceInfo(None, None, False, None)
