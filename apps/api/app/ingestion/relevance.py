import re
from dataclasses import dataclass, field

from app.models.enums import RelevanceState

STRONG_TITLE = re.compile(
    r"\b(intern|internship|fresher|graduate|entry[- ]level|associate|trainee|apprentice|"
    r"campus|early career|junior|0[- ]?1|0[- ]?2)\b",
    re.I,
)
STRONG_TEXT = re.compile(
    r"\b(freshers? (are )?(welcome|encouraged|eligible)|no experience (required|needed)|"
    r"0[- ]?[123] years?|0[- ]?[123] yrs?|first job|campus hiring|new grad)\b",
    re.I,
)
SENIOR_TITLE = re.compile(
    r"\b(senior|principal|staff|lead|manager|director|head of|architect|expert)\b", re.I
)
SENIOR_TEXT = re.compile(r"\b(\d{2,}\+?\s*(?:-|to)?\s*\d*\s*years? of experience|10\+ years)\b", re.I)
INTERN_TYPE = {"internship", "apprenticeship"}


@dataclass
class RelevanceResult:
    state: RelevanceState
    score: float
    reasons: list[str] = field(default_factory=list)


def score_relevance(title: str, description: str | None, employment_type: str | None) -> RelevanceResult:
    reasons: list[str] = []
    score = 0.0
    text = description or ""

    if STRONG_TITLE.search(title):
        score += 4.0
        reasons.append("early_career_title")
    if STRONG_TEXT.search(text[:6000]):
        score += 3.0
        reasons.append("explicit_fresher_language")
    if employment_type and employment_type.lower() in INTERN_TYPE:
        score += 3.0
        reasons.append("internship_or_apprenticeship")
    if re.search(r"\b(graduate program|graduate scheme|early career program)\b", text[:4000], re.I):
        score += 1.5
        reasons.append("graduate_program")

    if SENIOR_TITLE.search(title):
        score -= 4.0
        reasons.append("senior_title")
    if SENIOR_TEXT.search(text[:4000]):
        score -= 2.0
        reasons.append("senior_experience_requirement")

    if score >= 4:
        state = RelevanceState.STRONG
    elif score >= 1:
        state = RelevanceState.POSSIBLE
    elif score <= -3:
        state = RelevanceState.EXPERIENCED
    else:
        state = RelevanceState.UNCERTAIN

    return RelevanceResult(state=state, score=round(score, 2), reasons=reasons)
