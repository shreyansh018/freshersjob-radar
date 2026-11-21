import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models import Job, Preference, SavedJob, User
from app.schemas.user import PreferenceOut, PreferenceUpdate, SavedJobOut
from app.services.auth_service import get_current_user
from app.services.job_service import to_summary

router = APIRouter(prefix="/users/me", tags=["users"])


@router.get("/saved-jobs", response_model=list[SavedJobOut])
async def list_saved(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> list[SavedJobOut]:
    stmt = (
        select(SavedJob)
        .options(
            selectinload(SavedJob.job).selectinload(Job.company),
            selectinload(SavedJob.job).selectinload(Job.source),
        )
        .where(SavedJob.user_id == user.id)
        .order_by(SavedJob.saved_at.desc())
    )
    rows = list((await db.execute(stmt)).scalars().unique().all())
    return [SavedJobOut(saved_at=row.saved_at, job=to_summary(row.job)) for row in rows if row.job]


@router.post("/saved-jobs/{job_id}")
async def save_job(job_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    job = (await db.execute(select(Job).where(Job.id == job_id))).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    existing = (
        await db.execute(select(SavedJob).where(SavedJob.user_id == user.id, SavedJob.job_id == job_id))
    ).scalar_one_or_none()
    if not existing:
        db.add(SavedJob(user_id=user.id, job_id=job_id))
        await db.commit()
    return {"saved": True}


@router.delete("/saved-jobs/{job_id}")
async def unsave_job(job_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    await db.execute(delete(SavedJob).where(SavedJob.user_id == user.id, SavedJob.job_id == job_id))
    await db.commit()
    return {"saved": False}


@router.get("/preferences", response_model=PreferenceOut)
async def get_preferences(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> PreferenceOut:
    pref = (await db.execute(select(Preference).where(Preference.user_id == user.id))).scalar_one_or_none()
    if not pref:
        return PreferenceOut()
    return PreferenceOut.model_validate(pref)


@router.put("/preferences", response_model=PreferenceOut)
async def put_preferences(
    payload: PreferenceUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
) -> PreferenceOut:
    pref = (await db.execute(select(Preference).where(Preference.user_id == user.id))).scalar_one_or_none()
    if not pref:
        pref = Preference(user_id=user.id)
        db.add(pref)
    pref.roles = payload.roles
    pref.locations = payload.locations
    pref.skills = payload.skills
    pref.experience = payload.experience
    pref.remote_preference = payload.remote_preference
    await db.commit()
    await db.refresh(pref)
    return PreferenceOut.model_validate(pref)
