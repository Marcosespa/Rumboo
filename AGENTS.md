# Rumboo

Seguimiento de viajes y cumplidos para transportadoras en Colombia. `backend/` (FastAPI + PostgreSQL), `satrack-service/` (scraper Selenium), `landing-page/`. Alcance: `backend/PLAN.md` (prevalece). Fronteras: `docs/ARQUITECTURA_BACKEND.md`.

Reglas para cualquier agente (Claude Code, Codex). `CLAUDE.md` importa este archivo; lo propio de cada herramienta va en el suyo.

## Actitud
- Cuestiona mis decisiones antes de implementarlas. Señala problemas de seguridad, rendimiento o arquitectura aunque no pregunte, con una alternativa concreta.
- Si algo contradice PLAN.md o estas reglas, detente y dilo. No lo resuelvas en silencio.
- El cambio más pequeño que funcione. Nada especulativo.
- No digas que funciona sin haberlo ejecutado.

## Comandos
```bash
docker run -d --name rumboo-test-db -e POSTGRES_USER=rumboo -e POSTGRES_PASSWORD=rumboo \
  -e POSTGRES_DB=rumboo_test -p 127.0.0.1:55432:5432 postgres:16-alpine
scripts/verificar.sh            # ruff (líneas cambiadas) + import-linter + pytest de ambos servicios
cd backend && uv run pytest     # incluye lint-imports y alembic check
```

## Arquitectura
- Módulo = `models.py`, `schemas.py`, `servicio.py`, `router.py`. Cada módulo escribe solo sus tablas; los demás usan sus funciones y DTO.
- El negocio no importa FastAPI. Los servicios lanzan `core/errores.py` y `core/web.py` los traduce a HTTP.
- HTTP saliente solo en adaptadores (`satelital/cliente.py`, etc.), con timeout.
- No relajes `[tool.importlinter]`: rediseña.
- Esquema solo con migraciones Alembic nuevas. Nunca edites una ya commiteada.
- No toques `satrack-service/` sin pedírtelo.

## Seguridad
- Toda consulta filtra por la transportadora de la sesión. Un recurso ajeno responde `NoEncontrado`. Cada endpoint nuevo lleva prueba de aislamiento.
- Credenciales con `core/seguridad.cipher` (`ENCRYPTION_KEYS`). Nunca en respuestas, logs ni errores. No leas, imprimas ni edites ningún `.env` (raíz o subcarpetas); usa `.env.example`.
- Callbacks: HMAC de `"{timestamp}.{body}"`, `compare_digest`, ventana de 5 min.
- SQL solo parametrizado. Sin `shell=True`. Rutas de archivo confinadas al volumen privado.
- Ninguna dependencia nueva sin justificarla.

## Calidad
- Busca antes de escribir (`search_graph`/`grep`). Reutiliza `core/` y `tests/ayudas.py`.
- Imita el código vecino. Sin `except:` amplio, código muerto ni `print`. Usa `raise ... from err`.
- Pruebas contra PostgreSQL real con fakes externos: camino feliz, error, duplicado y aislamiento.
- Deuda a no copiar: servicios que devuelven ORM en vez de DTO.

## Terminado
`scripts/verificar.sh` en verde, pruebas del comportamiento nuevo, migración si cambia el esquema, PLAN.md actualizado si cambia el alcance. No hagas commit ni push sin que lo pida; nunca `git push --force`, `git reset --hard` ni `git commit --no-verify`.
