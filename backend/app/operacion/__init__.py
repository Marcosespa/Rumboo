"""Operación: el viaje como negocio.

Dueño de: conductores, vehiculos, viajes, remesas.
Hace: alta de viajes con remesas, reservas de conductor/vehículo, consentimiento, transiciones de estado,
catálogos. Próximo: importación Excel atómica por manifiesto.
Publica: `viaje_registrado` (core.eventos) para que otros módulos reaccionen sin que operacion los conozca.
Extensión: `servicio.registrar_datos_vehiculo` permite que otro módulo agregue datos al vehículo serializado
(satelital agrega su última ubicación) sin que operacion dependa de él.
Depende de: core, auditoria, acceso.

Deuda conocida: `vehiculos.en_satelital` y `vehiculos.ultima_posicion_id` son datos de satelital guardados en
esta tabla. Satelital solo los cambia mediante funciones de este servicio; una migración futura los moverá a
`vehiculos_satelitales`, propiedad de satelital.
"""
