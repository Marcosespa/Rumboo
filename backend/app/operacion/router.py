from fastapi import APIRouter, Query, Request
from sqlalchemy import func, or_, select
from app.deps import DB, User
from app.models import Conductor, CuentaSatelital, Posicion, Vehiculo, Viaje
from app.schemas import TransitionInput, ViajeInput
from app.services.monitoreo import reserve_job
from app.services.satrack_client import dispatch
from app.services.viajes import create_trip, get_trip, serialize_position, serialize_trip, transition

router = APIRouter(prefix="/api/viajes", tags=["Viajes"])


@router.get("")
def listing(user: User, db: DB, estado: str = "", q: str = "", page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    query = select(Viaje).join(Vehiculo).join(Conductor).where(Viaje.transportadora_id == user.transportadora_id)
    if estado:
        query = query.where(Viaje.estado == estado)
    if q.strip():
        pattern = f"%{q.strip()[:100]}%"
        query = query.where(or_(Viaje.manifiesto.ilike(pattern), Vehiculo.placa.ilike(pattern), Conductor.nombre.ilike(pattern)))
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    trips = db.scalars(query.order_by(Viaje.id.desc()).offset((page - 1) * page_size).limit(page_size))
    return {"items": [serialize_trip(db, t) for t in trips], "total": total, "page": page, "page_size": page_size}


@router.post("", status_code=201)
async def create(data: ViajeInput, user: User, db: DB, request: Request):
    trip = create_trip(db, user, data)
    result = serialize_trip(db, trip, detail=True)
    if trip.estado == "registrado":
        account = db.scalar(select(CuentaSatelital).where(CuentaSatelital.transportadora_id == user.transportadora_id))
        if account and account.estado != "credenciales_invalidas":
            job = reserve_job(db, account, request.app.state.settings)
            await dispatch(request.app, job)
    return result


@router.get("/{trip_id}")
def detail(trip_id: int, user: User, db: DB):
    return serialize_trip(db, get_trip(db, user.transportadora_id, trip_id), detail=True)


@router.get("/{trip_id}/posiciones")
def positions(trip_id: int, user: User, db: DB, limit: int = Query(1000, ge=1, le=2000)):
    get_trip(db, user.transportadora_id, trip_id)
    rows = list(db.scalars(select(Posicion).where(Posicion.viaje_id == trip_id, Posicion.transportadora_id == user.transportadora_id).order_by(Posicion.capturado_en.desc(), Posicion.id.desc()).limit(limit)))
    return [serialize_position(p) for p in reversed(rows)]


@router.post("/{trip_id}/transiciones")
def change(trip_id: int, data: TransitionInput, user: User, db: DB):
    return serialize_trip(db, transition(db, user, trip_id, data), detail=True)
