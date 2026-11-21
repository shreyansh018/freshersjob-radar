import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.job import JobSummary


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: EmailStr
    role: str
    created_at: datetime


class PreferenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    roles: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    experience: str | None = None
    remote_preference: str | None = None


class PreferenceUpdate(BaseModel):
    roles: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    experience: str | None = None
    remote_preference: str | None = None


class SavedJobOut(BaseModel):
    saved_at: datetime
    job: JobSummary
