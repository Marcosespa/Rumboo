from pydantic import BaseModel, ConfigDict, Field, SecretStr


class LoginInput(BaseModel):
    usuario: str = Field(min_length=1, max_length=100)
    password: SecretStr


class TransportadoraDTO(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: int
    nombre: str


class UsuarioDTO(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: int
    usuario: str
    nombre: str
    transportadora_id: int = Field(exclude=True)
    transportadora: TransportadoraDTO
