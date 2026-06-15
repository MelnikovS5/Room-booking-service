import enum
from sqlalchemy import String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class UserRole(str, enum.Enum):
    employee = "employee"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.employee)