from app.ingestion.normalize import normalize


def test_greenhouse_department_dict_becomes_string():
    raw = {
        "id": 123,
        "title": "Software Engineer Intern",
        "content": "<p>Build things</p>",
        "location": {"name": "Bengaluru, India"},
        "absolute_url": "https://example.com/jobs/123",
        "departments": [{"id": 1, "name": "Engineering", "child_ids": []}],
        "first_published": "2026-11-01T00:00:00Z",
    }
    result = normalize(raw, "greenhouse", "Acme")
    assert result is not None
    assert result.department == "Engineering"
    assert isinstance(result.department, str)
    assert result.location_text == "Bengaluru, India"
    assert result.posted_at is not None


def test_greenhouse_location_string_is_supported():
    raw = {
        "id": 124,
        "title": "Intern",
        "location": "Bengaluru, India",
        "absolute_url": "https://example.com/jobs/124",
    }
    result = normalize(raw, "greenhouse", "Acme")
    assert result is not None
    assert result.location_text == "Bengaluru, India"


def test_ashby_department_dict_becomes_string():
    raw = {
        "jobId": "a-1",
        "title": "Intern",
        "location": "Remote - India",
        "jobUrl": "https://example.com/a-1",
        "department": {"name": "Engineering"},
    }
    result = normalize(raw, "ashby", "Acme")
    assert result is not None
    assert result.department == "Engineering"
