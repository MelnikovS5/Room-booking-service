from pydantic import BaseModel, Field
from app.models.user import UserRole

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=200)
    role: UserRole = Field(default=UserRole.employee)

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=8, max_length=200)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole

