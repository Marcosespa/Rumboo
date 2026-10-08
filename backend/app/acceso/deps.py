from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.acceso.models import Usuario
from app.acceso.servicio import user_for_token
from app.core.web import DB

bearer = HTTPBearer(auto_error=False)


def current_user(db: DB, credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]):
    if credentials is None:
        raise HTTPException(401, "Inicia sesión para continuar")
    user = user_for_token(db, credentials.credentials)
    if user is None:
        raise HTTPException(401, "Tu sesión venció; vuelve a entrar")
    return user


User = Annotated[Usuario, Depends(current_user)]
