from datetime import datetime, timedelta, timezone
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, Field, SecretStr, field_validator
from app.operacion.validadores import normalize_plate


class AccountInput(BaseModel):
    usuario: str = Field(min_length=1, max_length=200)
    password: SecretStr
    @field_validator("password")
    @classmethod
    def password_required(cls, value):
        if not value.get_secret_value():
            raise ValueError("La contraseña de Satrack es obligatoria")
        return value


class CallbackPosition(BaseModel):
    plate: str
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    speed_kmh: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    status: str = Field(default="", max_length=80)
    address: str = Field(default="", max_length=2000)
    reported_at: datetime | None = None
    reported_at_raw: str = Field(default="", max_length=250)
    _plate = field_validator("plate")(normalize_plate)

    @field_validator("reported_at")
    @classmethod
    def valid_timestamp(cls, value):
        if value is not None:
            if value.tzinfo is None:
                raise ValueError("La hora GPS debe incluir zona horaria")
            if value > datetime.now(timezone.utc) + timedelta(minutes=5):
                raise ValueError("La hora GPS no puede estar en el futuro")
        return value


class CallbackVehicle(BaseModel):
    plate: str
    name: str = ""
    _plate = field_validator("plate")(normalize_plate)


class CallbackError(BaseModel):
    code: str = Field(max_length=80)
    message: str = Field(max_length=1000)
    plate: str | None = None


class CallbackInput(BaseModel):
    job_id: UUID
    type: Literal["positions", "vehicles"]
    status: Literal["ok", "partial", "failed"]
    finished_at: datetime
    positions: list[CallbackPosition] = Field(default_factory=list, max_length=1000)
    vehicles: list[CallbackVehicle] = Field(default_factory=list, max_length=5000)
    errors: list[CallbackError] = Field(default_factory=list, max_length=1000)
    @field_validator("finished_at")
    @classmethod
    def finished_timezone(cls, value):
        if value.tzinfo is None:
            raise ValueError("finished_at debe incluir zona horaria")
        return value
