from datetime import date
from sqlalchemy import Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    slot_id: Mapped[int] = mapped_column(ForeignKey("slots.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    booking_date: Mapped[date] = mapped_column(Date)

    __table_args__ = (
        UniqueConstraint("room_id", "slot_id", "booking_date", name="uq_room_slot_date"),
    )