import re
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator, model_validator


class Account(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(min_length=1, max_length=100)
    username: str = Field(min_length=1, max_length=200)
    password: SecretStr


class JobRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    job_id: UUID
    type: Literal["positions", "vehicles"]
    account: Account
    plates: list[str] = Field(default_factory=list, max_length=1000)

    @field_validator("plates")
    @classmethod
    def normalize_plates(cls, values):
        normalized = list(dict.fromkeys(re.sub(r"[\s-]", "", p).upper() for p in values))
        if any(not re.fullmatch(r"[A-Z]{3}\d{3}", p) for p in normalized):
            raise ValueError("Las placas deben tener tres letras y tres números")
        return normalized

    @model_validator(mode="after")
    def validate_positions(self):
        if self.type == "positions" and not self.plates:
            raise ValueError("positions requiere al menos una placa")
        if not self.account.password.get_secret_value():
            raise ValueError("La contraseña es obligatoria")
        return self


class Position(BaseModel):
    plate: str
    name: str = ""
    device_id: str = ""
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    speed_kmh: float | None = Field(default=None, ge=0)
    status: str = "desconocido"
    address: str = ""
    reported_at: datetime | None = None
    reported_at_raw: str = ""


class Vehicle(Position):
    """La flota incluye los datos disponibles, conservando el contrato de placa/nombre."""


class JobError(BaseModel):
    code: str
    message: str
    plate: str | None = None


class CallbackPayload(BaseModel):
    job_id: UUID
    type: Literal["positions", "vehicles"]
    status: Literal["ok", "partial", "failed"]
    finished_at: datetime
    positions: list[Position] = Field(default_factory=list)
    vehicles: list[Vehicle] = Field(default_factory=list)
    errors: list[JobError] = Field(default_factory=list)


class JobStatus(BaseModel):
    """Estado de un job consultable con GET /v1/jobs/{job_id} durante una hora."""
    job_id: UUID
    type: Literal["positions", "vehicles"]
    status: Literal["queued", "running", "done"]
    received_at: datetime
    started_at: datetime | None = None
    callback: Literal["pending", "delivered", "failed", "disabled"] = "pending"
    result: CallbackPayload | None = None
