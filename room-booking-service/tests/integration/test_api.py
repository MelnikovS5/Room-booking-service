import datetime
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.room import Room
from app.models.slot import Slot
from app.models.booking import Booking
from app.core.security import hash_password, create_access_token
from app.models.user import User, UserRole


@pytest.mark.asyncio
async def test_register(client: AsyncClient, db_session: AsyncSession):
    response = await client.post("/api/v1/auth/register", json={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpass123",
        "role": "employee",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient, regular_user):
    response = await client.post("/api/v1/auth/register", json={
        "username": "user",
        "email": "user@example.com",
        "password": "user123456",
        "role": "employee",
    })
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login(client: AsyncClient, regular_user):
    response = await client.post("/api/v1/auth/login", json={
        "username": "user",
        "password": "user12345",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid(client: AsyncClient):
    response = await client.post("/api/v1/auth/login", json={
        "username": "nonexistent",
        "password": "longenough123",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_rooms(client: AsyncClient, db_session: AsyncSession):
    db_session.add(Room(name="Test Room", description="For testing"))
    await db_session.flush()

    response = await client.get("/api/v1/rooms/")
    assert response.status_code == 200
    rooms = response.json()
    assert len(rooms) >= 1
    assert any(r["name"] == "Test Room" for r in rooms)


@pytest.mark.asyncio
async def test_get_slots(client: AsyncClient, db_session: AsyncSession):
    db_session.add(Slot(start_time=datetime.time(9, 0), end_time=datetime.time(11, 0)))
    await db_session.flush()

    response = await client.get("/api/v1/slots/")
    assert response.status_code == 200
    slots = response.json()
    assert len(slots) >= 1


@pytest.mark.asyncio
async def test_create_slot(client: AsyncClient):
    response = await client.post("/api/v1/slots/", json={
        "start_time": "10:00",
        "end_time": "12:00",
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data


@pytest.mark.asyncio
async def test_create_booking(user_client: AsyncClient, db_session: AsyncSession):
    room = Room(name="Booking Room", description="Test")
    db_session.add(room)
    await db_session.flush()

    slot = Slot(start_time=datetime.time(9, 0), end_time=datetime.time(11, 0))
    db_session.add(slot)
    await db_session.flush()

    response = await user_client.post("/api/v1/bookings/", json={
        "room_id": room.id,
        "slot_id": slot.id,
        "booking_date": "2026-07-01",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["room_id"] == room.id
    assert data["slot_id"] == slot.id
    assert data["booking_date"] == "2026-07-01"


@pytest.mark.asyncio
async def test_create_booking_room_not_found(user_client: AsyncClient):
    response = await user_client.post("/api/v1/bookings/", json={
        "room_id": 9999,
        "slot_id": 1,
        "booking_date": "2026-07-01",
    })
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_booking_slot_not_found(user_client: AsyncClient, db_session: AsyncSession):
    room = Room(name="Slot Test Room", description="Test")
    db_session.add(room)
    await db_session.flush()

    response = await user_client.post("/api/v1/bookings/", json={
        "room_id": room.id,
        "slot_id": 9999,
        "booking_date": "2026-07-01",
    })
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_booking_conflict(user_client: AsyncClient, db_session: AsyncSession):
    room = Room(name="Conflict Room", description="Test")
    db_session.add(room)
    await db_session.flush()

    slot = Slot(start_time=datetime.time(9, 0), end_time=datetime.time(11, 0))
    db_session.add(slot)
    await db_session.flush()

    await user_client.post("/api/v1/bookings/", json={
        "room_id": room.id,
        "slot_id": slot.id,
        "booking_date": "2026-07-01",
    })

    response = await user_client.post("/api/v1/bookings/", json={
        "room_id": room.id,
        "slot_id": slot.id,
        "booking_date": "2026-07-01",
    })
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_get_my_bookings(user_client: AsyncClient, db_session: AsyncSession):
    room = Room(name="My Bookings Room", description="Test")
    db_session.add(room)
    await db_session.flush()

    slot = Slot(start_time=datetime.time(9, 0), end_time=datetime.time(11, 0))
    db_session.add(slot)
    await db_session.flush()

    await user_client.post("/api/v1/bookings/", json={
        "room_id": room.id,
        "slot_id": slot.id,
        "booking_date": "2026-07-01",
    })

    response = await user_client.get("/api/v1/bookings/")
    assert response.status_code == 200
    bookings = response.json()
    assert len(bookings) >= 1


@pytest.mark.asyncio
async def test_delete_own_booking(user_client: AsyncClient, db_session: AsyncSession):
    room = Room(name="Delete Room", description="Test")
    db_session.add(room)
    await db_session.flush()

    slot = Slot(start_time=datetime.time(9, 0), end_time=datetime.time(11, 0))
    db_session.add(slot)
    await db_session.flush()

    create_resp = await user_client.post("/api/v1/bookings/", json={
        "room_id": room.id,
        "slot_id": slot.id,
        "booking_date": "2026-07-01",
    })
    booking_id = create_resp.json()["id"]

    response = await user_client.delete(f"/api/v1/bookings/{booking_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Booking cancelled"}


@pytest.mark.asyncio
async def test_delete_other_booking_forbidden(user_client: AsyncClient, db_session: AsyncSession):
    room = Room(name="Forbidden Room", description="Test")
    db_session.add(room)
    await db_session.flush()

    slot = Slot(start_time=datetime.time(9, 0), end_time=datetime.time(11, 0))
    db_session.add(slot)
    await db_session.flush()

    create_resp = await user_client.post("/api/v1/bookings/", json={
        "room_id": room.id,
        "slot_id": slot.id,
        "booking_date": "2026-07-01",
    })
    booking_id = create_resp.json()["id"]

    other_user = User(
        username="other", email="other@test.com",
        hashed_password=hash_password("other123"), role=UserRole.employee
    )
    db_session.add(other_user)
    await db_session.flush()
    other_token = create_access_token({"sub": str(other_user.id), "role": other_user.role.value})

    from httpx import ASGITransport, AsyncClient
    from app.main import app
    from app.db.session import get_db

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as other_client:
        other_client.headers["Authorization"] = f"Bearer {other_token}"
        response = await other_client.delete(f"/api/v1/bookings/{booking_id}")
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_booking_as_admin(auth_client: AsyncClient, user_client: AsyncClient, db_session: AsyncSession):
    room = Room(name="Admin Delete Room", description="Test")
    db_session.add(room)
    await db_session.flush()

    slot = Slot(start_time=datetime.time(9, 0), end_time=datetime.time(11, 0))
    db_session.add(slot)
    await db_session.flush()

    create_resp = await user_client.post("/api/v1/bookings/", json={
        "room_id": room.id,
        "slot_id": slot.id,
        "booking_date": "2026-07-01",
    })
    booking_id = create_resp.json()["id"]

    response = await auth_client.delete(f"/api/v1/bookings/{booking_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Booking cancelled"}


@pytest.mark.asyncio
async def test_delete_booking_not_found(auth_client: AsyncClient):
    response = await auth_client.delete("/api/v1/bookings/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    response = await client.get("/api/v1/bookings/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_rooms_availability_all_free(user_client: AsyncClient, db_session: AsyncSession):
    db_session.add(Room(name="Avail Room", description="Test"))
    await db_session.flush()
    db_session.add(Slot(start_time=datetime.time(9, 0), end_time=datetime.time(11, 0)))
    await db_session.flush()

    response = await user_client.get("/api/v1/rooms/availability", params={"date": "2026-07-01"})
    assert response.status_code == 200
    data = response.json()
    assert any(r["room_name"] == "Avail Room" for r in data)


@pytest.mark.asyncio
async def test_rooms_availability_slot_booked(user_client: AsyncClient, db_session: AsyncSession):
    room = Room(name="Booked Room", description="Test")
    db_session.add(room)
    await db_session.flush()
    slot = Slot(start_time=datetime.time(9, 0), end_time=datetime.time(11, 0))
    db_session.add(slot)
    await db_session.flush()

    booking_resp = await user_client.post("/api/v1/bookings/", json={
        "room_id": room.id, "slot_id": slot.id, "booking_date": "2026-07-01",
    })
    assert booking_resp.status_code == 200

    response = await user_client.get("/api/v1/rooms/availability", params={"date": "2026-07-01"})
    assert response.status_code == 200
    data = response.json()
    for room_data in data:
        if room_data["room_id"] == room.id:
            for s in room_data["slots"]:
                if s["slot_id"] == slot.id:
                    assert s["is_available"] is False


@pytest.mark.asyncio
async def test_rooms_availability_unauthorized(client: AsyncClient):
    response = await client.get("/api/v1/rooms/availability", params={"date": "2026-07-01"})
    assert response.status_code == 401