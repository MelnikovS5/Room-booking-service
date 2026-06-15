from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.room import RoomCreate, RoomResponse
from app.services.room import get_rooms

router = APIRouter(prefix="/rooms", tags=["Rooms"])

@router.get("/", response_model=list[RoomResponse])
async def get_rooms_endpoint(db: AsyncSession = Depends(get_db)):
    return await get_rooms(db)