import time
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
from app.acceso import servicio
from app.acceso.deps import User, bearer
from app.acceso.schemas import LoginInput
from app.core.web import DB

router = APIRouter(prefix="/api/auth", tags=["Sesión"])


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
    token, user = servicio.authenticate(db, data.usuario, data.password.get_secret_value(), request.app.state.settings.session_days)
    return {"token": token, "usuario": servicio.user_info(user)}


@router.get("/me")
def me(user: User):
    return servicio.user_info(user)


@router.post("/logout")
def logout(user: User, db: DB, credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)]):
    servicio.revoke_session(db, credentials.credentials)
    return {"status": "ok"}


configuracion_router = APIRouter(prefix="/api/configuracion", tags=["Configuración"])


@configuracion_router.get("")
def configuracion(user: User, db: DB):
    return servicio.configuracion(db, user.transportadora_id)
