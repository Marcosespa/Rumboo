from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.db import now
from app.models import ACTIVE_STATES, Conductor, CuentaSatelital, Evento, Posicion, Remesa, Transportadora, Vehiculo, Viaje


def event(db, tenant, trip_id, kind, detail, user_id=None):
    db.add(Evento(transportadora_id=tenant, viaje_id=trip_id, usuario_id=user_id, tipo=kind, detalle=detail))


def get_trip(db, tenant, trip_id, lock=False):
    query = select(Viaje).where(Viaje.id == trip_id, Viaje.transportadora_id == tenant)
    trip = db.scalar(query.with_for_update() if lock else query)
    if trip is None:
        raise HTTPException(404, "No encontramos ese viaje")
    return trip


def serialize_position(p):
    if p is None:
        return None
    return {key: getattr(p, key) for key in ("id", "lat", "lng", "velocidad_kmh", "direccion", "estado_gps", "reportado_en", "reportado_texto", "capturado_en", "viaje_id")}


def serialize_vehicle(db, v):
    return {"id": v.id, "placa": v.placa, "propietario": v.propietario, "en_satelital": v.en_satelital,
            "ultima_posicion": serialize_position(db.get(Posicion, v.ultima_posicion_id)) if v.ultima_posicion_id else None}


def serialize_driver(d):
    return {key: getattr(d, key) for key in ("id", "nombre", "cedula", "telefono", "autoriza_contacto")}


def serialize_trip(db, trip, detail=False):
    result = {key: getattr(trip, key) for key in ("id", "manifiesto", "origen", "destino", "estado", "salida_estimada", "llegada_estimada", "peso_salida_kg", "creado_en", "actualizado_en")}
    result["conductor"] = serialize_driver(trip.conductor)
    result["vehiculo"] = serialize_vehicle(db, trip.vehiculo)
    if detail:
        result["remesas"] = [{key: getattr(r, key) for key in ("id", "numero", "cliente", "peso_kg", "cantidad")} for r in trip.remesas]
        events = db.scalars(select(Evento).where(Evento.viaje_id == trip.id, Evento.transportadora_id == trip.transportadora_id).order_by(Evento.id.desc()).limit(100))
        result["eventos"] = [{"id": e.id, "tipo": e.tipo, "detalle": e.detalle, "creado_en": e.creado_en, "usuario_id": e.usuario_id} for e in events]
    return result


def create_trip(db, user, data):
    tenant = user.transportadora_id
    # Serialize reservations within one carrier, backed by unique active indexes.
    db.scalar(select(Transportadora).where(Transportadora.id == tenant).with_for_update())
    if db.scalar(select(Viaje.id).where(Viaje.transportadora_id == tenant, Viaje.manifiesto == data.manifiesto)):
        raise HTTPException(409, "Ya existe un viaje con ese manifiesto")
    driver = db.scalar(select(Conductor).where(Conductor.transportadora_id == tenant, Conductor.cedula == data.conductor.cedula))
    vehicle = db.scalar(select(Vehiculo).where(Vehiculo.transportadora_id == tenant, Vehiculo.placa == data.vehiculo.placa))
    for obj, column, message in ((driver, Viaje.conductor_id, "El conductor ya tiene un viaje activo"), (vehicle, Viaje.vehiculo_id, "El vehículo ya tiene un viaje activo")):
        if obj and db.scalar(select(Viaje.id).where(column == obj.id, Viaje.estado.in_(ACTIVE_STATES))):
            raise HTTPException(409, message)
    if not driver:
        driver = Conductor(transportadora_id=tenant, **data.conductor.model_dump())
        db.add(driver)
    else:
        for key, value in data.conductor.model_dump().items():
            setattr(driver, key, value)
    driver.autorizado_en = now() if driver.autoriza_contacto else None
    if not vehicle:
        vehicle = Vehiculo(transportadora_id=tenant, **data.vehiculo.model_dump())
        db.add(vehicle)
    else:
        vehicle.propietario = data.vehiculo.propietario
    try:
        db.flush()
        account = db.scalar(select(CuentaSatelital).where(CuentaSatelital.transportadora_id == tenant))
        state = "programado" if vehicle.en_satelital and account and account.estado == "ok" else "registrado"
        trip = Viaje(transportadora_id=tenant, manifiesto=data.manifiesto, conductor_id=driver.id, vehiculo_id=vehicle.id,
                     origen=data.origen, destino=data.destino, salida_estimada=data.salida_estimada, llegada_estimada=data.llegada_estimada,
                     peso_salida_kg=sum(r.peso_kg for r in data.remesas), estado=state)
        db.add(trip)
        db.flush()
        for remesa in data.remesas:
            db.add(Remesa(transportadora_id=tenant, viaje_id=trip.id, **remesa.model_dump()))
        event(db, tenant, trip.id, "viaje_creado", {"estado": state}, user.id)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "El manifiesto, conductor o vehículo ya está asociado a otro viaje activo")
    return trip


def transition(db, user, trip_id, data):
    trip = get_trip(db, user.transportadora_id, trip_id, lock=True)
    allowed = {"registrado": {"cancelado"}, "programado": {"en_ruta", "cancelado"}, "en_ruta": {"entregado", "cancelado"}}
    if data.estado not in allowed.get(trip.estado, set()):
        raise HTTPException(409, "Ese cambio no está permitido desde el estado actual")
    if data.estado == "cancelado" and not data.motivo.strip():
        raise HTTPException(422, "Escribe el motivo de cancelación")
    previous = trip.estado
    trip.estado = data.estado
    if data.estado == "cancelado":
        trip.motivo_cancelacion = data.motivo.strip()
    event(db, user.transportadora_id, trip.id, "estado_actualizado", {"anterior": previous, "estado": data.estado, "motivo": data.motivo.strip() or "Acción manual del operador"}, user.id)
    db.commit()
    return trip
