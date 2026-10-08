from datetime import timedelta
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from app.acceso.servicio import lock_carrier
from app.auditoria.servicio import eventos_de_viaje, registrar_evento
from app.core import eventos
from app.core.db import now
from app.core.errores import Conflicto, Invalido, NoEncontrado
from app.core.paginacion import paginar
from app.operacion.models import ACTIVE_STATES, Conductor, Remesa, Vehiculo, Viaje

# Otros módulos agregan datos al vehículo serializado sin que operacion los conozca (ver registrar_datos_vehiculo).
_vehicle_data = []


def registrar_datos_vehiculo(provider):
    """`provider(db, vehiculo) -> dict` se mezcla en cada vehículo serializado. Lo conecta app/main.py."""
    if provider not in _vehicle_data:
        _vehicle_data.append(provider)


def get_trip(db, tenant, trip_id, lock=False):
    query = select(Viaje).where(Viaje.id == trip_id, Viaje.transportadora_id == tenant)
    trip = db.scalar(query.with_for_update() if lock else query)
    if trip is None:
        raise NoEncontrado("No encontramos ese viaje")
    return trip


def serialize_vehicle(db, v):
    result = {"id": v.id, "placa": v.placa, "propietario": v.propietario, "en_satelital": v.en_satelital}
    for provider in _vehicle_data:
        result.update(provider(db, v))
    return result


def serialize_driver(d):
    return {key: getattr(d, key) for key in ("id", "nombre", "cedula", "telefono", "autoriza_contacto")}


def serialize_trip(db, trip, detail=False):
    result = {key: getattr(trip, key) for key in ("id", "manifiesto", "origen", "destino", "estado", "salida_estimada", "llegada_estimada", "peso_salida_kg", "creado_en", "actualizado_en")}
    result["conductor"] = serialize_driver(trip.conductor)
    result["vehiculo"] = serialize_vehicle(db, trip.vehiculo)
    if detail:
        result["remesas"] = [{key: getattr(r, key) for key in ("id", "numero", "cliente", "peso_kg", "cantidad")} for r in trip.remesas]
        result["eventos"] = eventos_de_viaje(db, trip.transportadora_id, trip.id)
    return result


def list_trips(db, tenant, state, text, page, page_size):
    query = select(Viaje).join(Vehiculo).join(Conductor).where(Viaje.transportadora_id == tenant)
    if state:
        query = query.where(Viaje.estado == state)
    if text.strip():
        pattern = f"%{text.strip()[:100]}%"
        query = query.where(or_(Viaje.manifiesto.ilike(pattern), Vehiculo.placa.ilike(pattern), Conductor.nombre.ilike(pattern)))
    return paginar(db, query.order_by(Viaje.id.desc()), page, page_size, lambda t: serialize_trip(db, t))


def list_vehicles(db, tenant):
    return [serialize_vehicle(db, v) for v in db.scalars(select(Vehiculo).where(Vehiculo.transportadora_id == tenant).order_by(Vehiculo.placa))]


def list_drivers(db, tenant):
    return [serialize_driver(d) for d in db.scalars(select(Conductor).where(Conductor.transportadora_id == tenant).order_by(Conductor.nombre))]


def create_trip(db, user, data):
    tenant = user.transportadora_id
    # Serialize reservations within one carrier, backed by unique active indexes.
    lock_carrier(db, tenant)
    if db.scalar(select(Viaje.id).where(Viaje.transportadora_id == tenant, Viaje.manifiesto == data.manifiesto)):
        raise Conflicto("Ya existe un viaje con ese manifiesto")
    driver = db.scalar(select(Conductor).where(Conductor.transportadora_id == tenant, Conductor.cedula == data.conductor.cedula))
    vehicle = db.scalar(select(Vehiculo).where(Vehiculo.transportadora_id == tenant, Vehiculo.placa == data.vehiculo.placa))
    for obj, column, message in ((driver, Viaje.conductor_id, "El conductor ya tiene un viaje activo"), (vehicle, Viaje.vehiculo_id, "El vehículo ya tiene un viaje activo")):
        if obj and db.scalar(select(Viaje.id).where(column == obj.id, Viaje.estado.in_(ACTIVE_STATES))):
            raise Conflicto(message)
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
        trip = Viaje(transportadora_id=tenant, manifiesto=data.manifiesto, conductor_id=driver.id, vehiculo_id=vehicle.id,
                     origen=data.origen, destino=data.destino, salida_estimada=data.salida_estimada, llegada_estimada=data.llegada_estimada,
                     peso_salida_kg=sum(r.peso_kg for r in data.remesas), estado="registrado")
        db.add(trip)
        db.flush()
        for remesa in data.remesas:
            db.add(Remesa(transportadora_id=tenant, viaje_id=trip.id, **remesa.model_dump()))
        registrar_evento(db, tenant, trip.id, "viaje_creado", {"estado": trip.estado}, user.id)
        # Satelital decide si la placa ya está verificada (programado) o pide verificarla.
        eventos.publicar(db, "viaje_registrado", transportadora_id=tenant, viaje_id=trip.id, vehiculo_id=vehicle.id)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise Conflicto("El manifiesto, conductor o vehículo ya está asociado a otro viaje activo")
    return trip


def transition(db, user, trip_id, data):
    trip = get_trip(db, user.transportadora_id, trip_id, lock=True)
    allowed = {"registrado": {"cancelado"}, "programado": {"en_ruta", "cancelado"}, "en_ruta": {"entregado", "cancelado"}}
    if data.estado not in allowed.get(trip.estado, set()):
        raise Conflicto("Ese cambio no está permitido desde el estado actual")
    if data.estado == "cancelado" and not data.motivo.strip():
        raise Invalido("Escribe el motivo de cancelación")
    previous = trip.estado
    trip.estado = data.estado
    if data.estado == "cancelado":
        trip.motivo_cancelacion = data.motivo.strip()
    registrar_evento(db, user.transportadora_id, trip.id, "estado_actualizado", {"anterior": previous, "estado": data.estado, "motivo": data.motivo.strip() or "Acción manual del operador"}, user.id)
    db.commit()
    return trip


# --- API para otros módulos: la única forma de cambiar estas tablas desde fuera de operacion ---

def get_vehicle(db, tenant, vehicle_id):
    return db.scalar(select(Vehiculo).where(Vehiculo.id == vehicle_id, Vehiculo.transportadora_id == tenant))


def vehicle_by_plate(db, tenant, plate, lock=False):
    query = select(Vehiculo).where(Vehiculo.transportadora_id == tenant, Vehiculo.placa == plate)
    return db.scalar(query.with_for_update() if lock else query)


def vehicles_of(db, tenant):
    return list(db.scalars(select(Vehiculo).where(Vehiculo.transportadora_id == tenant)))


def set_in_satellite(vehicle, present):
    vehicle.en_satelital = present


def set_last_position(vehicle, position_id):
    vehicle.ultima_posicion_id = position_id


def reset_satellite_verification(db, tenant):
    for vehicle in vehicles_of(db, tenant):
        vehicle.en_satelital = None


def schedule_verified_trips(db, tenant, vehicle):
    """Una placa confirmada en el satelital pasa sus viajes `registrado` a `programado`."""
    for trip in db.scalars(select(Viaje).where(Viaje.vehiculo_id == vehicle.id, Viaje.estado == "registrado").with_for_update()):
        trip.estado = "programado"
        registrar_evento(db, tenant, trip.id, "placa_verificada", {"estado": "programado", "placa": vehicle.placa})


def active_trip(db, vehicle_id):
    return db.scalar(select(Viaje).where(Viaje.vehiculo_id == vehicle_id, Viaje.estado.in_(ACTIVE_STATES)))


def plates_to_monitor(db, tenant, at):
    """Placas en ruta, con novedad o programadas para salir dentro de una hora."""
    return list(db.scalars(select(Vehiculo.placa).join(Viaje, Viaje.vehiculo_id == Vehiculo.id).where(
        Viaje.transportadora_id == tenant,
        (Viaje.estado.in_(("en_ruta", "con_novedad"))) | ((Viaje.estado == "programado") & (Viaje.salida_estimada <= at + timedelta(hours=1)))
    )).unique())


def has_unverified_trips(db, tenant):
    return db.scalar(select(Viaje.id).where(Viaje.transportadora_id == tenant, Viaje.estado == "registrado").limit(1)) is not None


def trip_counts(db, tenant, delivered_since):
    counts = dict(db.execute(select(Viaje.estado, func.count(Viaje.id)).where(Viaje.transportadora_id == tenant).group_by(Viaje.estado)).all())
    delivered = db.scalar(select(func.count(Viaje.id)).where(Viaje.transportadora_id == tenant, Viaje.estado == "entregado", Viaje.actualizado_en >= delivered_since))
    return counts, delivered


def vehicles_with_position(db, tenant):
    return db.scalar(select(func.count(Vehiculo.id)).where(Vehiculo.transportadora_id == tenant, Vehiculo.ultima_posicion_id.is_not(None)))


def active_trips(db, tenant, limit=10):
    return list(db.scalars(select(Viaje).where(Viaje.transportadora_id == tenant, Viaje.estado.in_(ACTIVE_STATES)).order_by(Viaje.id.desc()).limit(limit)))
