import asyncio
from fastapi import APIRouter, Query, Request, Response
from app.acceso.deps import User
from app.core.web import DB, read_body
from app.operacion import excel, servicio
from app.operacion.schemas import TransitionInput, ViajeInput

router = APIRouter(prefix="/api", tags=["Viajes"])


@router.get("/viajes")
def listing(user: User, db: DB, request: Request, estado: str = "", q: str = "",
            page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    return request.app.state.consultas.trips(db, user.transportadora_id, estado, q, page, page_size)


@router.post("/viajes", status_code=201)
async def create(data: ViajeInput, user: User, request: Request):
    state = request.app.state
    def write():
        with state.sessions() as db:
            return servicio.create_trip(db, user, data).id
    trip_id = await asyncio.to_thread(write)
    await state.eventos.despachar()
    await state.despachar_consultas(user.transportadora_id)
    def read():
        with state.sessions() as db:
            return state.consultas.trip(db, user.transportadora_id, trip_id)
    return await asyncio.to_thread(read)


@router.get("/viajes/plantilla")
def template(user: User):
    return Response(excel.plantilla(), media_type=excel.XLSX,
                    headers={"Content-Disposition": 'attachment; filename="plantilla_viajes.xlsx"'})


@router.post("/viajes/importar", openapi_extra={"requestBody": {"required": True, "content": {
    excel.XLSX: {"schema": {"type": "string", "format": "binary"}}}}})
async def import_file(user: User, request: Request):
    """Recibe el .xlsx como cuerpo crudo. El runner entrega los eventos de los viajes creados."""
    content = await read_body(request, excel.MAX_BYTES, "El archivo supera 1 MB")
    state = request.app.state

    def run():
        rows = excel.leer_filas(content)
        with state.sessions() as db:
            return servicio.import_trips(db, user, rows)
    return await asyncio.to_thread(run)


@router.get("/viajes/{trip_id}")
def detail(trip_id: int, user: User, db: DB, request: Request):
    return request.app.state.consultas.trip(db, user.transportadora_id, trip_id)


@router.post("/viajes/{trip_id}/transiciones")
def change(trip_id: int, data: TransitionInput, user: User, db: DB, request: Request):
    servicio.transition(db, user, trip_id, data)
    return request.app.state.consultas.trip(db, user.transportadora_id, trip_id)


@router.get("/vehiculos", tags=["Flota"])
def vehicles(user: User, db: DB, request: Request, page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=100)):
    return request.app.state.consultas.vehicles(db, user.transportadora_id, page, page_size)


@router.get("/conductores", tags=["Flota"])
def drivers(user: User, db: DB, page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=100)):
    return servicio.list_drivers(db, user.transportadora_id, page, page_size)
