"""Satelital: todo lo de Satrack del lado del backend.

Dueño de: cuentas_satelitales, consultas_satelitales, posiciones.
Hace: credenciales cifradas, reservar una consulta pendiente por cuenta, despachar jobs, aplicar el resultado
del callback de forma idempotente, programar consultas periódicas, historial y última ubicación.
Próximo (M1): reconciliar con GET /v1/jobs/{id} cada 5 s, guardar el resultado completo, sincronizar toda la flota,
contar cada fallo una sola vez y GET /api/consultas-satelitales/{job_id}.

- cliente.py: ÚNICO archivo que conoce el contrato HTTP de satrack-service.
- enlaces.py: cómo se conecta con otros módulos (suscripciones, extensiones y tareas). Lo usa app/main.py.

Depende de: core, auditoria, acceso, operacion (solo por sus servicios). Nadie depende de satelital salvo
indicadores y la raíz de composición.
"""
