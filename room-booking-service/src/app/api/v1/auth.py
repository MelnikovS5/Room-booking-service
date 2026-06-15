from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.services.auth import register, login

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse)
async def register_endpoint(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await register(db, data)

@router.post("/login", response_model=TokenResponse)
async def login_endpoint(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await login(db, data)