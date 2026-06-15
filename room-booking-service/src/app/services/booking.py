from datetime import date
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.booking import Booking
from app.models.room import Room
from app.models.slot import Slot
from app.schemas.booking import BookingCreate, BookingResponse
from app.core.exceptions import NotFound, Conflict, Forbidden


def _parse_date(value: str) -> date:
    parts = value.split("-")
    return date(int(parts[0]), int(parts[1]), int(parts[2]))


async def create_booking(db: AsyncSession, data: BookingCreate, user_id: int):
    room = await db.execute(select(Room).where(Room.id == data.room_id))
    if room.scalar_one_or_none() is None:
        raise NotFound("Room not found")
    slot = await db.execute(select(Slot).where(Slot.id == data.slot_id))
    if slot.scalar_one_or_none() is None:
        raise NotFound("Slot not found")
    booking_date = _parse_date(data.booking_date)
    booking = await db.execute(select(Booking).where(Booking.slot_id == data.slot_id, Booking.room_id == data.room_id, Booking.booking_date == booking_date))
    if booking.scalar_one_or_none():
        raise Conflict("Slot already booked")
    booking = Booking(
        room_id=data.room_id,
        slot_id=data.slot_id,
        user_id=user_id,
        booking_date=booking_date
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return BookingResponse(id=booking.id, room_id=booking.room_id, slot_id=booking.slot_id, user_id=booking.user_id, booking_date=str(booking.booking_date))

async def get_my_bookings(db: AsyncSession, user_id: int):
    bookings = await db.execute(select(Booking).where(Booking.user_id == user_id))
    return [BookingResponse(id=booking.id, room_id=booking.room_id, slot_id=booking.slot_id, user_id=booking.user_id, booking_date=str(booking.booking_date)) for booking in bookings.scalars().all()]

async def delete_booking(db: AsyncSession, booking_id: int, user):
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalars().first()
    if not booking:
        raise NotFound("Booking not found")
    if booking.user_id != user.id and user.role != "admin":
        raise Forbidden("Cannot cancel other's booking")
    await db.delete(booking)
    await db.commit()
    return {"message": "Booking cancelled"}