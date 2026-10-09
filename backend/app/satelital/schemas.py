from datetime import datetime, timedelta, timezone
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator
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


class DatosGPS(BaseModel):
    plate: str = Field(max_length=100)
    name: str = Field(default="", max_length=200)
    device_id: str = Field(default="", max_length=100)
    lat: float | None = Field(default=None, ge=-90, le=90, allow_inf_nan=False)
    lng: float | None = Field(default=None, ge=-180, le=180, allow_inf_nan=False)
    speed_kmh: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    status: str = Field(default="", max_length=80)
    address: str = Field(default="", max_length=2000)
    reported_at: datetime | None = None
    reported_at_raw: str = Field(default="", max_length=250)

    @field_validator("reported_at")
    @classmethod
    def valid_timestamp(cls, value):
        if value is not None:
            if value.tzinfo is None:
                raise ValueError("La hora GPS debe incluir zona horaria")
            if value > datetime.now(timezone.utc) + timedelta(minutes=5):
                raise ValueError("La hora GPS no puede estar en el futuro")
        return value


class CallbackPosition(DatosGPS):
    _plate = field_validator("plate")(normalize_plate)


class CallbackVehicle(DatosGPS):
    """Conserva filas de flota con placa no importable para su revisión en el resultado."""


class CallbackError(BaseModel):
    code: str = Field(max_length=60)
    message: str = Field(max_length=1000)
    plate: str | None = Field(default=None, max_length=100)


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


class JobState(BaseModel):
    job_id: UUID
    type: Literal["positions", "vehicles"]
    status: Literal["queued", "running", "done"]
    result: CallbackInput | None = None


class AccountDTO(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: int
    transportadora_id: int = Field(exclude=True)
    usuario: str
    proveedor: str
    estado: str
    fallos_consecutivos: int
    ultima_consulta_ok: datetime | None
    ultimo_error: str | None
    backoff_hasta: datetime | None
    consulta_pendiente: bool


class PosicionDTO(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)
    id: int
    lat: float | None
    lng: float | None
    velocidad_kmh: float | None
    direccion: str
    estado_gps: str
    reportado_en: datetime | None
    reportado_texto: str
    capturado_en: datetime
    viaje_id: int | None


class EstadoVehiculoDTO(BaseModel):
    model_config = ConfigDict(frozen=True)
    en_satelital: bool | None = None
    alias: str = ""
    device_id: str = ""
    ultima_posicion: PosicionDTO | None = None


class ConsultaDTO(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)
    job_id: str
    tipo: str
    estado: str
    placas: list[str]
    enviado_en: datetime
    respondido_en: datetime | None
    intentos: int
    error_codigo: str | None
    error_detalle: str | None
    resultado: dict | None
