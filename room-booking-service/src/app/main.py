from fastapi import FastAPI
from app.api.v1.auth import router as auth_router
from app.api.v1.rooms import router as rooms_router
from app.api.v1.slots import router as slots_router
from app.api.v1.bookings import router as bookings_router

app = FastAPI(title="Room Booking Service")

app.include_router(auth_router, prefix="/api/v1")
app.include_router(rooms_router, prefix="/api/v1")
app.include_router(slots_router, prefix="/api/v1")
app.include_router(bookings_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Room Booking Service API"}