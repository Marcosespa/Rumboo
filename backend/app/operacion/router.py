from fastapi import APIRouter, Query, Request
from app.acceso.deps import User
from app.core.web import DB
from app.operacion import servicio
from app.operacion.schemas import TransitionInput, ViajeInput

router = APIRouter(prefix="/api", tags=["Viajes"])


@router.get("/viajes")
def listing(user: User, db: DB, estado: str = "", q: str = "", page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    return servicio.list_trips(db, user.transportadora_id, estado, q, page, page_size)


@router.post("/viajes", status_code=201)
async def create(data: ViajeInput, user: User, db: DB, request: Request):
    trip = servicio.create_trip(db, user, data)
    await request.app.state.eventos.despachar(db)
    db.refresh(trip)
    return servicio.serialize_trip(db, trip, detail=True)


@router.get("/viajes/{trip_id}")
def detail(trip_id: int, user: User, db: DB):
    return servicio.serialize_trip(db, servicio.get_trip(db, user.transportadora_id, trip_id), detail=True)


@router.post("/viajes/{trip_id}/transiciones")
def change(trip_id: int, data: TransitionInput, user: User, db: DB):
    return servicio.serialize_trip(db, servicio.transition(db, user, trip_id, data), detail=True)


@router.get("/vehiculos", tags=["Flota"])
def vehicles(user: User, db: DB):
    return servicio.list_vehicles(db, user.transportadora_id)


@router.get("/conductores", tags=["Flota"])
def drivers(user: User, db: DB):
    return servicio.list_drivers(db, user.transportadora_id)
