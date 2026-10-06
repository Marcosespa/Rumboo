from typing import Literal
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    satrack_service_api_key: str = Field(min_length=16)
    callback_secret: str = ""
    # Vacío = modo independiente: el resultado solo se consulta con GET /v1/jobs/{job_id}.
    callback_url: str = ""
    provider: Literal["satrack", "simulator"] = "satrack"
    max_concurrency: int = Field(default=3, ge=1, le=10)
    max_queued_jobs: int = Field(default=50, ge=1, le=1000)
    max_retained_jobs: int = Field(default=1000, ge=1, le=10000)
    job_timeout_s: float = Field(default=120, gt=0)
    max_sessions: int = Field(default=3, ge=1, le=10)
    session_idle_s: int = Field(default=900, ge=30)
    headless: bool = True
    data_dir: str = "/data/satrack"
    chrome_binary: str = ""
    chromedriver_path: str = ""

    @model_validator(mode="after")
    def validate_callback(self):
        if self.callback_url:
            if not self.callback_url.startswith(("http://", "https://")):
                raise ValueError("CALLBACK_URL debe ser una URL HTTP o HTTPS")
            if len(self.callback_secret) < 16:
                raise ValueError("CALLBACK_SECRET requiere al menos 16 caracteres cuando hay callback")
        return self
