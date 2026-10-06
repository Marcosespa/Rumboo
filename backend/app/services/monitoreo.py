from datetime import timedelta
from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.db import now, aware
from app.models import ACTIVE_STATES, ConsultaSatelital, CuentaSatelital, Posicion, Transportadora, Vehiculo, Viaje
from app.security import cipher
from app.services.viajes import event


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


def active_plates(db, tenant, at):
    return list(db.scalars(select(Vehiculo.placa).join(Viaje, Viaje.vehiculo_id == Vehiculo.id).where(
        Viaje.transportadora_id == tenant,
        (Viaje.estado.in_(("en_ruta", "con_novedad"))) | ((Viaje.estado == "programado") & (Viaje.salida_estimada <= at + timedelta(hours=1)))
    )).unique())


def tick(sessions, settings):
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
            carrier = db.get(Transportadora, account.transportadora_id)
            if last and aware(last.enviado_en) > at - timedelta(minutes=carrier.frecuencia_consulta_min):
                continue
            unverified = db.scalar(select(Viaje.id).where(Viaje.transportadora_id == account.transportadora_id, Viaje.estado == "registrado").limit(1))
            plates = active_plates(db, account.transportadora_id, at)
            if unverified or account.estado == "sin_verificar":
                job = reserve_job(db, account, settings)
            elif plates:
                job = reserve_job(db, account, settings, "positions", plates)
            else:
                continue
            if job:
                jobs.append(job)
    return jobs


def process_callback(db, payload):
    query = db.scalar(select(ConsultaSatelital).where(ConsultaSatelital.job_id == str(payload.job_id)).with_for_update())
    if not query:
        raise HTTPException(404, "Consulta no encontrada")
    if query.tipo != payload.type:
        raise HTTPException(422, "El tipo de respuesta no coincide con la consulta")
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
            for vehicle in db.scalars(select(Vehiculo).where(Vehiculo.transportadora_id == tenant)):
                vehicle.en_satelital = vehicle.placa in plates
                if vehicle.en_satelital:
                    for trip in db.scalars(select(Viaje).where(Viaje.vehiculo_id == vehicle.id, Viaje.estado == "registrado").with_for_update()):
                        trip.estado = "programado"
                        event(db, tenant, trip.id, "placa_verificada", {"estado": "programado", "placa": vehicle.placa})
        if payload.type == "positions":
            for row in payload.positions:
                if row.plate not in query.placas:
                    continue
                vehicle = db.scalar(select(Vehiculo).where(Vehiculo.transportadora_id == tenant, Vehiculo.placa == row.plate).with_for_update())
                if not vehicle:
                    continue
                timestamp = aware(row.reported_at)
                position = db.scalar(select(Posicion).where(Posicion.vehiculo_id == vehicle.id, Posicion.reportado_en == timestamp)) if timestamp else None
                if position is None:
                    trip = db.scalar(select(Viaje).where(Viaje.vehiculo_id == vehicle.id, Viaje.estado.in_(ACTIVE_STATES)))
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
                        vehicle.ultima_posicion_id = position.id
                        vehicle.en_satelital = True
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
                vehicle = db.scalar(select(Vehiculo).where(Vehiculo.transportadora_id == tenant, Vehiculo.placa == error.plate))
                if vehicle:
                    vehicle.en_satelital = False
                    trip = db.scalar(select(Viaje).where(Viaje.vehiculo_id == vehicle.id, Viaje.estado.in_(ACTIVE_STATES)))
                    event(db, tenant, trip.id if trip else None, "placa_no_encontrada", {"placa": vehicle.placa})
    event(db, tenant, None, "consulta_satelital", {"job_id": query.job_id, "estado": query.estado})
    db.commit()
    return {"status": "ok"}
