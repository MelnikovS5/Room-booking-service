from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_title: str = "Room Booking Service"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/room_booking"
    database_url_sync: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/room_booking"
    secret_key: str = "secret_key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()