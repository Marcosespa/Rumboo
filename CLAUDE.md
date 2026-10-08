# Rumboo — instrucciones para Claude

Rumboo ayuda a equipos de tráfico de transportadoras en Colombia a seguir viajes y recuperar/cerrar cumplidos. Monorepo: `backend/` (FastAPI + PostgreSQL), `satrack-service/` (scraper Selenium como API), `landing-page/` (estática). **Fuente de verdad del alcance: `backend/PLAN.md`**; fronteras y runner: `docs/ARQUITECTURA_BACKEND.md`. Si el código y el plan discrepan, gana el plan; si el plan está mal, dilo antes de implementar.

## 1. Actitud: sé crítico antes que complaciente

- **Cuestiona mis decisiones de diseño antes de implementarlas.** Si ves un problema de seguridad, rendimiento o arquitectura, dilo aunque no te lo haya preguntado. Propón alternativas cuando mi enfoque no sea el mejor.
- Si una petición contradice `PLAN.md`, una regla de esta página o introduce deuda, detente y explica el conflicto con una recomendación concreta. No lo "arregles en silencio" ni lo implementes a medias.
- Prefiere el cambio más pequeño que resuelve el problema. Nada de abstracciones especulativas, frameworks internos, flags "por si acaso" ni código para épicos que no se están implementando.
- Reporta con honestidad: si no corriste las pruebas, dilo; si fallan, muestra la salida. "Debería funcionar" no es evidencia.

## 2. Comandos

```bash
# Base de pruebas del backend (PostgreSQL real; SQLite no reproduce locks ni índices parciales)
docker run -d --name rumboo-test-db -e POSTGRES_USER=rumboo -e POSTGRES_PASSWORD=rumboo \
  -e POSTGRES_DB=rumboo_test -p 127.0.0.1:55432:5432 postgres:16-alpine

cd backend && uv run pytest            # incluye lint-imports y alembic check (tests/test_arquitectura.py)
cd backend && uv run lint-imports      # fronteras entre módulos
cd satrack-service && uv run pytest
scripts/verificar.sh                   # puerta de calidad completa (ruff sobre lo cambiado + fronteras + pruebas)
npm --prefix landing-page run dev      # landing en http://127.0.0.1:4173
```

## 3. Arquitectura del backend (no negociable sin actualizar PLAN.md)

- Módulos por dominio en `backend/app/<modulo>/` con `models.py`, `schemas.py`, `servicio.py`, `router.py`. Las capas y prohibiciones están en `[tool.importlinter]` de `backend/pyproject.toml`; **no las relajes para que algo compile**: rediseña.
- **Cada módulo modifica solo sus tablas.** Otro módulo usa sus funciones públicas y DTO, nunca sus modelos ORM.
- **El negocio no conoce HTTP.** `servicio.py`, `models.py`, `schemas.py` y `core/*` (salvo `core/web.py`) no importan FastAPI/Starlette. Los servicios lanzan errores de `core/errores.py` y `core/web.py` los traduce.
- Casos de uso = funciones. Clases solo para adaptadores y estructuras de datos.
- Un adaptador por sistema externo (`satelital/cliente.py`, futuro `mensajeria/openwa.py`, `voz/cliente.py`, `documentos/almacenamiento.py`). Ningún otro archivo hace HTTP hacia fuera.
- Runner en `core/tareas.py`: recibe funciones por composición, cada ejecución con su propia sesión, HTTP fuera de transacciones, efectos idempotentes. Sin Redis/Celery en el MVP.
- Esquema solo vía Alembic (`alembic revision --autogenerate`, revisar el archivo generado). **Nunca edites una migración ya commiteada**; crea otra.
- `satrack-service/` es un servicio cerrado: no lo modifiques salvo que te lo pida explícitamente. El backend se adapta a su contrato HTTP.

## 4. Seguridad (cada cambio se revisa contra esto)

- **Aislamiento por transportadora:** toda consulta de datos de negocio filtra por la transportadora de la sesión. Un recurso de otra transportadora responde `NoEncontrado` (no `403`, para no revelar existencia). Todo endpoint nuevo lleva prueba de aislamiento.
- **Secretos:** credenciales Satrack cifradas con Fernet (`core/seguridad.cipher`); nunca en respuestas, logs, excepciones, capturas de Selenium ni fixtures reales. No leas ni edites `.env`; usa `.env.example`.
- **Webhooks/callbacks:** firma HMAC verificada con `hmac.compare_digest` sobre el cuerpo crudo, antes de parsear. API keys con `secrets.compare_digest`.
- **Entradas:** validación con Pydantic en el borde; SQL solo con SQLAlchemy parametrizado (prohibido f-strings/`text()` con datos del usuario); `subprocess` sin `shell=True`; rutas de archivos resueltas y confinadas al volumen privado.
- **Salidas externas:** `httpx` siempre con timeout explícito; reintentos acotados e idempotentes; un resultado incierto se reconcilia, no se reenvía a ciegas.
- **Sesiones:** token opaco, guardado como hash (`token_hash`), con vencimiento y revocable. Contraseñas con bcrypt. No introduzcas JWT/OAuth (fuera del MVP).
- **Dependencias:** no agregues ninguna sin justificar por qué la librería estándar o lo ya instalado no basta; fija rango de versión y actualiza `uv.lock`.

## 5. Calidad y no duplicación

- **Antes de escribir una función, busca si ya existe** (`search_graph`/`grep` por nombre y por comportamiento). Reutiliza `core/paginacion.py`, `core/errores.py`, `core/seguridad.py`, `tests/ayudas.py` y los fakes de `tests/conftest.py`. Si encuentras dos implementaciones de lo mismo, dilo y propone consolidar.
- Imita el código vecino: nombres de dominio en español, funciones cortas, comentarios solo para el *porqué*. Sin código muerto, `print`, `TODO` sin dueño ni `except:`/`except Exception: pass`.
- Errores: captura la excepción concreta, encadena con `raise ... from err`, y no ocultes fallos de integraciones.
- Pruebas: comportamiento observable vía API o servicio, contra PostgreSQL real; clientes externos falsos, nunca Satrack/OpenWA reales en la suite. Cubre el camino feliz, el error de dominio, el duplicado/idempotencia y el aislamiento.
- **Deuda conocida — no la copies como patrón:** `satrack-service/crawler.py` (raíz) es el script legado, reemplazado por `app/crawler.py`; servicios que todavía devuelven ORM en vez de DTO; `vehiculos.en_satelital`/`ultima_posicion_id` deben migrar a `VehiculoSatelital` (PLAN §3.2).

## 6. Definición de terminado

Un cambio está listo solo si:
1. `scripts/verificar.sh` pasa (o explicas exactamente qué no se pudo ejecutar y por qué).
2. Tiene pruebas nuevas para el comportamiento nuevo, incluido aislamiento si toca datos de negocio.
3. Si cambia el esquema, hay migración y `alembic check` pasa.
4. Si cambia alcance, contrato o épico, `backend/PLAN.md` se actualizó **antes**.
5. Pasó `/revisar` sin hallazgos bloqueantes abiertos.

## 7. Flujo con subagentes (`.claude/agents/`)

| Cuándo | Agente / comando |
|---|---|
| Antes de implementar algo no trivial (módulo, tabla, integración, cambio de contrato) | `arquitecto-critico`: revisa el enfoque contra PLAN.md y propone alternativas |
| Antes de commitear o abrir PR | `/revisar`: puerta de calidad + `revisor-codigo` y `auditor-seguridad` en paralelo |
| Cambios en acceso, sesiones, secretos, webhooks, archivos o integraciones | `auditor-seguridad` obligatorio aunque el cambio sea pequeño |

Los hallazgos de los agentes son información, no órdenes: verifica cada uno contra el código antes de aplicarlo y descarta los falsos positivos explicando por qué. No hagas commit, push ni despliegue sin que yo lo pida.
