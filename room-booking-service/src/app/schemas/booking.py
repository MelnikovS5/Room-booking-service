from pydantic import BaseModel, Field

class BookingCreate(BaseModel):
    room_id: int = Field(...)
    slot_id: int = Field(...)
    booking_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")  # YYYY-MM-DD format

class BookingResponse(BaseModel):
    id: int
    room_id: int
    slot_id: int
    user_id: int
    booking_date: str
    