from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.acceso.schemas import UsuarioDTO
from app.acceso.servicio import user_for_token
from app.core.web import DB

bearer = HTTPBearer(auto_error=False)


def current_user(db: DB, credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]):
    if credentials is None:
        raise HTTPException(401, "Inicia sesión para continuar")
    user = user_for_token(db, credentials.credentials)
    # Devuelve la conexión al pool: los endpoints que abren su propia sesión no deben retener dos por petición.
    db.rollback()
    if user is None:
        raise HTTPException(401, "Tu sesión venció; vuelve a entrar")
    return user


User = Annotated[UsuarioDTO, Depends(current_user)]
