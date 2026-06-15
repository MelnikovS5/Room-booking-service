import asyncio
from app.db.session import async_session, engine
from app.db.base import Base
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.room import Room
from app.models.slot import Slot
import datetime
from sqlalchemy import select

async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as db:
        result = await db.execute(select(User).where(User.username == "admin"))
        if not result.scalars().first():
            user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=hash_password("admin123"),
                role=UserRole.admin
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        rooms = await db.execute(select(Room))
        if not rooms.scalars().first():
            rooms_data = [
                Room(name="Переговорная1", description="Комната для переговоров"),
                Room(name="Переговорная2", description="Комната для переговоров"),
                Room(name="Переговорная3", description="Комната для переговоров")
            ]
            db.add_all(rooms_data)
            await db.commit()
        slots = await db.execute(select(Slot))
        if not slots.scalars().first():
            slots_data = [
                Slot(start_time=datetime.time(9, 0), end_time=datetime.time(11, 0)),
                Slot(start_time=datetime.time(11, 0), end_time=datetime.time(13, 0)),
                Slot(start_time=datetime.time(13, 0), end_time=datetime.time(15, 0)),
                Slot(start_time=datetime.time(15, 0), end_time=datetime.time(17, 0)),
                Slot(start_time=datetime.time(17, 0), end_time=datetime.time(19, 0))
            ]
            db.add_all(slots_data)
            await db.commit()
        
if __name__ == "__main__":
    asyncio.run(seed())
        