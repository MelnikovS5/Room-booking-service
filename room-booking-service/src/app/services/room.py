from datetime import date as Date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.room import Room
from app.models.slot import Slot
from app.models.booking import Booking
from app.schemas.room import RoomResponse, RoomAvailabilityResponse, SlotAvailability


async def get_rooms(db: AsyncSession) -> list[RoomResponse]:
    result = await db.execute(select(Room))
    rooms = result.scalars().all()
    return [RoomResponse(id=room.id, name=room.name, description=room.description) for room in rooms]


async def get_rooms_availability(db: AsyncSession, booking_date: Date) -> list[RoomAvailabilityResponse]:
    rooms_result = await db.execute(select(Room))
    rooms = rooms_result.scalars().all()

    slots_result = await db.execute(select(Slot))
    all_slots = slots_result.scalars().all()

    bookings_result = await db.execute(
        select(Booking).where(Booking.booking_date == booking_date)
    )
    booked = {(b.room_id, b.slot_id) for b in bookings_result.scalars().all()}

    result = []
    for room in rooms:
        slots = [
            SlotAvailability(
                slot_id=s.id,
                start_time=str(s.start_time),
                end_time=str(s.end_time),
                is_available=(room.id, s.id) not in booked,
            )
            for s in all_slots
        ]
        result.append(RoomAvailabilityResponse(room_id=room.id, room_name=room.name, slots=slots))
    return result