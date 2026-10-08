import hashlib
import hmac
from fastapi import APIRouter, Header, HTTPException, Query, Request
from pydantic import ValidationError
from app.acceso.deps import User
from app.core.db import now
from app.core.web import DB
from app.operacion import servicio as operacion
from app.satelital import servicio
from app.satelital.schemas import AccountInput, CallbackInput

router = APIRouter(tags=["Satrack"])


@router.get("/api/cuenta-satelital")
def get(user: User, db: DB):
    return servicio.account_info(db, servicio.account_of(db, user.transportadora_id))


@router.put("/api/cuenta-satelital")
async def update(data: AccountInput, user: User, db: DB, request: Request):
    state = request.app.state
    account = servicio.save_account(db, user.transportadora_id, data, state.settings)
    job = servicio.reserve_job(db, account, state.settings)
    await servicio.dispatch(state.sessions, state.satrack, job)
    db.refresh(account)
    return servicio.account_info(db, account)


@router.post("/api/cuenta-satelital/sincronizar", status_code=202)
async def synchronize(user: User, db: DB, request: Request):
    state = request.app.state
    account = servicio.get_account(db, user.transportadora_id)
    job = servicio.reserve_job(db, account, state.settings)
    await servicio.dispatch(state.sessions, state.satrack, job)
    return {"status": "aceptado" if job else "pendiente", "job_id": job["job_id"] if job else None}


@router.post("/api/cuenta-satelital/consultar", status_code=202)
async def query_now(user: User, db: DB, request: Request):
    state = request.app.state
    account = servicio.get_account(db, user.transportadora_id)
    plates = operacion.plates_to_monitor(db, user.transportadora_id, now())
    if not plates:
        raise HTTPException(409, "No hay viajes en ruta o próximos a salir para consultar")
    job = servicio.reserve_job(db, account, state.settings, "positions", plates)
    await servicio.dispatch(state.sessions, state.satrack, job)
    return {"status": "aceptado" if job else "pendiente", "job_id": job["job_id"] if job else None}


@router.get("/api/viajes/{trip_id}/posiciones", tags=["Viajes"])
def positions(trip_id: int, user: User, db: DB, limit: int = Query(1000, ge=1, le=2000)):
    return servicio.trip_positions(db, user.transportadora_id, trip_id, limit)


@router.post("/internal/satrack/callback", include_in_schema=False)
async def callback(request: Request, db: DB, x_signature: str = Header(default=""), x_job_id: str = Header(default="")):
    body = await request.body()
    if len(body) > 2_000_000:
        raise HTTPException(413, "Respuesta demasiado grande")
    expected = "sha256=" + hmac.new(request.app.state.settings.callback_secret.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(x_signature, expected):
        raise HTTPException(401, "Firma del callback inválida")
    try:
        payload = CallbackInput.model_validate_json(body)
    except ValidationError:
        raise HTTPException(422, "El callback no cumple el contrato")
    if str(payload.job_id) != x_job_id:
        raise HTTPException(422, "El identificador del callback no coincide")
    return servicio.apply_result(db, payload)
