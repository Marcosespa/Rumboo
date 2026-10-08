"""Infraestructura compartida. No conoce ningún dominio de negocio.

- config: variables de entorno.
- db: engine, Base declarativa y fechas UTC.
- seguridad: contraseñas, hash de tokens y cifrado Fernet.
- errores: errores de negocio sin HTTP (core.web los traduce).
- eventos: reacciones entre módulos sin que el que publica conozca al que escucha.
- tareas: runner de tareas de fondo independiente del proceso que lo ejecuta.
- paginacion: formato común de listados.
- web: única parte de core que conoce FastAPI (sesión de BD por petición y errores HTTP).

Ningún archivo de core importa módulos de negocio; import-linter lo verifica.
"""
