from fastapi import APIRouter
from app.acceso.deps import User
from app.core.web import DB
from app.indicadores import servicio

router = APIRouter(prefix="/api/panel", tags=["Panel"])


@router.get("")
def panel(user: User, db: DB):
    return servicio.panel(db, user.transportadora_id)
