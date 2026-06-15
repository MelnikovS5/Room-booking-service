from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.room import RoomCreate, RoomResponse, RoomAvailabilityResponse
from app.services.room import get_rooms, get_rooms_availability
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/rooms", tags=["Rooms"])

@router.get("/", response_model=list[RoomResponse])
async def get_rooms_endpoint(db: AsyncSession = Depends(get_db)):
    return await get_rooms(db)

@router.get("/availability", response_model=list[RoomAvailabilityResponse])
async def get_availability_endpoint(
    date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_rooms_availability(db, date)