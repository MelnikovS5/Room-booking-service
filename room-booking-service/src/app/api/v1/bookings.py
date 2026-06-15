from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.booking import create_booking, get_my_bookings, delete_booking
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.post("/", response_model=BookingResponse)
async def create_booking_endpoint(data: BookingCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await create_booking(db, data, current_user.id)

@router.get("/", response_model=list[BookingResponse])
async def get_bookings_endpoint(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await get_my_bookings(db, current_user.id)

@router.delete("/{booking_id}")
async def delete_booking_endpoint(booking_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await delete_booking(db, booking_id, current_user)
