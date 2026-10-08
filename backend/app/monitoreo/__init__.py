"""Monitoreo: convertir posiciones en acciones. Se implementa en M3 (reglas sin ruta) y M4 (rutas).

Será dueño de: puntos_control (origen, destino y paradas con coordenadas y radio), alertas (una abierta por
viaje y tipo), novedades y, en M4, rutas_viaje (GeoJSON versionado).
Hará:
- reglas.py: funciones PURAS (viaje, muestras GPS distintas, puntos, parámetros) -> hallazgos o "no evaluable".
  Sin tabla de estado: se recalculan desde las posiciones guardadas, por eso sobreviven a reinicios.
  M3: señal (30 min sin muestra con consultas correctas), detención (<5 km/h por 60 min fuera de paradas;
  sin velocidad no se evalúa), llegada detectada (1 km, 2 muestras; NO pasa el viaje a entregado) y llegada
  pactada vencida (+60 min). M4: desvío (5 km del corredor) y ETA por avance sobre la ruta.
- geo.py: distancias y geocercas con shapely/haversine. Sin PostGIS en el MVP.
- alertas: abrir, deduplicar, atender y cerrar con auditoría; media/alta llevan el viaje a con_novedad.

Escuchará (vía app/main.py): `posiciones_nuevas` de satelital. Satelital no sabe que monitoreo existe.
Depende de: core, auditoria, acceso, operacion, satelital (solo sus servicios).
"""
