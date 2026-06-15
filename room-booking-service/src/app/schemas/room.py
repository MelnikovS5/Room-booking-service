from pydantic import BaseModel, Field

class RoomCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str | None = Field(None, max_length=255)

class RoomResponse(BaseModel):
    id: int
    name: str
    description: str | None

class SlotAvailability(BaseModel):
    slot_id: int
    start_time: str
    end_time: str
    is_available: bool

class RoomAvailabilityResponse(BaseModel):
    room_id: int
    room_name: str
    slots: list[SlotAvailability]

