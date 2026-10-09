from pydantic import BaseModel, ConfigDict, Field, SecretStr


class LoginInput(BaseModel):
    usuario: str = Field(min_length=1, max_length=100)
    password: SecretStr


class TransportadoraDTO(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: int
    nombre: str


class ConfiguracionDTO(BaseModel):
    """Parámetros vigentes de la transportadora; solo los que ya usa el backend."""
    model_config = ConfigDict(frozen=True)
    frecuencia_consulta_min: int
    zona_horaria: str = "America/Bogota"


class UsuarioDTO(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: int
    usuario: str
    nombre: str
    transportadora_id: int = Field(exclude=True)
    transportadora: TransportadoraDTO
