from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pydantic import ValidationError
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from app.acceso.servicio import lock_carrier
from app.auditoria.servicio import eventos_de_viaje, registrar_evento
from app.core import eventos
from app.core.db import now
from app.core.errores import Conflicto, Invalido, NoEncontrado
from app.core.paginacion import paginar
from app.operacion.models import ACTIVE_STATES, Conductor, Remesa, Vehiculo, Viaje
from app.operacion.schemas import (ConductorDTO, ErrorImportacionDTO, RemesaDTO, ResultadoImportacionDTO, VehiculoDTO,
                                   ViajeDTO, ViajeImportadoDTO, ViajeInput)

BOGOTA = ZoneInfo("America/Bogota")


def _trip(db, tenant, trip_id, lock=False):
    query = select(Viaje).where(Viaje.id == trip_id, Viaje.transportadora_id == tenant)
    trip = db.scalar(query.with_for_update() if lock else query)
    if trip is None:
        raise NoEncontrado("No encontramos ese viaje")
    return trip


def get_trip(db, tenant, trip_id):
    return _trip_dto(db, _trip(db, tenant, trip_id), detail=True)


def _trip_dto(db, trip, detail=False):
    fields = {key: getattr(trip, key) for key in (
        "id", "transportadora_id", "manifiesto", "origen", "destino", "estado", "salida_estimada",
        "llegada_estimada", "peso_salida_kg", "creado_en", "actualizado_en")}
    return ViajeDTO(**fields, conductor=ConductorDTO.model_validate(trip.conductor),
                    vehiculo=VehiculoDTO.model_validate(trip.vehiculo),
                    remesas=tuple(RemesaDTO.model_validate(r) for r in trip.remesas) if detail else (),
                    eventos=tuple(eventos_de_viaje(db, trip.transportadora_id, trip.id)) if detail else ())


def list_trips(db, tenant, state, text, page, page_size):
    query = select(Viaje).options(selectinload(Viaje.conductor), selectinload(Viaje.vehiculo))\
        .join(Vehiculo).join(Conductor).where(Viaje.transportadora_id == tenant)
    if state:
        query = query.where(Viaje.estado == state)
    if text.strip():
        pattern = f"%{text.strip()[:100]}%"
        query = query.where(or_(Viaje.manifiesto.ilike(pattern), Vehiculo.placa.ilike(pattern), Conductor.nombre.ilike(pattern)))
    return paginar(db, query.order_by(Viaje.id.desc()), page, page_size, lambda t: _trip_dto(db, t))


def list_vehicles(db, tenant, page, page_size):
    query = select(Vehiculo).where(Vehiculo.transportadora_id == tenant).order_by(Vehiculo.placa, Vehiculo.id)
    return paginar(db, query, page, page_size, VehiculoDTO.model_validate)


def list_drivers(db, tenant, page, page_size):
    query = select(Conductor).where(Conductor.transportadora_id == tenant).order_by(Conductor.nombre, Conductor.id)
    return paginar(db, query, page, page_size, ConductorDTO.model_validate)


def create_trip(db, user, data, update_catalog=True):
    """update_catalog=False (importación): reutiliza conductor y vehículo existentes sin modificarlos ni tocar su
    consentimiento; si el celular difiere, rechaza el viaje para no dejar autorizado un número no confirmado."""
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
    elif update_catalog:
        for key, value in data.conductor.model_dump().items():
            setattr(driver, key, value)
    elif driver.telefono != data.conductor.telefono:
        raise Conflicto("El celular del conductor no coincide con el registrado; actualízalo desde el formulario")
    if update_catalog:
        driver.autorizado_en = now() if driver.autoriza_contacto else None
    if not vehicle:
        vehicle = Vehiculo(transportadora_id=tenant, **data.vehiculo.model_dump())
        db.add(vehicle)
    elif update_catalog:
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
    except IntegrityError as err:
        db.rollback()
        raise Conflicto("El manifiesto, conductor o vehículo ya está asociado a otro viaje activo") from err
    return _trip_dto(db, trip, detail=True)


TRIP_COLUMNS = ("origen", "destino", "salida_estimada", "llegada_estimada", "conductor_nombre", "conductor_cedula",
                "conductor_telefono", "placa", "propietario")


def _text(value):
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value).strip()


def _date(value):
    """Solo fechas reales: un número (serial de Excel o texto de dígitos) no debe leerse como segundos Unix."""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.strip())
        except ValueError:
            return None  # la validación del viaje informa el campo
    if not isinstance(value, datetime):
        return None
    return value.replace(tzinfo=BOGOTA) if value.tzinfo is None else value


def _column(loc):
    if not loc:
        return None
    if loc[0] == "conductor" and len(loc) > 1:
        return f"conductor_{loc[1]}"
    if loc[0] == "vehiculo" and len(loc) > 1:
        return str(loc[1])
    if loc[0] == "remesas" and len(loc) > 2:
        return f"remesa_{loc[2]}"
    return str(loc[0])


def _trip_from_rows(manifest, rows):
    first = rows[0]
    return ViajeInput(
        manifiesto=manifest, origen=_text(first.get("origen")), destino=_text(first.get("destino")),
        salida_estimada=_date(first.get("salida_estimada")), llegada_estimada=_date(first.get("llegada_estimada")),
        conductor={"nombre": _text(first.get("conductor_nombre")), "cedula": _text(first.get("conductor_cedula")),
                   "telefono": _text(first.get("conductor_telefono")), "autoriza_contacto": False},
        vehiculo={"placa": _text(first.get("placa")), "propietario": _text(first.get("propietario"))},
        remesas=[{"numero": _text(r.get("remesa_numero")), "cliente": _text(r.get("remesa_cliente")),
                  "peso_kg": r.get("remesa_peso_kg"), "cantidad": r.get("remesa_cantidad") or None} for r in rows])


def import_trips(db, user, rows):
    """Un viaje por manifiesto, cada uno en su propia transacción: un grupo inválido no crea nada y no impide los
    demás. No modifica conductores ni vehículos existentes. Los errores no repiten valores de celdas."""
    groups, errors, created = {}, [], []
    for row in rows:
        manifest = _text(row.get("manifiesto"))
        if not manifest:
            errors.append(ErrorImportacionDTO(manifiesto="", filas=(row["fila"],), campo="manifiesto",
                                              mensaje="El manifiesto es obligatorio"))
            continue
        groups.setdefault(manifest, []).append(row)
    for manifest, group in groups.items():
        lines = tuple(r["fila"] for r in group)
        mixed = next((c for c in TRIP_COLUMNS if len({_text(r.get(c)) for r in group}) > 1), None)
        if mixed:
            errors.append(ErrorImportacionDTO(manifiesto=manifest, filas=lines, campo=mixed,
                                              mensaje="Las filas del manifiesto deben tener el mismo valor"))
            continue
        try:
            data = _trip_from_rows(manifest, group)
        except ValidationError as err:
            for error in err.errors():
                loc = error["loc"]
                rows_of_error = (group[loc[1]]["fila"],) if loc[:1] == ("remesas",) and len(loc) > 2 else lines
                errors.append(ErrorImportacionDTO(manifiesto=manifest, filas=rows_of_error, campo=_column(loc),
                                                  mensaje=error["msg"].replace("Value error, ", "")))
            continue
        try:
            trip = create_trip(db, user, data, update_catalog=False)
        except Conflicto as err:
            db.rollback()
            errors.append(ErrorImportacionDTO(manifiesto=manifest, filas=lines, campo=None, mensaje=err.mensaje))
            continue
        created.append(ViajeImportadoDTO(manifiesto=manifest, id=trip.id))
    return ResultadoImportacionDTO(creados=tuple(created), errores=tuple(errors))


def transition(db, user, trip_id, data):
    trip = _trip(db, user.transportadora_id, trip_id, lock=True)
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
    return _trip_dto(db, trip, detail=True)


# --- API para otros módulos: la única forma de cambiar estas tablas desde fuera de operacion ---

def get_vehicle(db, tenant, vehicle_id):
    vehicle = db.scalar(select(Vehiculo).where(Vehiculo.id == vehicle_id, Vehiculo.transportadora_id == tenant))
    return VehiculoDTO.model_validate(vehicle) if vehicle else None


def vehicle_by_plate(db, tenant, plate):
    vehicle = db.scalar(select(Vehiculo).where(Vehiculo.transportadora_id == tenant, Vehiculo.placa == plate))
    return VehiculoDTO.model_validate(vehicle) if vehicle else None


def vehicles_of(db, tenant):
    """Flota completa, sin paginar, para la sincronización satelital."""
    return [VehiculoDTO.model_validate(v) for v in db.scalars(
        select(Vehiculo).where(Vehiculo.transportadora_id == tenant).order_by(Vehiculo.placa))]


def import_vehicle(db, tenant, plate):
    """Importa identidad de la flota; satelital conserva alias, presencia y posición."""
    vehicle = db.scalar(select(Vehiculo).where(Vehiculo.transportadora_id == tenant, Vehiculo.placa == plate))
    if vehicle is None:
        vehicle = Vehiculo(transportadora_id=tenant, placa=plate, propietario="")
        db.add(vehicle)
        db.flush()
    return VehiculoDTO.model_validate(vehicle)


def schedule_verified_trips(db, tenant, vehicle_id):
    vehicle = get_vehicle(db, tenant, vehicle_id)
    if vehicle is None:
        raise NoEncontrado("No encontramos ese vehículo")
    for trip in db.scalars(select(Viaje).where(Viaje.transportadora_id == tenant,
            Viaje.vehiculo_id == vehicle_id, Viaje.estado == "registrado").with_for_update()):
        trip.estado = "programado"
        registrar_evento(db, tenant, trip.id, "placa_verificada", {"estado": "programado", "placa": vehicle.placa})


def active_trip(db, tenant, vehicle_id):
    trip = db.scalar(select(Viaje).where(Viaje.transportadora_id == tenant, Viaje.vehiculo_id == vehicle_id,
                                        Viaje.estado.in_(ACTIVE_STATES)))
    return _trip_dto(db, trip) if trip else None


def journey_snapshot(db, tenant, plates):
    rows = db.execute(select(Vehiculo.placa, Viaje.id).join(Viaje, Viaje.vehiculo_id == Vehiculo.id).where(
        Vehiculo.transportadora_id == tenant, Viaje.transportadora_id == tenant,
        Vehiculo.placa.in_(plates), Viaje.estado.in_(ACTIVE_STATES)))
    return dict(rows.all())


def trip_departures(db, tenant, trip_ids):
    """Salida estimada por viaje, en una sola consulta, para asociar posiciones por lotes."""
    ids = set(trip_ids)
    if not ids:
        return {}
    return dict(db.execute(select(Viaje.id, Viaje.salida_estimada).where(
        Viaje.transportadora_id == tenant, Viaje.id.in_(ids))).all())


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


def active_trips(db, tenant, limit=10):
    rows = db.scalars(select(Viaje).options(selectinload(Viaje.conductor), selectinload(Viaje.vehiculo))
                      .where(Viaje.transportadora_id == tenant, Viaje.estado.in_(ACTIVE_STATES))
                      .order_by(Viaje.id.desc()).limit(limit))
    return [_trip_dto(db, trip) for trip in rows]
