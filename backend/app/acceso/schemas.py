from pydantic import BaseModel, Field, SecretStr


class LoginInput(BaseModel):
    usuario: str = Field(min_length=1, max_length=100)
    password: SecretStr
