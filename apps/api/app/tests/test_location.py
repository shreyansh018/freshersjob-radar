from app.ingestion.location import parse_location
from app.models.enums import RemoteScope, WorkplaceType


def test_bengaluru_onsite_is_india_eligible():
    info = parse_location("Bengaluru, Karnataka, India", "Join our team")
    assert info.india_eligible is True
    assert info.city == "Bengaluru"
    assert info.country == "India"
    assert info.workplace_type == WorkplaceType.ONSITE


def test_worldwide_remote_without_india_signal_is_excluded():
    info = parse_location("Remote - Worldwide", "Work from anywhere in the world")
    assert info.india_eligible is False
    assert info.remote_scope == RemoteScope.WORLDWIDE


def test_india_remote_is_included():
    info = parse_location("Remote - India", "Remote role for candidates based in India")
    assert info.india_eligible is True
    assert info.workplace_type == WorkplaceType.REMOTE
    assert info.remote_scope == RemoteScope.INDIA


def test_negative_remote_is_not_treated_as_remote():
    info = parse_location("Pune, India", "This role is not remote")
    assert info.workplace_type == WorkplaceType.ONSITE
    assert info.india_eligible is True


def test_us_location_with_incidental_india_mention_is_excluded():
    info = parse_location(
        "New York, NY; Pittsburgh, PA",
        "Our applicant privacy notice applies to India candidates too. We are based in PA.",
    )
    assert info.india_eligible is False
    assert info.country is None


def test_ambiguous_in_office_location_uses_description_city():
    info = parse_location("In-Office", "Work with our Bengaluru, India engineering team")
    assert info.india_eligible is True
    assert info.city == "Bengaluru"


def test_explicit_worldwide_remote_is_excluded_even_with_india_mention():
    info = parse_location("Remote - Worldwide", "Candidates in India may also apply")
    assert info.india_eligible is False
