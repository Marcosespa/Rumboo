from datetime import datetime, time
from zoneinfo import ZoneInfo
from fastapi import APIRouter
from sqlalchemy import func, select
from app.db import now
from app.deps import DB, User
from app.models import ACTIVE_STATES, CuentaSatelital, Vehiculo, Viaje
from app.routers.cuenta_satelital import account_info
from app.services.viajes import serialize_trip

router = APIRouter(prefix="/api/panel", tags=["Panel"])


@router.get("")
def panel(user: User, db: DB):
    tenant = user.transportadora_id
    counts = dict(db.execute(select(Viaje.estado, func.count(Viaje.id)).where(Viaje.transportadora_id == tenant).group_by(Viaje.estado)).all())
    today = datetime.combine(now().astimezone(ZoneInfo("America/Bogota")).date(), time.min, ZoneInfo("America/Bogota"))
    delivered = db.scalar(select(func.count(Viaje.id)).where(Viaje.transportadora_id == tenant, Viaje.estado == "entregado", Viaje.actualizado_en >= today))
    fleet = db.scalar(select(func.count(Vehiculo.id)).where(Vehiculo.transportadora_id == tenant, Vehiculo.ultima_posicion_id.is_not(None)))
    account = db.scalar(select(CuentaSatelital).where(CuentaSatelital.transportadora_id == tenant))
    active = db.scalars(select(Viaje).where(Viaje.transportadora_id == tenant, Viaje.estado.in_(ACTIVE_STATES)).order_by(Viaje.id.desc()).limit(10))
    return {"conteos": counts, "entregados_hoy": delivered, "vehiculos_con_posicion": fleet,
            "cuenta_satelital": account_info(db, account), "viajes_activos": [serialize_trip(db, t) for t in active]}
