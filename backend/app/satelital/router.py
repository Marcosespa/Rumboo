from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select
from app.db import now
from app.deps import DB, User
from app.models import ConsultaSatelital, CuentaSatelital, Vehiculo
from app.schemas import AccountInput
from app.security import cipher
from app.services.monitoreo import active_plates, reserve_job
from app.services.satrack_client import dispatch

router = APIRouter(prefix="/api/cuenta-satelital", tags=["Satrack"])


def account_info(db, account):
    if not account:
        return None
    pending = db.scalar(select(ConsultaSatelital.job_id).where(ConsultaSatelital.cuenta_satelital_id == account.id, ConsultaSatelital.estado == "pendiente"))
    return {"id": account.id, "usuario": account.usuario, "proveedor": account.proveedor, "estado": account.estado,
            "fallos_consecutivos": account.fallos_consecutivos, "ultima_consulta_ok": account.ultima_consulta_ok,
            "ultimo_error": account.ultimo_error, "backoff_hasta": account.backoff_hasta, "consulta_pendiente": bool(pending)}


def get_account(db, tenant):
    account = db.scalar(select(CuentaSatelital).where(CuentaSatelital.transportadora_id == tenant))
    if not account:
        raise HTTPException(409, "Conecta tu cuenta de Satrack primero")
    return account


@router.get("")
def get(user: User, db: DB):
    return account_info(db, db.scalar(select(CuentaSatelital).where(CuentaSatelital.transportadora_id == user.transportadora_id)))


@router.put("")
async def update(data: AccountInput, user: User, db: DB, request: Request):
    account = db.scalar(select(CuentaSatelital).where(CuentaSatelital.transportadora_id == user.transportadora_id).with_for_update())
    if not account:
        account = CuentaSatelital(transportadora_id=user.transportadora_id, usuario=data.usuario.strip(), password_cifrado="")
        db.add(account)
    else:
        account.version += 1
        for pending in db.scalars(select(ConsultaSatelital).where(ConsultaSatelital.cuenta_satelital_id == account.id, ConsultaSatelital.estado == "pendiente").with_for_update()):
            pending.estado = "cancelado"
            pending.error_codigo = "STALE_ACCOUNT"
    account.usuario = data.usuario.strip()
    account.password_cifrado = cipher(request.app.state.settings).encrypt(data.password.get_secret_value().encode()).decode()
    account.estado, account.fallos_consecutivos, account.ultimo_error, account.backoff_hasta = "sin_verificar", 0, None, None
    for vehicle in db.scalars(select(Vehiculo).where(Vehiculo.transportadora_id == user.transportadora_id)):
        vehicle.en_satelital = None
    db.commit()
    job = reserve_job(db, account, request.app.state.settings)
    await dispatch(request.app, job)
    db.refresh(account)
    return account_info(db, account)


@router.post("/sincronizar", status_code=202)
async def synchronize(user: User, db: DB, request: Request):
    account = get_account(db, user.transportadora_id)
    job = reserve_job(db, account, request.app.state.settings)
    await dispatch(request.app, job)
    return {"status": "aceptado" if job else "pendiente", "job_id": job["job_id"] if job else None}


@router.post("/consultar", status_code=202)
async def query_now(user: User, db: DB, request: Request):
    account = get_account(db, user.transportadora_id)
    plates = active_plates(db, user.transportadora_id, now())
    if not plates:
        raise HTTPException(409, "No hay viajes en ruta o próximos a salir para consultar")
    job = reserve_job(db, account, request.app.state.settings, "positions", plates)
    await dispatch(request.app, job)
    return {"status": "aceptado" if job else "pendiente", "job_id": job["job_id"] if job else None}
