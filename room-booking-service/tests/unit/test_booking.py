import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.booking import create_booking, get_my_bookings, delete_booking
from app.schemas.booking import BookingCreate, BookingResponse
from app.models.user import User, UserRole
from app.models.booking import Booking
from app.models.room import Room
from app.models.slot import Slot
from app.core.exceptions import NotFound, Conflict, Forbidden


def make_mock_result(scalar_return):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = scalar_return
    mock_result.scalars.return_value.all.return_value = []
    mock_result.scalars.return_value.first.return_value = scalar_return
    return mock_result


@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.id = 1
    user.role = UserRole.employee
    return user


@pytest.fixture
def mock_admin():
    admin = MagicMock(spec=User)
    admin.id = 2
    admin.role = UserRole.admin
    return admin


@pytest.fixture
def mock_room():
    room = MagicMock(spec=Room)
    room.id = 1
    return room


@pytest.fixture
def mock_slot():
    slot = MagicMock(spec=Slot)
    slot.id = 1
    return slot


@pytest.mark.asyncio
async def test_create_booking_success():
    mock_db = AsyncMock()
    mock_db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=MagicMock())),  # room exists
        MagicMock(scalar_one_or_none=MagicMock(return_value=MagicMock())),  # slot exists
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),  # no conflict
    ]
    mock_db.add = MagicMock()
    async def mock_refresh(booking):
        booking.id = 1
    mock_db.refresh = mock_refresh

    data = BookingCreate(room_id=1, slot_id=1, booking_date="2026-06-20")
    user_id = 1

    result = await create_booking(mock_db, data, user_id)

    assert result.room_id == 1
    assert result.slot_id == 1
    assert result.user_id == 1
    assert result.booking_date == "2026-06-20"
    assert result.id == 1


@pytest.mark.asyncio
async def test_create_booking_room_not_found():
    mock_db = AsyncMock()
    mock_db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),
    ]

    data = BookingCreate(room_id=999, slot_id=1, booking_date="2026-06-20")
    user_id = 1

    with pytest.raises(NotFound):
        await create_booking(mock_db, data, user_id)


@pytest.mark.asyncio
async def test_create_booking_slot_not_found():
    mock_db = AsyncMock()
    mock_db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=MagicMock())),  # room exists
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),  # slot not found
    ]

    data = BookingCreate(room_id=1, slot_id=999, booking_date="2026-06-20")
    user_id = 1

    with pytest.raises(NotFound):
        await create_booking(mock_db, data, user_id)


@pytest.mark.asyncio
async def test_create_booking_conflict():
    mock_db = AsyncMock()
    mock_db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=MagicMock())),  # room
        MagicMock(scalar_one_or_none=MagicMock(return_value=MagicMock())),  # slot
        MagicMock(scalar_one_or_none=MagicMock(return_value=MagicMock())),  # conflict exists
    ]

    data = BookingCreate(room_id=1, slot_id=1, booking_date="2026-06-20")
    user_id = 1

    with pytest.raises(Conflict):
        await create_booking(mock_db, data, user_id)


@pytest.mark.asyncio
async def test_get_my_bookings():
    mock_db = AsyncMock()
    bookings = [MagicMock(), MagicMock()]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = bookings
    mock_db.execute.side_effect = [mock_result]

    result = await get_my_bookings(mock_db, 1)

    assert len(result) == 2


@pytest.mark.asyncio
async def test_delete_booking_success_by_owner():
    mock_db = AsyncMock()
    booking = MagicMock()
    booking.user_id = 1
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = booking
    scalars_mock.return_value = scalars_mock
    mock_db.execute.side_effect = [
        MagicMock(scalars=scalars_mock)
    ]
    mock_db.delete = AsyncMock()
    mock_db.commit = AsyncMock()

    user = MagicMock()
    user.id = 1
    user.role = "employee"

    result = await delete_booking(mock_db, 1, user)

    assert result == {"message": "Booking cancelled"}
    mock_db.delete.assert_called_once_with(booking)


@pytest.mark.asyncio
async def test_delete_booking_success_by_admin():
    mock_db = AsyncMock()
    booking = MagicMock()
    booking.user_id = 1
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = booking
    scalars_mock.return_value = scalars_mock
    mock_db.execute.side_effect = [
        MagicMock(scalars=scalars_mock)
    ]
    mock_db.delete = AsyncMock()
    mock_db.commit = AsyncMock()

    admin = MagicMock()
    admin.id = 2
    admin.role = "admin"

    result = await delete_booking(mock_db, 1, admin)

    assert result == {"message": "Booking cancelled"}


@pytest.mark.asyncio
async def test_delete_booking_not_found():
    mock_db = AsyncMock()
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = None
    scalars_mock.return_value = scalars_mock
    mock_db.execute.side_effect = [
        MagicMock(scalars=scalars_mock)
    ]

    user = MagicMock()
    user.id = 1
    user.role = "employee"

    with pytest.raises(NotFound):
        await delete_booking(mock_db, 999, user)


@pytest.mark.asyncio
async def test_delete_booking_forbidden():
    mock_db = AsyncMock()
    booking = MagicMock()
    booking.user_id = 1
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = booking
    scalars_mock.return_value = scalars_mock
    mock_db.execute.side_effect = [
        MagicMock(scalars=scalars_mock)
    ]

    user = MagicMock()
    user.id = 2
    user.role = "employee"

    with pytest.raises(Forbidden):
        await delete_booking(mock_db, 1, user)