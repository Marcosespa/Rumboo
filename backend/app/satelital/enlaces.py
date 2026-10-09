"""La composición registra estos consumidores y tareas; no hay extensiones globales."""
from functools import partial
from app.core.tareas import TareaPeriodica
from app.satelital import servicio


def connect(bus):
    bus.suscribir("viaje_registrado", servicio.verify_plate_for_new_trip,
                  destinatario="satelital.verificar_viaje.v1")


def tasks(sessions, settings, client):
    return [
        TareaPeriodica("satelital.programar_consultas", settings.scheduler_interval_s,
                       partial(servicio.scheduled_queries, sessions, settings, client)),
        TareaPeriodica("satelital.reconciliar", settings.reconciliation_interval_s,
                       partial(servicio.reconcile_queries, sessions, settings, client)),
        TareaPeriodica("satelital.despachar_reservas", settings.eventos_interval_s,
                       partial(servicio.dispatch_reserved, sessions, settings, client)),
    ]
