from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import Conflict, Unauthorized

async def register(db: AsyncSession, data: RegisterRequest):
    result = await db.execute(select(User).where(User.username == data.username))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise Conflict("Username already exist")
    result = await db.execute(select(User).where(User.email == data.email))
    existing_email = result.scalar_one_or_none()
    if existing_email:
        raise Conflict("Email already exist")
    
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse(id=user.id, username=user.username, email=user.email, role=user.role)

async def login(db: AsyncSession, data: LoginRequest):
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()
    if not user:
        raise Unauthorized("Invalid credentials")
    if not verify_password(data.password, user.hashed_password):
        raise Unauthorized("Invalid credentials")
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return TokenResponse(access_token=token)