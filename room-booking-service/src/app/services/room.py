from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.room import Room
from app.schemas.room import RoomResponse

async def get_rooms(db: AsyncSession) -> list[RoomResponse]:
    result = await db.execute(select(Room))
    rooms = result.scalars().all()
    return [RoomResponse(id=room.id, name=room.name, description=room.description) for room in rooms]