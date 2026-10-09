from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.operacion.validadores import normalize_phone, normalize_plate


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


class ConductorDTO(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)
    id: int
    nombre: str
    cedula: str
    telefono: str
    autoriza_contacto: bool


class VehiculoDTO(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)
    id: int
    transportadora_id: int = Field(exclude=True)
    placa: str
    propietario: str


class RemesaDTO(RemesaInput):
    model_config = ConfigDict(frozen=True, from_attributes=True)
    id: int


class ViajeImportadoDTO(BaseModel):
    model_config = ConfigDict(frozen=True)
    manifiesto: str
    id: int


class ErrorImportacionDTO(BaseModel):
    """Error de un manifiesto: filas de Excel, columna y mensaje; nunca el valor de la celda."""
    model_config = ConfigDict(frozen=True)
    manifiesto: str
    filas: tuple[int, ...]
    campo: str | None
    mensaje: str


class ResultadoImportacionDTO(BaseModel):
    model_config = ConfigDict(frozen=True)
    creados: tuple[ViajeImportadoDTO, ...]
    errores: tuple[ErrorImportacionDTO, ...]


class ViajeDTO(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: int
    transportadora_id: int = Field(exclude=True)
    manifiesto: str
    origen: str
    destino: str
    estado: str
    salida_estimada: datetime
    llegada_estimada: datetime
    peso_salida_kg: float
    creado_en: datetime
    actualizado_en: datetime
    conductor: ConductorDTO
    vehiculo: VehiculoDTO
    remesas: tuple[RemesaDTO, ...] = ()
    eventos: tuple[dict, ...] = ()
