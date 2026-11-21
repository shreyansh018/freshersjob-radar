from enum import Enum

from pydantic import BaseModel, Field, field_validator

from app.models.enums import EmploymentType, ExperienceLevel, RoleCategory, WorkplaceType


def _coerce(enum_cls: type[Enum], default):
    def validator(value):
        if isinstance(value, enum_cls):
            return value
        if isinstance(value, str):
            for member in enum_cls:
                if member.value.lower() == value.strip().lower():
                    return member
        return default

    return validator


_coerce_role = _coerce(RoleCategory, RoleCategory.OTHER)
_coerce_level = _coerce(ExperienceLevel, ExperienceLevel.UNKNOWN)
_coerce_type = _coerce(EmploymentType, EmploymentType.UNKNOWN)
_coerce_workplace = _coerce(WorkplaceType, WorkplaceType.UNKNOWN)


class ClassificationResult(BaseModel):
    role_category: RoleCategory = Field(default=RoleCategory.OTHER)
    experience_level: ExperienceLevel = Field(default=ExperienceLevel.UNKNOWN)
    min_experience: float | None = None
    max_experience: float | None = None
    fresher_suitability: bool = False
    job_type: EmploymentType = Field(default=EmploymentType.UNKNOWN)
    city: str | None = None
    workplace_type: WorkplaceType = Field(default=WorkplaceType.UNKNOWN)
    remote_eligible_for_india: bool = False
    skills: list[str] = Field(default_factory=list)
    degree_requirements: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning: str = Field(default="", max_length=500)

    @field_validator("role_category", mode="before")
    @classmethod
    def validate_role(cls, value):
        return _coerce_role(value)

    @field_validator("experience_level", mode="before")
    @classmethod
    def validate_level(cls, value):
        return _coerce_level(value)

    @field_validator("job_type", mode="before")
    @classmethod
    def validate_job_type(cls, value):
        return _coerce_type(value)

    @field_validator("workplace_type", mode="before")
    @classmethod
    def validate_workplace(cls, value):
        return _coerce_workplace(value)

    @field_validator("confidence", mode="before")
    @classmethod
    def bound_confidence(cls, value):
        try:
            number = float(value)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(1.0, number))
