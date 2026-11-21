from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.job import CategoryCount, StatsResponse
from app.services.stats_service import get_categories, get_locations, get_stats

router = APIRouter(tags=["meta"])


@router.get("/stats", response_model=StatsResponse)
async def stats(db: AsyncSession = Depends(get_db)) -> StatsResponse:
    return await get_stats(db)


@router.get("/categories", response_model=list[CategoryCount])
async def categories(db: AsyncSession = Depends(get_db)) -> list[CategoryCount]:
    return await get_categories(db)


@router.get("/locations", response_model=list[CategoryCount])
async def locations(db: AsyncSession = Depends(get_db)) -> list[CategoryCount]:
    return await get_locations(db)
