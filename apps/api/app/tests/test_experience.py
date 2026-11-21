from app.ingestion.experience import extract_experience


def test_range_is_extracted():
    info = extract_experience("Candidates with 0-2 years of experience may apply")
    assert info.min_years == 0
    assert info.max_years == 2
    assert info.explicit is True


def test_fresher_is_extracted():
    info = extract_experience("We welcome freshers to apply")
    assert info.min_years == 0
    assert info.max_years == 1


def test_missing_experience_is_not_inferred():
    info = extract_experience("Great team, exciting product")
    assert info.min_years is None
    assert info.max_years is None
    assert info.explicit is False
