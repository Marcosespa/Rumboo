from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+psycopg://rumboo:rumboo@db:5432/rumboo"
    secret_key: str = Field(min_length=32)
    satrack_service_url: str = "http://satrack:8080"
    satrack_service_api_key: str = Field(min_length=16)
    callback_secret: str = Field(min_length=16)
    cors_origins: str = "http://localhost:5173"
    session_days: int = Field(default=7, ge=1, le=30)
    scheduler_enabled: bool = True
    scheduler_interval_s: int = Field(default=60, ge=1)
    consulta_timeout_s: int = Field(default=240, ge=10)


def get_settings():
    return Settings()
