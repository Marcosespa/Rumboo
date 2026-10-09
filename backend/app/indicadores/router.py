from fastapi import APIRouter, Request
from app.acceso.deps import User
from app.core.web import DB

router = APIRouter(prefix="/api/panel", tags=["Panel"])


@router.get("")
def panel(user: User, db: DB, request: Request):
    return request.app.state.consultas.panel(db, user.transportadora_id)
