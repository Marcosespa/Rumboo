import asyncio
import hashlib
import hmac
import re
import time
from fastapi import APIRouter, Header, HTTPException, Query, Request
from pydantic import ValidationError
from app.acceso.deps import User
from app.core.db import now
from app.core.errores import Conflicto
from app.core.web import DB, read_body
from app.operacion import servicio as operacion
from app.satelital import servicio
from app.satelital.schemas import AccountInput, CallbackInput

router = APIRouter(tags=["Satrack"])
CALLBACK_MAX_AGE_S = 300


async def _call(state, function, *args):
    def execute():
        with state.sessions() as db:
            return function(db, *args)
    return await asyncio.to_thread(execute)


@router.get("/api/cuenta-satelital")
def get(user: User, db: DB):
    return servicio.account_info(db, user.transportadora_id)


@router.put("/api/cuenta-satelital")
async def update(data: AccountInput, user: User, request: Request):
    state = request.app.state
    job_id = await _call(state, servicio.save_account, user.transportadora_id, data, state.settings)
    await servicio.dispatch(state.sessions, state.settings, state.satrack, job_id)
    return await _call(state, servicio.account_info, user.transportadora_id)


async def _request(state, tenant, kind, plates=None):
    result = await _call(state, servicio.request_job, tenant, kind, plates)
    if result["status"] == "aceptado":
        await servicio.dispatch(state.sessions, state.settings, state.satrack, result["job_id"])
    return result


@router.post("/api/cuenta-satelital/sincronizar", status_code=202)
async def synchronize(user: User, request: Request):
    return await _request(request.app.state, user.transportadora_id, "vehicles")


@router.post("/api/cuenta-satelital/consultar", status_code=202)
async def query_now(user: User, request: Request):
    state = request.app.state
    plates = await _call(state, operacion.plates_to_monitor, user.transportadora_id, now())
    if not plates:
        raise Conflicto("No hay viajes en ruta o próximos a salir para consultar")
    return await _request(state, user.transportadora_id, "positions", plates)


@router.get("/api/consultas-satelitales/{job_id}")
def query_status(job_id: str, user: User, db: DB):
    return servicio.query_info(db, user.transportadora_id, job_id)


@router.get("/api/viajes/{trip_id}/posiciones", tags=["Viajes"])
def positions(trip_id: int, user: User, db: DB, limit: int = Query(1000, ge=1, le=2000)):
    return servicio.trip_positions(db, user.transportadora_id, trip_id, limit)


@router.post("/internal/satrack/callback", include_in_schema=False)
async def callback(request: Request, x_signature: str = Header(default=""), x_job_id: str = Header(default=""),
                   x_timestamp: str = Header(default="")):
    # Solo dígitos ASCII: str.isdigit acepta "²" y int() fallaría con 500.
    if not re.fullmatch(r"[0-9]{1,12}", x_timestamp) or abs(time.time() - int(x_timestamp)) > CALLBACK_MAX_AGE_S:
        raise HTTPException(401, "Firma del callback inválida")
    body = await read_body(request, 2_000_000, "Respuesta demasiado grande")
    signed = f"{x_timestamp}.".encode() + body
    expected = "sha256=" + hmac.new(request.app.state.settings.callback_secret.encode(), signed, hashlib.sha256).hexdigest()
    # Bytes: compare_digest rechaza str no ASCII con TypeError. Las cabeceras llegan decodificadas en latin-1.
    if not hmac.compare_digest(x_signature.encode("latin-1"), expected.encode()):
        raise HTTPException(401, "Firma del callback inválida")
    try:
        payload = CallbackInput.model_validate_json(body)
    except ValidationError as err:
        raise HTTPException(422, "El callback no cumple el contrato") from err
    if str(payload.job_id) != x_job_id:
        raise HTTPException(422, "El identificador del callback no coincide")
    return await _call(request.app.state, servicio.apply_result, payload)
