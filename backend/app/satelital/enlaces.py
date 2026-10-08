"""Cómo se conecta satelital con el resto. Solo lo llama la raíz de composición (app/main.py).

Ningún otro módulo importa satelital para esto: operacion publica `viaje_registrado` y ofrece una extensión
de datos del vehículo; aquí satelital se suscribe y se registra.
"""
from functools import partial
from app.core.tareas import TareaPeriodica
from app.operacion import servicio as operacion
from app.satelital import servicio


def connect(bus, sessions, settings, client):
    operacion.registrar_datos_vehiculo(servicio.last_position)
    bus.suscribir("viaje_registrado", partial(servicio.verify_plate_for_new_trip, sessions, settings, client))


def tasks(sessions, settings, client):
    return [TareaPeriodica("satelital.programar_consultas", settings.scheduler_interval_s,
                           partial(servicio.scheduled_queries, sessions, settings, client))]
