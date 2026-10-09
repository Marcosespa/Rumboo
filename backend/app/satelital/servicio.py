"""Casos de uso satelitales. Tablas privadas, DTO públicos y HTTP fuera de transacciones."""
import asyncio
from datetime import timedelta
from uuid import uuid4
from cryptography.fernet import InvalidToken
from sqlalchemy import func, select
from app.acceso.servicio import lock_carrier, query_frequency_min
from app.auditoria.servicio import registrar_evento
from app.core.db import aware, now
from app.core.errores import Conflicto, ErrorDominio, Invalido, NoEncontrado
from app.core.seguridad import cipher
from app.operacion import servicio as operacion
from app.operacion.validadores import normalize_plate
from app.satelital.cliente import ServicioSatelitalNoDisponible
from app.satelital.models import ConsultaSatelital, CuentaSatelital, Posicion, VehiculoSatelital
from app.satelital.schemas import AccountDTO, ConsultaDTO, EstadoVehiculoDTO, PosicionDTO


def _account(db, tenant, lock=False):
    stmt = select(CuentaSatelital).where(CuentaSatelital.transportadora_id == tenant)
    return db.scalar(stmt.with_for_update() if lock else stmt)


def _require_account(db, tenant):
    account = _account(db, tenant, lock=True)
    if account is None:
        raise Conflicto("Conecta tu cuenta de Satrack primero")
    return account


def account_info(db, tenant):
    account = _account(db, tenant)
    if account is None:
        return None
    pending = db.scalar(select(ConsultaSatelital.job_id).where(
        ConsultaSatelital.cuenta_satelital_id == account.id, ConsultaSatelital.estado == "pendiente"))
    return AccountDTO(**{k: getattr(account, k) for k in (
        "id", "transportadora_id", "usuario", "proveedor", "estado", "fallos_consecutivos",
        "ultima_consulta_ok", "ultimo_error", "backoff_hasta")}, consulta_pendiente=pending is not None)


def _reserve(db, account, kind="vehicles", plates=None):
    pending = db.scalar(select(ConsultaSatelital).where(
        ConsultaSatelital.cuenta_satelital_id == account.id, ConsultaSatelital.estado == "pendiente"))
    if pending is not None:
        return pending, False
    snapshot_plates = plates or [v.placa for v in operacion.vehicles_of(db, account.transportadora_id)]
    query = ConsultaSatelital(job_id=str(uuid4()), transportadora_id=account.transportadora_id,
        cuenta_satelital_id=account.id, cuenta_version=account.version, tipo=kind, placas=plates or [],
        viajes_solicitados=operacion.journey_snapshot(db, account.transportadora_id, snapshot_plates))
    db.add(query)
    db.flush()
    return query, True


def save_account(db, tenant, data, settings):
    lock_carrier(db, tenant)
    account = _account(db, tenant, lock=True)
    if account is None:
        account = CuentaSatelital(transportadora_id=tenant, usuario=data.usuario.strip(), password_cifrado="")
        db.add(account)
        db.flush()
    else:
        account.version += 1
        for pending in db.scalars(select(ConsultaSatelital).where(
                ConsultaSatelital.cuenta_satelital_id == account.id, ConsultaSatelital.estado == "pendiente").with_for_update()):
            pending.estado, pending.error_codigo = "cancelado", "STALE_ACCOUNT"
    account.usuario = data.usuario.strip()
    account.password_cifrado = cipher(settings).encrypt(data.password.get_secret_value().encode()).decode()
    account.estado, account.fallos_consecutivos, account.ultimo_error, account.backoff_hasta = "sin_verificar", 0, None, None
    for row in db.scalars(select(VehiculoSatelital).where(VehiculoSatelital.transportadora_id == tenant)):
        row.en_satelital = None
        row.cuenta_version = account.version
    query, _ = _reserve(db, account)
    job_id = query.job_id
    db.commit()
    return job_id


def reencrypt_accounts(db, settings):
    """Recifra con la clave vigente preservando la marca de tiempo del cifrado."""
    encryption = cipher(settings)
    accounts = list(db.scalars(select(CuentaSatelital).with_for_update()))
    for account in accounts:
        account.password_cifrado = encryption.rotate(account.password_cifrado.encode()).decode()
    db.commit()
    return len(accounts)


def request_job(db, tenant, kind="vehicles", plates=None):
    lock_carrier(db, tenant)
    account = _require_account(db, tenant)
    if account.estado == "credenciales_invalidas":
        raise Conflicto("Actualiza las credenciales de Satrack antes de consultar")
    query, created = _reserve(db, account, kind, plates)
    result = {"status": "aceptado" if created else "pendiente", "job_id": query.job_id, "tipo": query.tipo}
    db.commit()
    return result


def query_info(db, tenant, job_id):
    row = db.scalar(select(ConsultaSatelital).where(ConsultaSatelital.job_id == job_id,
                                                  ConsultaSatelital.transportadora_id == tenant))
    if row is None:
        raise NoEncontrado("Consulta no encontrada")
    return ConsultaDTO.model_validate(row)


def _locked_query(db, job_id):
    identity = db.execute(select(ConsultaSatelital.transportadora_id, ConsultaSatelital.cuenta_satelital_id)
                          .where(ConsultaSatelital.job_id == job_id)).first()
    if identity is None:
        raise NoEncontrado("Consulta no encontrada")
    # Orden único para las reservas, cambios de credenciales, timeouts y respuestas.
    lock_carrier(db, identity.transportadora_id)
    account = db.scalar(select(CuentaSatelital).where(CuentaSatelital.id == identity.cuenta_satelital_id).with_for_update())
    query = db.scalar(select(ConsultaSatelital).where(ConsultaSatelital.job_id == job_id).with_for_update())
    return query, account


def _prepare_send(sessions, settings, job_id):
    with sessions() as db:
        query, account = _locked_query(db, job_id)
        if query.estado != "pendiente" or account.version != query.cuenta_version:
            return None
        if query.intentos >= 3 or aware(query.proximo_envio) > now():
            return None
        try:
            password = cipher(settings).decrypt(account.password_cifrado.encode()).decode()
        except InvalidToken:
            # Clave retirada sin `cli recifrar`: se marca esta cuenta y el lote sigue con las demás.
            query.estado = "fallido"
            _failure(query, account, "CREDENTIALS_UNREADABLE", "No se pudieron leer las credenciales; vuelve a conectar la cuenta")
            account.estado = "credenciales_invalidas"
            db.commit()
            return None
        if query.intentos == 0:
            # El plazo de timeout corre desde el primer POST, no desde la reserva.
            query.enviado_en = now()
        query.intentos += 1
        query.proximo_envio = now() + timedelta(seconds=(2, 10, 30)[query.intentos - 1])
        job = {"job_id": query.job_id, "type": query.tipo, "plates": query.placas,
               "account": {"id": str(account.id), "username": account.usuario, "password": password}}
        db.commit()
        return job


def _sending_error(sessions, job_id):
    with sessions() as db:
        query, _ = _locked_query(db, job_id)
        if query.estado == "pendiente":
            query.error_codigo = "SERVICE_UNAVAILABLE"
            query.error_detalle = "Envío incierto; se consultará el estado antes de reintentar"
            db.commit()


async def dispatch(sessions, settings, client, job_id):
    if not job_id:
        return
    job = await asyncio.to_thread(_prepare_send, sessions, settings, job_id)
    if job is None:
        return
    try:
        await client.send_job(job)
    except ServicioSatelitalNoDisponible:
        await asyncio.to_thread(_sending_error, sessions, job_id)


def _failure(query, account, code, detail):
    query.error_codigo, query.error_detalle = code, detail
    if account.version != query.cuenta_version:
        return
    if not query.fallo_contado:
        account.fallos_consecutivos += 1
        query.fallo_contado = True
    account.ultimo_error = detail
    if code == "AUTH_FAILED":
        account.estado = "credenciales_invalidas"
    elif code in ("CAPTCHA_REQUIRED", "PROVIDER_CHANGED"):
        account.backoff_hasta = now() + timedelta(minutes=15)
        account.estado = "falla"
    elif account.fallos_consecutivos >= 3:
        account.estado = "falla"


def _expire(sessions, settings, job_id):
    with sessions() as db:
        query, account = _locked_query(db, job_id)
        if query.estado == "pendiente" and aware(query.enviado_en) + timedelta(seconds=settings.consulta_timeout_s) <= now():
            query.estado = "timeout"
            _failure(query, account, "TIMEOUT", "El servicio satelital no entregó la respuesta a tiempo")
            db.commit()
            return True
        return query.estado != "pendiente"


def _pending_ids(sessions, tenant=None, unsent=False):
    with sessions() as db:
        stmt = select(ConsultaSatelital.job_id).where(ConsultaSatelital.estado == "pendiente")
        if tenant is not None:
            stmt = stmt.where(ConsultaSatelital.transportadora_id == tenant)
        if unsent:
            stmt = stmt.where(ConsultaSatelital.intentos == 0)
        return list(db.scalars(stmt.order_by(ConsultaSatelital.enviado_en).limit(100)))


async def dispatch_reserved(sessions, settings, client, tenant=None):
    for job_id in await asyncio.to_thread(_pending_ids, sessions, tenant, True):
        await dispatch(sessions, settings, client, job_id)


def _apply_polled_result(sessions, payload):
    try:
        with sessions() as db:
            return apply_result(db, payload)
    except ErrorDominio:
        # Una respuesta incompatible no debe bloquear las otras cuentas del lote.
        with sessions() as db:
            query, account = _locked_query(db, str(payload.job_id))
            if query.estado == "pendiente":
                query.estado = "fallido"
                _failure(query, account, "INVALID_RESULT", "El resultado no coincide con la consulta")
                db.commit()


async def reconcile_queries(sessions, settings, client):
    """Único lugar que vence consultas: primero pregunta al scraper, así un resultado listo se aplica aunque la API
    haya estado detenida más que el timeout."""
    for job_id in await asyncio.to_thread(_pending_ids, sessions):
        try:
            state = await client.get_job(job_id)
        except ServicioSatelitalNoDisponible:
            await asyncio.to_thread(_expire, sessions, settings, job_id)
            continue
        if state is not None and state.status == "done" and state.result is not None:
            await asyncio.to_thread(_apply_polled_result, sessions, state.result)
        elif not await asyncio.to_thread(_expire, sessions, settings, job_id) and state is None:
            await dispatch(sessions, settings, client, job_id)


def plan_queries(sessions, settings):
    at = now()
    jobs = []
    with sessions() as db:
        account_ids = list(db.scalars(select(CuentaSatelital.id).where(CuentaSatelital.estado != "credenciales_invalidas")))
    for account_id in account_ids:
        with sessions() as db:
            tenant = db.scalar(select(CuentaSatelital.transportadora_id).where(CuentaSatelital.id == account_id))
            lock_carrier(db, tenant)
            account = _require_account(db, tenant)
            if account.estado == "credenciales_invalidas" or (account.backoff_hasta and aware(account.backoff_hasta) > at):
                continue
            if db.scalar(select(ConsultaSatelital.job_id).where(
                    ConsultaSatelital.cuenta_satelital_id == account.id, ConsultaSatelital.estado == "pendiente")):
                continue
            last = db.scalar(select(ConsultaSatelital.enviado_en).where(ConsultaSatelital.cuenta_satelital_id == account.id)
                             .order_by(ConsultaSatelital.enviado_en.desc()).limit(1))
            if last and aware(last) > at - timedelta(minutes=query_frequency_min(db, tenant)):
                continue
            plates = operacion.plates_to_monitor(db, tenant, at)
            if operacion.has_unverified_trips(db, tenant) or account.estado == "sin_verificar":
                query, _ = _reserve(db, account)
            elif plates:
                query, _ = _reserve(db, account, "positions", plates)
            else:
                continue
            jobs.append(query.job_id)
            db.commit()
    return jobs


async def scheduled_queries(sessions, settings, client):
    for job_id in await asyncio.to_thread(plan_queries, sessions, settings):
        await dispatch(sessions, settings, client, job_id)
    await dispatch_reserved(sessions, settings, client)


def _plate(value):
    try:
        return normalize_plate(value)
    except ValueError:
        return None


def _satellite_vehicle(db, account, vehicle_id):
    row = db.get(VehiculoSatelital, vehicle_id)
    if row is None:
        row = VehiculoSatelital(vehiculo_id=vehicle_id, transportadora_id=account.transportadora_id,
                               cuenta_satelital_id=account.id, cuenta_version=account.version)
        db.add(row)
        db.flush()
    return row


def _save_position(db, query, payload, row, vehicle, satellite, stale, departures):
    if not any((row.lat is not None, row.lng is not None, row.speed_kmh is not None,
                row.address, row.reported_at, row.reported_at_raw, row.status not in ("", "desconocido"))):
        return
    timestamp = aware(row.reported_at)
    position = db.scalar(select(Posicion).where(Posicion.vehiculo_id == vehicle.id,
                         Posicion.reportado_en == timestamp)) if timestamp else None
    if position is None:
        trip_id = query.viajes_solicitados.get(vehicle.placa)
        if trip_id:
            departure = departures.get(trip_id)
            if departure is None or (timestamp and timestamp < aware(departure) - timedelta(hours=1)):
                trip_id = None
        lat, lng = (None, None) if row.lat == 0 and row.lng == 0 else (row.lat, row.lng)
        position = Posicion(transportadora_id=query.transportadora_id, vehiculo_id=vehicle.id,
            viaje_id=trip_id, consulta_id=query.job_id, lat=lat, lng=lng, velocidad_kmh=row.speed_kmh,
            direccion=row.address, estado_gps=row.status, reportado_en=timestamp,
            reportado_texto=row.reported_at_raw, capturado_en=payload.finished_at)
        db.add(position)
        db.flush()
    previous = db.get(Posicion, satellite.ultima_posicion_id) if satellite.ultima_posicion_id else None
    if not stale and (previous is None or aware(position.reportado_en or position.capturado_en) >=
                     aware(previous.reportado_en or previous.capturado_en)):
        satellite.ultima_posicion_id = position.id


def apply_result(db, payload):
    query, account = _locked_query(db, str(payload.job_id))
    if query.tipo != payload.type:
        raise Invalido("El tipo de respuesta no coincide con la consulta")
    if query.respondido_en is not None:
        return {"status": "ok", "duplicado": True}
    # Vencida o cancelada: el resultado se guarda y aporta historial, sin cambiar estados ya decididos.
    late = query.estado != "pendiente"
    query.resultado = payload.model_dump(mode="json")
    query.respondido_en = now()
    if not late:
        query.estado = {"ok": "ok", "partial": "parcial", "failed": "fallido"}[payload.status]
    if account.version != query.cuenta_version:
        query.error_codigo = "STALE_ACCOUNT"
        query.error_detalle = "Respuesta de una configuración anterior; no aplicada"
        db.commit()
        return {"status": "ok", "obsoleto": True}
    latest = db.scalar(select(ConsultaSatelital.enviado_en).where(
        ConsultaSatelital.cuenta_satelital_id == account.id, ConsultaSatelital.respondido_en.is_not(None),
        ConsultaSatelital.job_id != query.job_id, ConsultaSatelital.cuenta_version == account.version)
        .order_by(ConsultaSatelital.enviado_en.desc()).limit(1))
    stale = late or (latest is not None and aware(latest) > aware(query.enviado_en))
    tenant = account.transportadora_id
    departures = operacion.trip_departures(db, tenant, query.viajes_solicitados.values())
    if payload.status != "failed":
        rows = payload.vehicles if payload.type == "vehicles" else payload.positions
        found = set()
        for row in rows:
            plate = _plate(row.plate)
            if not plate or (payload.type == "positions" and plate not in query.placas):
                continue
            if plate in found:
                continue
            found.add(plate)
            vehicle = operacion.vehicle_by_plate(db, tenant, plate)
            if vehicle is None and payload.type == "vehicles" and not stale:
                vehicle = operacion.import_vehicle(db, tenant, plate)
            if vehicle is None:
                continue
            satellite = _satellite_vehicle(db, account, vehicle.id)
            if not stale:
                satellite.en_satelital = True
                satellite.cuenta_version = account.version
                if payload.type == "vehicles":
                    satellite.alias, satellite.device_id = row.name, row.device_id
                operacion.schedule_verified_trips(db, tenant, vehicle.id)
            _save_position(db, query, payload, row, vehicle, satellite, stale, departures)
        if payload.type == "vehicles" and payload.status == "ok" and not stale:
            for vehicle in operacion.vehicles_of(db, tenant):
                if vehicle.placa not in found:
                    _satellite_vehicle(db, account, vehicle.id).en_satelital = False
    if not stale:
        if payload.status in ("ok", "partial"):
            account.estado, account.fallos_consecutivos = "ok", 0
            account.ultima_consulta_ok, account.backoff_hasta = now(), None
            account.ultimo_error = "; ".join(e.message for e in payload.errors) or None
            query.error_codigo, query.error_detalle = None, None
        else:
            error = payload.errors[0] if payload.errors else None
            _failure(query, account, error.code if error else "PROVIDER_UNAVAILABLE",
                     error.message if error else "No fue posible consultar Satrack")
        for error in payload.errors:
            if error.code == "VEHICLE_NOT_FOUND" and error.plate:
                vehicle = operacion.vehicle_by_plate(db, tenant, _plate(error.plate))
                if vehicle:
                    _satellite_vehicle(db, account, vehicle.id).en_satelital = False
                    trip = operacion.active_trip(db, tenant, vehicle.id)
                    registrar_evento(db, tenant, trip.id if trip else None, "placa_no_encontrada", {"placa": vehicle.placa})
    registrar_evento(db, tenant, None, "consulta_satelital", {"job_id": query.job_id, "estado": query.estado,
                                                              "tardio": late})
    db.commit()
    return {"status": "ok", "tardio": True} if late else {"status": "ok"}


def trip_positions(db, tenant, trip_id, limit):
    operacion.get_trip(db, tenant, trip_id)
    rows = list(db.scalars(select(Posicion).where(Posicion.viaje_id == trip_id, Posicion.transportadora_id == tenant)
                          .order_by(Posicion.capturado_en.desc(), Posicion.id.desc()).limit(limit)))
    return [PosicionDTO.model_validate(p) for p in reversed(rows)]


def vehicle_states(db, tenant, vehicle_ids):
    result = {}
    if not vehicle_ids:
        return result
    rows = db.execute(select(VehiculoSatelital, Posicion).outerjoin(Posicion,
        VehiculoSatelital.ultima_posicion_id == Posicion.id).where(
        VehiculoSatelital.transportadora_id == tenant, VehiculoSatelital.vehiculo_id.in_(vehicle_ids)))
    for row, position in rows:
        result[row.vehiculo_id] = EstadoVehiculoDTO(en_satelital=row.en_satelital, alias=row.alias,
            device_id=row.device_id, ultima_posicion=PosicionDTO.model_validate(position) if position else None)
    return result


def vehicles_with_position(db, tenant):
    return db.scalar(select(func.count()).select_from(VehiculoSatelital).where(
        VehiculoSatelital.transportadora_id == tenant, VehiculoSatelital.ultima_posicion_id.is_not(None)))


def verify_plate_for_new_trip(db, *, transportadora_id, viaje_id, vehiculo_id):
    trip = operacion.get_trip(db, transportadora_id, viaje_id)
    if trip.estado != "registrado" or trip.vehiculo.id != vehiculo_id:
        return
    lock_carrier(db, transportadora_id)
    account = _account(db, transportadora_id, lock=True)
    if account is None or account.estado == "credenciales_invalidas":
        return
    states = vehicle_states(db, transportadora_id, [vehiculo_id])
    if account.estado == "ok" and states.get(vehiculo_id, EstadoVehiculoDTO()).en_satelital:
        operacion.schedule_verified_trips(db, transportadora_id, vehiculo_id)
    else:
        _reserve(db, account)
