from app.ai.schema import ClassificationResult


def test_unknown_enum_values_are_clamped():
    result = ClassificationResult.model_validate(
        {
            "role_category": "Wizard",
            "experience_level": "Legendary",
            "job_type": "Something else",
            "workplace_type": "Moon",
            "confidence": 5,
        }
    )
    assert result.role_category.value == "Other"
    assert result.experience_level.value == "Unknown"
    assert result.job_type.value == "Unknown"
    assert result.workplace_type.value == "Unknown"
    assert result.confidence == 1.0


def test_valid_payload_round_trips():
    result = ClassificationResult.model_validate(
        {
            "role_category": "Frontend Development",
            "experience_level": "Fresher",
            "fresher_suitability": True,
            "skills": ["React", "TypeScript"],
            "confidence": 0.82,
            "reasoning": "Intern title and React stack",
        }
    )
    assert result.role_category.value == "Frontend Development"
    assert result.skills == ["React", "TypeScript"]
