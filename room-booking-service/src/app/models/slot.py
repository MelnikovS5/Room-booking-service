import datetime
from sqlalchemy import Time
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Slot(Base):
    __tablename__ = "slots"

    id: Mapped[int] = mapped_column(primary_key=True)
    start_time: Mapped[datetime.time] = mapped_column(Time())
    end_time: Mapped[datetime.time] = mapped_column(Time())