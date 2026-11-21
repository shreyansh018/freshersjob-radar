from app.ingestion.relevance import score_relevance
from app.models.enums import RelevanceState


def test_intern_title_is_strong():
    result = score_relevance("Software Engineering Intern", "Work with our platform team", "Internship")
    assert result.state == RelevanceState.STRONG
    assert "early_career_title" in result.reasons


def test_senior_role_is_experienced():
    result = score_relevance("Senior Staff Engineer", "10+ years of experience required", "Full-time")
    assert result.state == RelevanceState.EXPERIENCED


def test_neutral_role_is_uncertain():
    result = score_relevance("Accountant", "Handle ledgers and monthly closing", "Full-time")
    assert result.state == RelevanceState.UNCERTAIN
