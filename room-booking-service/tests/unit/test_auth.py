import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth import register, login
from app.schemas.auth import RegisterRequest, LoginRequest
from app.models.user import User, UserRole
from app.core.exceptions import Conflict, Unauthorized


def make_mock_result(scalar_return):
    """Создаёт мок результата execute с правильным scalar_one_or_none"""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = scalar_return
    return mock_result


@pytest.mark.asyncio
async def test_register_success():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        make_mock_result(None),  # username не занят
        make_mock_result(None),  # email не занят
    ]
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    
    async def mock_refresh(user):
        user.id = 1
    mock_db.refresh = mock_refresh

    data = RegisterRequest(
        username="newuser",
        email="newuser@example.com",
        password="password123",
    )

    result = await register(mock_db, data)

    assert result.username == "newuser"
    assert result.email == "newuser@example.com"
    assert result.role == UserRole.employee
    assert result.id == 1


@pytest.mark.asyncio
async def test_register_duplicate_username():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = make_mock_result(MagicMock())

    data = RegisterRequest(
        username="existing",
        email="new@example.com",
        password="password123",
    )

    with pytest.raises(Conflict):
        await register(mock_db, data)


@pytest.mark.asyncio
async def test_register_duplicate_email():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        make_mock_result(None),   # username свободен
        make_mock_result(MagicMock()),  # email занят
    ]

    data = RegisterRequest(
        username="newuser",
        email="existing@example.com",
        password="password123",
    )

    with pytest.raises(Conflict):
        await register(mock_db, data)


@pytest.mark.asyncio
async def test_login_success():
    mock_db = AsyncMock(spec=AsyncSession)
    user = MagicMock()
    user.id = 1
    user.username = "testuser"
    user.hashed_password = "hashed_password"
    user.role = UserRole.employee
    mock_db.execute.return_value = make_mock_result(user)

    data = LoginRequest(username="testuser", password="password123")

    with patch("app.services.auth.verify_password", return_value=True):
        with patch("app.services.auth.create_access_token", return_value="test_token"):
            result = await login(mock_db, data)

    assert result.access_token == "test_token"


@pytest.mark.asyncio
async def test_login_user_not_found():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = make_mock_result(None)

    data = LoginRequest(username="nonexistent", password="password123")

    with pytest.raises(Unauthorized):
        await login(mock_db, data)


@pytest.mark.asyncio
async def test_login_wrong_password():
    mock_db = AsyncMock(spec=AsyncSession)
    user = MagicMock()
    user.hashed_password = "hashed_password"
    mock_db.execute.return_value = make_mock_result(user)

    data = LoginRequest(username="testuser", password="wrong_password")

    with patch("app.services.auth.verify_password", return_value=False):
        with pytest.raises(Unauthorized):
            await login(mock_db, data)