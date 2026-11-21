import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.job import DateTimeTz, Job


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), default="user", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTimeTz(), default=_now)

    saved_jobs: Mapped[list["SavedJob"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    preferences: Mapped["Preference | None"] = relationship(back_populates="user", uselist=False)
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="user")

    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True)
    saved_at: Mapped[datetime] = mapped_column(DateTimeTz(), default=_now)

    user: Mapped[User] = relationship(back_populates="saved_jobs")
    job: Mapped["Job"] = relationship()


class Preference(Base):
    __tablename__ = "preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    roles: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    locations: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    skills: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    experience: Mapped[str | None] = mapped_column(String(64))
    remote_preference: Mapped[str | None] = mapped_column(String(32))
    updated_at: Mapped[datetime] = mapped_column(DateTimeTz(), default=_now, onupdate=_now)

    user: Mapped[User] = relationship(back_populates="preferences")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTimeTz(), default=_now)

    user: Mapped[User] = relationship(back_populates="notifications")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    keywords: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    company: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str | None] = mapped_column(String(120))
    city: Mapped[str | None] = mapped_column(String(120))
    experience: Mapped[str | None] = mapped_column(String(64))
    employment_type: Mapped[str | None] = mapped_column(String(64))
    cadence: Mapped[str] = mapped_column(String(16), default="daily")
    paused: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTimeTz(), default=_now)

    user: Mapped[User] = relationship(back_populates="alerts")
