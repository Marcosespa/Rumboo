from datetime import datetime, timedelta, timezone
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator, model_validator
from app.validators import normalize_phone, normalize_plate


class LoginInput(BaseModel):
    usuario: str = Field(min_length=1, max_length=100)
    password: SecretStr


class ConductorInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    nombre: str = Field(min_length=1, max_length=200)
    cedula: str = Field(pattern=r"^\d{6,10}$")
    telefono: str
    autoriza_contacto: bool = False
    _phone = field_validator("telefono")(normalize_phone)


class VehiculoInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    placa: str
    propietario: str = Field(default="", max_length=200)
    _plate = field_validator("placa")(normalize_plate)


class RemesaInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    numero: str = Field(min_length=1, max_length=80)
    cliente: str = Field(min_length=1, max_length=200)
    peso_kg: float = Field(gt=0, le=100000, allow_inf_nan=False)
    cantidad: int | None = Field(default=None, gt=0)


class ViajeInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    manifiesto: str = Field(min_length=1, max_length=40)
    origen: str = Field(min_length=1, max_length=200)
    destino: str = Field(min_length=1, max_length=200)
    salida_estimada: datetime
    llegada_estimada: datetime
    conductor: ConductorInput
    vehiculo: VehiculoInput
    remesas: list[RemesaInput] = Field(min_length=1, max_length=100)

    @field_validator("salida_estimada", "llegada_estimada")
    @classmethod
    def timezone_required(cls, value):
        if value.tzinfo is None:
            raise ValueError("La fecha debe incluir su zona horaria")
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def validate_trip(self):
        if self.origen.casefold() == self.destino.casefold():
            raise ValueError("El origen y el destino deben ser distintos")
        if self.llegada_estimada <= self.salida_estimada:
            raise ValueError("La llegada debe ser posterior a la salida")
        if len({r.numero for r in self.remesas}) != len(self.remesas):
            raise ValueError("Los números de remesa no pueden repetirse")
        return self


class TransitionInput(BaseModel):
    estado: Literal["programado", "en_ruta", "entregado", "cancelado"]
    motivo: str = Field(default="", max_length=1000)


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
