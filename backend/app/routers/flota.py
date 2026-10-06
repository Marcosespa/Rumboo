from fastapi import APIRouter
from sqlalchemy import select
from app.deps import DB, User
from app.models import Conductor, Vehiculo
from app.services.viajes import serialize_driver, serialize_vehicle

router = APIRouter(prefix="/api", tags=["Flota"])


@router.get("/vehiculos")
def vehicles(user: User, db: DB):
    return [serialize_vehicle(db, v) for v in db.scalars(select(Vehiculo).where(Vehiculo.transportadora_id == user.transportadora_id).order_by(Vehiculo.placa))]


@router.get("/conductores")
def drivers(user: User, db: DB):
    return [serialize_driver(d) for d in db.scalars(select(Conductor).where(Conductor.transportadora_id == user.transportadora_id).order_by(Conductor.nombre))]
