from app.ingestion.dedupe import canonical_url, dedupe_hash, similar_title


def test_tracking_params_are_stripped():
    first = canonical_url("https://boards.greenhouse.io/acme/jobs/12?utm_source=x")
    second = canonical_url("https://boards.greenhouse.io/acme/jobs/12")
    assert first == second


def test_dedupe_hash_stable_for_same_canonical_url():
    first = dedupe_hash("Engineer", "Acme", "Bengaluru", "https://acme.com/j/1?utm_source=x")
    second = dedupe_hash("Engineer", "Acme", "Bengaluru", "https://acme.com/j/1")
    assert first == second


def test_similar_titles_detected_but_distinct_roles_not_merged():
    assert similar_title("Software Engineer Intern", "Software Engineering Intern") is True
    assert similar_title("Software Engineer Intern", "Product Manager Intern") is False
