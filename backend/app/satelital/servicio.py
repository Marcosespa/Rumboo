import asyncio
import logging
from datetime import timedelta
from uuid import uuid4
from sqlalchemy import select
from app.acceso.servicio import query_frequency_min
from app.auditoria.servicio import registrar_evento
from app.core.db import aware, now
from app.core.errores import Conflicto, Invalido, NoEncontrado
from app.core.seguridad import cipher
from app.operacion import servicio as operacion
from app.satelital.cliente import ServicioSatelitalNoDisponible
from app.satelital.models import ConsultaSatelital, CuentaSatelital, Posicion

logger = logging.getLogger(__name__)


def account_of(db, tenant, lock=False):
    query = select(CuentaSatelital).where(CuentaSatelital.transportadora_id == tenant)
    return db.scalar(query.with_for_update() if lock else query)


def get_account(db, tenant):
    account = account_of(db, tenant)
    if not account:
        raise Conflicto("Conecta tu cuenta de Satrack primero")
    return account


def account_info(db, account):
    if not account:
        return None
    pending = db.scalar(select(ConsultaSatelital.job_id).where(ConsultaSatelital.cuenta_satelital_id == account.id, ConsultaSatelital.estado == "pendiente"))
    return {"id": account.id, "usuario": account.usuario, "proveedor": account.proveedor, "estado": account.estado,
            "fallos_consecutivos": account.fallos_consecutivos, "ultima_consulta_ok": account.ultima_consulta_ok,
            "ultimo_error": account.ultimo_error, "backoff_hasta": account.backoff_hasta, "consulta_pendiente": bool(pending)}


def save_account(db, tenant, data, settings):
    account = account_of(db, tenant, lock=True)
    if not account:
        account = CuentaSatelital(transportadora_id=tenant, usuario=data.usuario.strip(), password_cifrado="")
        db.add(account)
    else:
        account.version += 1
        for pending in db.scalars(select(ConsultaSatelital).where(ConsultaSatelital.cuenta_satelital_id == account.id, ConsultaSatelital.estado == "pendiente").with_for_update()):
            pending.estado = "cancelado"
            pending.error_codigo = "STALE_ACCOUNT"
    account.usuario = data.usuario.strip()
    account.password_cifrado = cipher(settings).encrypt(data.password.get_secret_value().encode()).decode()
    account.estado, account.fallos_consecutivos, account.ultimo_error, account.backoff_hasta = "sin_verificar", 0, None, None
    operacion.reset_satellite_verification(db, tenant)
    db.commit()
    return account


def reencrypt_accounts(db, settings):
    """Recifra las credenciales con la clave vigente; tras ejecutarlo se pueden retirar las claves antiguas."""
    fernet = cipher(settings)
    accounts = db.scalars(select(CuentaSatelital).with_for_update()).all()
    for account in accounts:
        account.password_cifrado = fernet.rotate(account.password_cifrado.encode()).decode()
    db.commit()
    return len(accounts)


def reserve_job(db, account, settings, kind="vehicles", plates=None):
    account = db.scalar(select(CuentaSatelital).where(CuentaSatelital.id == account.id).with_for_update())
    pending = db.scalar(select(ConsultaSatelital).where(ConsultaSatelital.cuenta_satelital_id == account.id, ConsultaSatelital.estado == "pendiente"))
    if pending:
        return None
    job_id = str(uuid4())
    query = ConsultaSatelital(job_id=job_id, transportadora_id=account.transportadora_id, cuenta_satelital_id=account.id,
                             cuenta_version=account.version, tipo=kind, placas=plates or [])
    db.add(query)
    job = {"job_id": job_id, "type": kind, "plates": plates or [], "account": {"id": str(account.id),
           "username": account.usuario, "password": cipher(settings).decrypt(account.password_cifrado.encode()).decode()}}
    db.commit()
    return job


async def dispatch(sessions, client, job):
    if not job:
        return
    try:
        await client.send_job(job)
    except ServicioSatelitalNoDisponible:
        with sessions() as db:
            query = db.scalar(select(ConsultaSatelital).where(ConsultaSatelital.job_id == job["job_id"]).with_for_update())
            if query and query.estado == "pendiente" and query.respondido_en is None:
                query.estado = "fallido"
                query.error_codigo = "SERVICE_UNAVAILABLE"
                query.error_detalle = "El servicio satelital no está disponible; se reintentará"
                account = db.get(CuentaSatelital, query.cuenta_satelital_id)
                if account.version == query.cuenta_version:
                    account.fallos_consecutivos += 1
                    account.ultimo_error = query.error_detalle
                    if account.fallos_consecutivos >= 3:
                        account.estado = "falla"
                db.commit()
        logger.warning("Servicio satelital no disponible job=%s", job["job_id"])


def plan_queries(sessions, settings):
    """Marca timeouts y reserva la siguiente consulta de cada cuenta según su frecuencia."""
    jobs = []
    at = now()
    with sessions() as db:
        expired = db.scalars(select(ConsultaSatelital).where(ConsultaSatelital.estado == "pendiente", ConsultaSatelital.enviado_en < at - timedelta(seconds=settings.consulta_timeout_s)).with_for_update()).all()
        for query in expired:
            query.estado = "timeout"
            query.error_codigo = "TIMEOUT"
            query.error_detalle = "El servicio satelital no entregó la respuesta a tiempo"
            account = db.get(CuentaSatelital, query.cuenta_satelital_id)
            if account.version == query.cuenta_version:
                account.fallos_consecutivos += 1
                account.ultimo_error = query.error_detalle
                if account.fallos_consecutivos >= 3:
                    account.estado = "falla"
        db.commit()
        account_ids = list(db.scalars(select(CuentaSatelital.id).where(CuentaSatelital.estado != "credenciales_invalidas")))
        for account_id in account_ids:
            account = db.get(CuentaSatelital, account_id)
            if account.backoff_hasta and aware(account.backoff_hasta) > at:
                continue
            if db.scalar(select(ConsultaSatelital.job_id).where(ConsultaSatelital.cuenta_satelital_id == account.id, ConsultaSatelital.estado == "pendiente")):
                continue
            last = db.scalar(select(ConsultaSatelital).where(ConsultaSatelital.cuenta_satelital_id == account.id).order_by(ConsultaSatelital.enviado_en.desc()).limit(1))
            if last and aware(last.enviado_en) > at - timedelta(minutes=query_frequency_min(db, account.transportadora_id)):
                continue
            plates = operacion.plates_to_monitor(db, account.transportadora_id, at)
            if operacion.has_unverified_trips(db, account.transportadora_id) or account.estado == "sin_verificar":
                job = reserve_job(db, account, settings)
            elif plates:
                job = reserve_job(db, account, settings, "positions", plates)
            else:
                continue
            if job:
                jobs.append(job)
    return jobs


async def scheduled_queries(sessions, settings, client):
    """Tarea periódica: el runner de core.tareas la ejecuta cada SCHEDULER_INTERVAL_S."""
    for job in await asyncio.to_thread(plan_queries, sessions, settings):
        await dispatch(sessions, client, job)


def apply_result(db, payload):
    """Aplica el resultado de un job de forma idempotente. Hoy llega por callback; en M1 también por GET."""
    query = db.scalar(select(ConsultaSatelital).where(ConsultaSatelital.job_id == str(payload.job_id)).with_for_update())
    if not query:
        raise NoEncontrado("Consulta no encontrada")
    if query.tipo != payload.type:
        raise Invalido("El tipo de respuesta no coincide con la consulta")
    if query.respondido_en is not None:
        return {"status": "ok", "duplicado": True}
    account = db.scalar(select(CuentaSatelital).where(CuentaSatelital.id == query.cuenta_satelital_id).with_for_update())
    query.respondido_en = now()
    query.estado = {"ok": "ok", "partial": "parcial", "failed": "fallido"}[payload.status]
    if account.version != query.cuenta_version:
        query.error_codigo = "STALE_ACCOUNT"
        query.error_detalle = "Respuesta de una configuración anterior; no aplicada"
        db.commit()
        return {"status": "ok", "obsoleto": True}
    latest_completed = db.scalar(select(ConsultaSatelital.enviado_en).where(
        ConsultaSatelital.cuenta_satelital_id == account.id,
        ConsultaSatelital.respondido_en.is_not(None), ConsultaSatelital.job_id != query.job_id,
        ConsultaSatelital.cuenta_version == account.version).order_by(ConsultaSatelital.enviado_en.desc()).limit(1))
    stale = latest_completed is not None and aware(latest_completed) > aware(query.enviado_en)
    tenant = account.transportadora_id
    if payload.status != "failed":
        if payload.type == "vehicles" and not stale:
            plates = {v.plate for v in payload.vehicles}
            for vehicle in operacion.vehicles_of(db, tenant):
                operacion.set_in_satellite(vehicle, vehicle.placa in plates)
                if vehicle.en_satelital:
                    operacion.schedule_verified_trips(db, tenant, vehicle)
        if payload.type == "positions":
            for row in payload.positions:
                if row.plate not in query.placas:
                    continue
                vehicle = operacion.vehicle_by_plate(db, tenant, row.plate, lock=True)
                if not vehicle:
                    continue
                timestamp = aware(row.reported_at)
                position = db.scalar(select(Posicion).where(Posicion.vehiculo_id == vehicle.id, Posicion.reportado_en == timestamp)) if timestamp else None
                if position is None:
                    trip = operacion.active_trip(db, vehicle.id)
                    # Do not attach delayed coordinates from an earlier trip to the current trip.
                    trip_id = trip.id if trip and (timestamp is None or timestamp >= aware(trip.salida_estimada) - timedelta(hours=1)) else None
                    position = Posicion(transportadora_id=tenant, vehiculo_id=vehicle.id, viaje_id=trip_id, consulta_id=query.job_id,
                        lat=row.lat, lng=row.lng, velocidad_kmh=row.speed_kmh, direccion=row.address, estado_gps=row.status,
                        reportado_en=timestamp, reportado_texto=row.reported_at_raw, capturado_en=payload.finished_at)
                    db.add(position)
                    db.flush()
                previous = db.get(Posicion, vehicle.ultima_posicion_id) if vehicle.ultima_posicion_id else None
                if previous is None or aware(position.reportado_en or position.capturado_en) >= aware(previous.reportado_en or previous.capturado_en):
                    if not stale:
                        operacion.set_last_position(vehicle, position.id)
                        operacion.set_in_satellite(vehicle, True)
    if not stale:
        if payload.status in ("ok", "partial"):
            account.estado = "ok"
            account.fallos_consecutivos = 0
            account.ultima_consulta_ok = now()
            account.backoff_hasta = None
            account.ultimo_error = "; ".join(e.message for e in payload.errors) or None
        else:
            error = payload.errors[0] if payload.errors else None
            code = error.code if error else "PROVIDER_UNAVAILABLE"
            query.error_codigo = code
            query.error_detalle = error.message if error else "No fue posible consultar Satrack"
            account.ultimo_error = query.error_detalle
            account.fallos_consecutivos += 1
            if code == "AUTH_FAILED":
                account.estado = "credenciales_invalidas"
            elif code in ("CAPTCHA_REQUIRED", "PROVIDER_CHANGED"):
                account.backoff_hasta = now() + timedelta(minutes=15)
                account.estado = "falla"
            elif account.fallos_consecutivos >= 3:
                account.estado = "falla"
        for error in payload.errors:
            if error.code == "VEHICLE_NOT_FOUND" and error.plate:
                vehicle = operacion.vehicle_by_plate(db, tenant, error.plate)
                if vehicle:
                    operacion.set_in_satellite(vehicle, False)
                    trip = operacion.active_trip(db, vehicle.id)
                    registrar_evento(db, tenant, trip.id if trip else None, "placa_no_encontrada", {"placa": vehicle.placa})
    registrar_evento(db, tenant, None, "consulta_satelital", {"job_id": query.job_id, "estado": query.estado})
    db.commit()
    return {"status": "ok"}


def serialize_position(p):
    if p is None:
        return None
    return {key: getattr(p, key) for key in ("id", "lat", "lng", "velocidad_kmh", "direccion", "estado_gps", "reportado_en", "reportado_texto", "capturado_en", "viaje_id")}


def trip_positions(db, tenant, trip_id, limit):
    operacion.get_trip(db, tenant, trip_id)
    rows = list(db.scalars(select(Posicion).where(Posicion.viaje_id == trip_id, Posicion.transportadora_id == tenant).order_by(Posicion.capturado_en.desc(), Posicion.id.desc()).limit(limit)))
    return [serialize_position(p) for p in reversed(rows)]


def last_position(db, vehicle):
    """Extensión de operacion: agrega la última ubicación al vehículo serializado."""
    return {"ultima_posicion": serialize_position(db.get(Posicion, vehicle.ultima_posicion_id)) if vehicle.ultima_posicion_id else None}


async def verify_plate_for_new_trip(sessions, settings, client, *, transportadora_id, viaje_id, vehiculo_id):
    """Reacción a `viaje_registrado`: programa el viaje si la placa ya está confirmada; si no, pide verificarla."""
    with sessions() as db:
        account = account_of(db, transportadora_id)
        if not account or account.estado == "credenciales_invalidas":
            return
        vehicle = operacion.get_vehicle(db, transportadora_id, vehiculo_id)
        if account.estado == "ok" and vehicle and vehicle.en_satelital:
            operacion.schedule_verified_trips(db, transportadora_id, vehicle)
            db.commit()
            return
        job = reserve_job(db, account, settings)
    await dispatch(sessions, client, job)
