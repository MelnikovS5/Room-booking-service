from pydantic import BaseModel, Field

class SlotCreate(BaseModel):
    start_time: str = Field(...)
    end_time: str = Field(...)

class SlotResponse(BaseModel):
    id: int
    start_time: str
    end_time: str

class AvailableSlotResponse(BaseModel):
    id: int
    start_time: str
    end_time: str
    is_available: bool
