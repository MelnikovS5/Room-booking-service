from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.slot import SlotCreate, SlotResponse
from app.services.slot import get_slots, create_slot

router = APIRouter(prefix="/slots", tags=["Slots"])

@router.get("/", response_model=list[SlotResponse])
async def get_slots_endpoint(db: AsyncSession = Depends(get_db)):
    return await get_slots(db)

@router.post("/", response_model=SlotResponse)
async def create_slot_endpoint(data: SlotCreate, db: AsyncSession = Depends(get_db)):
    return await create_slot(db, data)