import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models.user import User, UserRole
from app.core.security import hash_password, create_access_token

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    connection = await engine.connect()
    await connection.begin()
    session = AsyncSession(bind=connection, expire_on_commit=False)
    yield session
    await session.close()
    await connection.rollback()
    await connection.close()


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_user(db_session):
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=hash_password("admin123"),
        role=UserRole.admin,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def regular_user(db_session):
    user = User(
        username="user",
        email="user@example.com",
        hashed_password=hash_password("user12345"),
        role=UserRole.employee,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def admin_token(admin_user):
    return create_access_token({"sub": str(admin_user.id), "role": admin_user.role.value})


@pytest_asyncio.fixture
async def user_token(regular_user):
    return create_access_token({"sub": str(regular_user.id), "role": regular_user.role.value})


async def _make_auth_client(db_session, token):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest_asyncio.fixture
async def auth_client(db_session, admin_token):
    client = await _make_auth_client(db_session, admin_token)
    yield client
    await client.aclose()
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user_client(db_session, user_token):
    client = await _make_auth_client(db_session, user_token)
    yield client
    await client.aclose()
    app.dependency_overrides.clear()