# Room Booking Service

Сервис для бронирования переговорных комнат. FastAPI + PostgreSQL + JWT.

## Быстрый старт

```bash
docker compose up --build
```

Приложение будет доступно на http://localhost:8000.
Swagger-документация: http://localhost:8000/docs.

## Запуск без Docker

```bash
poetry install
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Требуется запущенный PostgreSQL. URL базы задаётся через переменную окружения `DATABASE_URL`.

## Seed

При первом запуске автоматически создаются:
- администратор `admin` / `admin123`
- 3 переговорные комнаты
- 5 временных слотов (09:00–19:00)

## API

| Метод | Путь | Описание |
| POST | /api/v1/auth/register | Регистрация |
| POST | /api/v1/auth/login | Получить JWT-токен |
| GET | /api/v1/rooms/ | Список комнат |
| GET | /api/v1/slots/ | Список слотов |
| POST | /api/v1/slots/ | Создать слот |
| POST | /api/v1/bookings/ | Создать бронь* |
| GET | /api/v1/bookings/ | Мои брони* |
| DELETE | /api/v1/bookings/{id} | Отменить бронь* |

*Требуется заголовок `Authorization: Bearer <token>`.

Права: сотрудник управляет только своими бронями, администратор — любыми.

## Тесты

```bash
poetry run pytest -v
```

32 теста (15 unit + 17 integration), SQLite in-memory.

## Переменные окружения

| Переменная | По умолчанию |
| DATABASE_URL | postgresql+asyncpg://postgres:postgres@localhost:5432/room_booking |
| SECRET_KEY | secret_key |
| ACCESS_TOKEN_EXPIRE_MINUTES | 1440 |
