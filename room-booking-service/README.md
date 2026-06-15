# Room Booking Service

Сервис для бронирования переговорных комнат в коворкинге.

Стек: FastAPI + PostgreSQL/SQLite + SQLAlchemy + JWT + Docker.

## Быстрый старт

```bash
docker compose up --build
```

Приложение на http://localhost:8000, Swagger на http://localhost:8000/docs.

## Запуск без Docker

```bash
poetry install
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

По умолчанию используется SQLite. Для PostgreSQL задайте `DATABASE_URL`.

## docker run

```bash
docker build -t room-booking-service .
docker run -p 8000:8000 room-booking-service
```

Работает с SQLite без дополнительных настроек.

## Seed

При первом запуске автоматически создаются таблицы и начальные данные:
- администратор `admin` / `admin123`
- 3 комнаты: Переговорная1–3
- 5 слотов: 09:00–11:00, 11:00–13:00, 13:00–15:00, 15:00–17:00, 17:00–19:00

## API

**Без аутентификации**
- `POST /api/v1/auth/register` — регистрация
- `POST /api/v1/auth/login` — получить JWT
- `GET /api/v1/rooms/` — список комнат
- `GET /api/v1/slots/` — список слотов
- `POST /api/v1/slots/` — создать слот

**Требуют JWT (заголовок `Authorization: Bearer <token>`)**
- `GET /api/v1/rooms/availability?date=YYYY-MM-DD` — доступность слотов на дату
- `POST /api/v1/bookings/` — создать бронь
- `GET /api/v1/bookings/` — мои брони
- `DELETE /api/v1/bookings/{id}` — отменить бронь

Права: сотрудник управляет только своими бронями, администратор — любыми.

## Тесты

```bash
poetry run pytest -v
```

35 тестов: 15 unit + 20 integration. Используется SQLite in-memory.

## Переменные окружения

- `DATABASE_URL` — по умолчанию `sqlite+aiosqlite:///./room_booking.db`
- `SECRET_KEY` — по умолчанию `secret_key`
- `ACCESS_TOKEN_EXPIRE_MINUTES` — по умолчанию `1440`
