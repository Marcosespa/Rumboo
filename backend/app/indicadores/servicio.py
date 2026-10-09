from datetime import datetime, time
from zoneinfo import ZoneInfo
from app.core.db import now
from app.operacion import servicio as operacion
from app.satelital import servicio as satelital


def panel(db, tenant):
    today = datetime.combine(now().astimezone(ZoneInfo("America/Bogota")).date(), time.min, ZoneInfo("America/Bogota"))
    counts, delivered = operacion.trip_counts(db, tenant, today)
    return {"conteos": counts, "entregados_hoy": delivered,
            "vehiculos_con_posicion": satelital.vehicles_with_position(db, tenant),
            "cuenta_satelital": satelital.account_info(db, tenant),
            "viajes_activos": operacion.active_trips(db, tenant)}
