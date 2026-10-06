import time
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import HTTPAuthorizationCredentials
from typing import Annotated
from sqlalchemy import delete, select
from app.deps import DB, User, bearer
from app.db import now
from app.models import Sesion, Usuario
from app.schemas import LoginInput
from app.security import create_session, hash_password, token_hash, verify_password

router = APIRouter(prefix="/api/auth", tags=["Sesión"])
DUMMY_HASH = hash_password("invalid-login-placeholder")


def user_info(user):
    return {"id": user.id, "usuario": user.usuario, "nombre": user.nombre,
            "transportadora": {"id": user.transportadora_id, "nombre": user.transportadora.nombre}}


@router.post("/login")
def login(data: LoginInput, db: DB, request: Request):
    address = request.client.host if request.client else "unknown"
    at = time.monotonic()
    with request.app.state.login_lock:
        attempts = request.app.state.login_attempts
        for key in list(attempts):
            attempts[key] = [t for t in attempts[key] if at - t < 300]
            if not attempts[key]:
                del attempts[key]
        if len(attempts.get(address, [])) >= 20:
            raise HTTPException(429, "Demasiados intentos; espera cinco minutos")
        attempts.setdefault(address, []).append(at)
    user = db.scalar(select(Usuario).where(Usuario.usuario == data.usuario.strip()))
    valid = verify_password(data.password.get_secret_value(), user.password_hash if user else DUMMY_HASH)
    if not user or not user.activo or not valid:
        raise HTTPException(401, "Usuario o contraseña incorrectos")
    db.execute(delete(Sesion).where(Sesion.expira_en < now()))
    token = create_session(db, user, request.app.state.settings.session_days)
    return {"token": token, "usuario": user_info(user)}


@router.get("/me")
def me(user: User):
    return user_info(user)


@router.post("/logout")
def logout(user: User, db: DB, credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)]):
    db.execute(delete(Sesion).where(Sesion.token_hash == token_hash(credentials.credentials)))
    db.commit()
    return {"status": "ok"}
