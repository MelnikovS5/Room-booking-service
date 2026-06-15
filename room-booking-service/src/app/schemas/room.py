from pydantic import BaseModel, Field

class RoomCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str | None = Field(None, max_length=255)

class RoomResponse(BaseModel):
    id: int
    name: str
    description: str | None

