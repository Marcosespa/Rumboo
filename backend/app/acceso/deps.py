from typing import Annotated
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db import get_db, now, aware
from app.models import Sesion, Usuario
from app.security import token_hash

DB = Annotated[Session, Depends(get_db)]
bearer = HTTPBearer(auto_error=False)


def current_user(db: DB, credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]):
    if credentials is None:
        raise HTTPException(401, "Inicia sesión para continuar")
    session = db.get(Sesion, token_hash(credentials.credentials))
    if session is None or aware(session.expira_en) <= now() or not session.usuario.activo:
        raise HTTPException(401, "Tu sesión venció; vuelve a entrar")
    return session.usuario


User = Annotated[Usuario, Depends(current_user)]
