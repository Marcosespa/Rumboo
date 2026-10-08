from cryptography.fernet import Fernet
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+psycopg://rumboo:rumboo@db:5432/rumboo"
    secret_key: str = Field(min_length=32)
    # Claves Fernet separadas por coma, la vigente primero. Rotar: anteponer una nueva y ejecutar `cli recifrar`.
    encryption_keys: str = ""
    satrack_service_url: str = "http://satrack:8080"
    satrack_service_api_key: str = Field(min_length=16)
    callback_secret: str = Field(min_length=16)
    cors_origins: str = "http://localhost:5173"
    session_days: int = Field(default=7, ge=1, le=30)
    scheduler_enabled: bool = True
    scheduler_interval_s: int = Field(default=60, ge=1)
    reconciliation_interval_s: int = Field(default=5, ge=1)
    eventos_interval_s: int = Field(default=2, ge=1)
    runner_lock_check_s: float = Field(default=1, gt=0)
    consulta_timeout_s: int = Field(default=240, ge=10)

    @field_validator("encryption_keys")
    @classmethod
    def _claves_fernet_validas(cls, value):
        for key in filter(None, map(str.strip, value.split(","))):
            Fernet(key)
        return value

    @property
    def encryption_key_list(self):
        return [key.strip() for key in self.encryption_keys.split(",") if key.strip()]


def get_settings():
    return Settings()
