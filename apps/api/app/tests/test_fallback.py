from app.ingestion.experience import extract_experience
from app.ingestion.fallback import deterministic_fields, infer_level
from app.ingestion.relevance import score_relevance
from app.ingestion.location import parse_location
from app.models.enums import ExperienceLevel


def _fields(title: str, description: str = "") -> dict:
    location = parse_location("Bengaluru, India", description)
    relevance = score_relevance(title, description, None)
    experience = extract_experience(f"{title}\n{description[:3000]}")
    return deterministic_fields(
        title=title,
        relevance=relevance,
        location=location,
        employment_type_raw=None,
        experience=experience,
    )


def test_senior_title_is_tagged_experienced_and_kept():
    fields = _fields("Senior Software Engineer", "8 years of experience required")
    assert fields["experience_level"] == ExperienceLevel.EXPERIENCED
    assert fields["fresher_friendly"] is False
    assert fields["role_category"] is not None  # still a usable listing


def test_explicit_years_tag_experienced_without_senior_word():
    fields = _fields("Platform Engineer", "Minimum 5 years of experience")
    assert fields["experience_level"] == ExperienceLevel.EXPERIENCED


def test_intern_and_fresher_titles_stay_early_career():
    assert infer_level("Software Engineer Intern", score_relevance("Software Engineer Intern", "", "internship")) == ExperienceLevel.INTERNSHIP
    assert _fields("Software Engineer, New Grad")["experience_level"] == ExperienceLevel.FRESHER


def test_associate_title_is_entry_level():
    assert _fields("Operations Associate")["experience_level"] == ExperienceLevel.ENTRY_LEVEL


def test_internal_is_not_an_intern():
    assert _fields("Senior Internal Auditor")["experience_level"] == ExperienceLevel.EXPERIENCED
    assert _fields("Engineering Manager - Internal Systems")["experience_level"] == ExperienceLevel.EXPERIENCED


def test_india_fresher_title_patterns():
    for title in ("Software Engineer I", "SDE 1", "Graduate Engineer Trainee", "Software Engineer - Apprentice"):
        assert _fields(title)["experience_level"] == ExperienceLevel.FRESHER, title


def test_early_levels_are_fresher_friendly():
    assert _fields("Software Engineer Intern")["fresher_friendly"] is True
    assert _fields("Software Engineer I")["fresher_friendly"] is True
    assert _fields("Operations Associate")["fresher_friendly"] is True
