from datetime import time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.slot import Slot
from app.schemas.slot import SlotResponse, SlotCreate

async def get_slots(db: AsyncSession) -> list[SlotResponse]:
    result = await db.execute(select(Slot))
    slots = result.scalars().all()
    return [SlotResponse(id=slot.id, start_time=str(slot.start_time), end_time=str(slot.end_time)) for slot in slots]

def _parse_time(value: str) -> time:
    parts = value.split(":")
    return time(int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)

async def create_slot(db: AsyncSession, data: SlotCreate) -> SlotResponse:
    slot = Slot(
        start_time=_parse_time(data.start_time),
        end_time=_parse_time(data.end_time)
    )
    db.add(slot)
    await db.commit()
    await db.refresh(slot)
    return SlotResponse(id=slot.id, start_time=str(slot.start_time), end_time=str(slot.end_time))
