# Plan de implementación — `satrack-service`

> Arranque, contrato implementado y colección Postman: [README del servicio](README.md).

> Microservicio que convierte el crawler de Satrack ([`crawler.py`](crawler.py), Selenium) en un servicio HTTP independiente.
> El crawler se moverá a `app/crawler.py` al implementar. Implementa el contrato de [IMPLEMENTACION.md §2](../IMPLEMENTACION.md#2-microservicio-satrack-service).
>
> **Referencia técnica subordinada al [Plan maestro del MVP](../backend/PLAN.md).** Ese documento gobierna alcance, contratos y decisiones; esta referencia conserva el diseño previo y no acredita el estado de la implementación.

## 1. Responsabilidad

Recibe un *job*, consulta Satrack y devuelve el resultado al backend por **callback HTTP firmado**.

- No tiene base de datos ni scheduler, y no sabe qué es un viaje. **El backend decide** cuándo consultar y qué hacer con los datos.
- Todo su estado vive en memoria (sesiones de navegador, jobs vistos). Si se reinicia, lo único que pierde son las sesiones abiertas en Satrack: vuelve a iniciar sesión en el siguiente job.

## 2. Tecnologías

| Pieza | Elección | Por qué |
|---|---|---|
| Lenguaje | Python 3.12 | El crawler ya existe en Python; el backend también es Python |
| HTTP | FastAPI + Uvicorn | Validación con Pydantic, OpenAPI gratis y async para el callback |
| Scraping | **Selenium 4** (el crawler actual) | Reutiliza la lógica y selectores que ya funcionan. Selenium Manager resuelve el driver en local |
| Navegador | Chromium headless | En Docker se instala `chromium` + `chromium-driver` de Debian (funciona en amd64 y arm64) |
| Cliente HTTP | httpx (async) | Para el callback con reintentos |
| Config | pydantic-settings | Variables de entorno tipadas |
| Dependencias | uv + `pyproject.toml` | Instalación rápida y reproducible (`uv.lock`) |

## 3. Arquitectura interna

```
 POST /v1/jobs ──▶ JobManager ──▶ (lock por cuenta) ──▶ (semáforo global) ──▶ Provider.run(job)  [hilo]
       │                                                                          │
   202 Accepted                                                     SatrackProvider ─▶ SessionPool ─▶ crawler.py (Selenium)
                                                                    SimulatorProvider (camiones falsos)
                                                                                  │
                                         send_callback(payload) ◀─────────────────┘
                                         POST CALLBACK_URL + HMAC, reintentos 2s/10s/30s
```

- **Selenium es bloqueante**, así que cada job corre en un hilo (`asyncio.to_thread`) y el event loop queda libre para recibir más peticiones.
- **Un job a la vez por cuenta** (`asyncio.Lock` por `account.id`): dos jobs de la misma cuenta nunca usan el mismo navegador al tiempo.
- **Máximo `MAX_CONCURRENCY` jobs en paralelo** (semáforo global). El lock de cuenta se toma **antes** del semáforo para que un job en espera no ocupe un cupo.
- **Timeout duro** por job (`JOB_TIMEOUT_S`). Si se vence, se responde `TIMEOUT` y se cierra el navegador de esa cuenta para cortar el trabajo del hilo.

### 3.1 Caché de sesión (`SessionPool`)

Iniciar sesión en Satrack con Selenium tarda 20–40 s y hacerlo cada 5 min aumenta el riesgo de bloqueo. Por eso:

- Se mantiene **un Chrome abierto y logueado por cuenta**, identificado por `account.id` + hash de las credenciales (si cambia la contraseña, se abre sesión nueva).
- En cada job se **recarga** la página de vehículos; solo se hace login si no hay sesión o si Satrack nos devolvió al formulario de login.
- Las sesiones se cierran tras `SESSION_IDLE_S` sin uso (default 15 min, mayor que la frecuencia de consulta de 5 min) y hay un máximo de `MAX_SESSIONS` (se cierra la menos usada).

### 3.2 Proveedores intercambiables

Mismo estilo orientado a clases que el backend ([backend/PLAN.md §4](../backend/PLAN.md#4-arquitectura-orientada-a-clases)): clase base abstracta con el flujo común y una hija por proveedor, registradas por nombre (`PROVIDER=satrack`).

```python
class BaseProvider(ABC):
    name: ClassVar[str]

    def fetch_positions(self, account: Account) -> list[Position]:
        """Plantilla: lee la flota, normaliza placas, convierte 0,0 → null y registra métricas."""
        return [self._normalizar(p) for p in self._leer_posiciones(account)]

    @abstractmethod
    def _leer_posiciones(self, account: Account) -> list[Position]: ...   # toda la flota de la cuenta
    @abstractmethod
    def list_vehicles(self, account: Account) -> list[Vehicle]: ...
    def abort(self, account_id: str) -> None: ...                          # corta un job vencido (por defecto, nada)
    def cleanup_idle(self) -> None: ...
    def close(self) -> None: ...


@providers.register("satrack")
class SatrackProvider(BaseProvider): ...      # SessionPool + crawler Selenium

@providers.register("simulator")
class SimulatorProvider(BaseProvider): ...
```

- `satrack`: usa el crawler real.
- `simulator`: flota falsa moviéndose por rutas reales de Colombia (Bogotá → Cali, Bogotá → Medellín, …). Permite desarrollar y hacer demos **sin credenciales de Satrack**. La contraseña `invalida` simula `AUTH_FAILED`.

**Una consulta por cuenta, no por placa:** el proveedor devuelve toda la flota y el `JobManager` filtra las placas pedidas. Las placas pedidas que no aparecen generan `VEHICLE_NOT_FOUND`.

## 4. API

Todas las peticiones (salvo `/health`) llevan `X-Api-Key: <SATRACK_SERVICE_API_KEY>`.

### `POST /v1/jobs`

```json
{
  "job_id": "7f1c2e9a-5b1d-4c1e-9a43-0f3f8c1f2a10",
  "type": "positions",
  "account": { "id": "12", "username": "usuario_satrack", "password": "********" },
  "plates": ["ABC123", "XYZ789"]
}
```

| Respuesta | Cuándo |
|---|---|
| `202 {"job_id": "..."}` | Job aceptado |
| `401` | API key inválida |
| `409` | `job_id` ya recibido en la última hora (idempotencia) |
| `422` | Payload inválido (p. ej. `positions` sin placas) |

Tipos: `positions` (última posición de cada placa pedida) y `vehicles` (todas las placas de la cuenta, para validar la placa al registrar un viaje).

### `GET /health`

`{"status": "ok", "provider": "satrack", "running_jobs": 1, "queued_jobs": 0, "sessions": 2}`

### Callback al backend

`POST {CALLBACK_URL}` (fija por variable de entorno, nunca viene en la petición) con headers `X-Job-Id` y `X-Signature: sha256=<HMAC-SHA256 del body con CALLBACK_SECRET>`.

```json
{
  "job_id": "7f1c2e9a-...",
  "type": "positions",
  "status": "ok",
  "finished_at": "2026-10-05T14:05:12Z",
  "positions": [
    {
      "plate": "ABC123",
      "lat": 4.6097, "lng": -74.0817,
      "speed_kmh": null,
      "status": "on",
      "address": "Vía Bogotá - Girardot km 23",
      "reported_at": "2026-10-05T14:02:00Z",
      "reported_at_raw": "05/10/2026 09:02:00"
    }
  ],
  "vehicles": [],
  "errors": [{ "plate": "XYZ789", "code": "VEHICLE_NOT_FOUND", "message": "La placa no está en la cuenta" }]
}
```

- `status`: `ok` (sin errores), `partial` (hay errores por placa) o `failed` (error de job).
- El crawler lee la lista de vehículos del DOM, que **no muestra velocidad**: `speed_kmh` llega `null` con Satrack (el simulador sí la envía). `lat`/`lng` llegan `null` si Satrack no las expone.
- `reported_at` se normaliza a UTC desde la hora de Colombia cuando el texto es una fecha reconocible; si no, llega `null` y el backend usa la hora de captura. El texto original siempre viaja en `reported_at_raw`.

### Códigos de error

| Código | Significado | Nivel |
|---|---|---|
| `AUTH_FAILED` | Usuario o contraseña de Satrack inválidos | job |
| `CAPTCHA_REQUIRED` | Satrack pidió captcha o 2FA | job |
| `PROVIDER_CHANGED` | No se encontró la lista de vehículos ni el login: Satrack cambió su web | job |
| `PROVIDER_UNAVAILABLE` | Satrack caído, sin red o el navegador no arrancó | job |
| `TIMEOUT` | El job superó `JOB_TIMEOUT_S` | job |
| `VEHICLE_NOT_FOUND` | La placa no está en la cuenta | placa |

## 5. Cambios sobre el crawler original

Se conserva la lógica de extracción (`_extraer_datos_vehiculo`, selectores y fallbacks). Se cambia:

1. **Sin duplicación:** creación del driver, login y espera de la lista se separan en funciones (`crear_driver`, `iniciar_sesion`, `cargar_vehiculos`) en vez de repetirse en dos funciones.
2. **Errores tipados:** en lugar de `Exception("Error durante el scraping")`, se lanza `ProviderError(code)` distinguiendo login rechazado, captcha, página cambiada o Satrack caído.
3. **Sin `print`:** se usa `logging` y **nunca** se registra la contraseña (`SecretStr`).
4. **Evidencia en fallos:** ante `PROVIDER_CHANGED` o `CAPTCHA_REQUIRED` se guarda screenshot + HTML en `DATA_DIR/failures/` y se borran a los 7 días.
5. Se elimina `scrape_vehiculos_satrack_y_guardar` (escribía en BD vía callback: ahora eso lo hace el backend) y `webdriver-manager` (Selenium 4 ya trae Selenium Manager).
6. Coordenadas `0.0, 0.0` → `null` (en Colombia nunca son válidas).

## 6. Estructura de carpetas

```
satrack-service/
├── app/
│   ├── main.py            # FastAPI: rutas, API key, lifespan
│   ├── config.py          # Settings (variables de entorno)
│   ├── schemas.py         # JobRequest, Position, Vehicle, JobError, CallbackPayload
│   ├── errors.py          # ProviderError + códigos
│   ├── jobs.py            # JobManager: dedupe, lock por cuenta, semáforo, timeout
│   ├── callback.py        # POST firmado con HMAC + reintentos
│   ├── crawler.py         # crawler Selenium (refactor del original)
│   └── providers/
│       ├── __init__.py    # get_provider() según PROVIDER
│       ├── base.py        # BaseProvider (ABC) + registro por nombre
│       ├── satrack.py     # SessionPool + adaptador del crawler
│       └── simulator.py   # flota falsa
├── tests/                 # API, jobs, callback y simulador
├── Dockerfile
├── pyproject.toml
└── .env.example
```

## 7. Variables de entorno

| Variable | Default | Uso |
|---|---|---|
| `SATRACK_SERVICE_API_KEY` | — (obligatoria) | Auth de las peticiones |
| `CALLBACK_URL` | — (obligatoria) | `http://api:8000/internal/satrack/callback` |
| `CALLBACK_SECRET` | — (obligatoria) | Firma HMAC del callback |
| `PROVIDER` | `satrack` | `satrack` \| `simulator` |
| `MAX_CONCURRENCY` | `3` | Jobs en paralelo |
| `JOB_TIMEOUT_S` | `120` | Timeout duro por job (Selenium es más lento que `fetch`) |
| `MAX_SESSIONS` / `SESSION_IDLE_S` | `3` / `900` | Caché de navegadores |
| `HEADLESS` | `true` | `false` para ver el navegador en local |
| `DATA_DIR` | `/data/satrack` | Evidencia de fallos |
| `CHROME_BINARY` / `CHROMEDRIVER_PATH` | vacío | Rutas en Docker; vacío = Selenium Manager |

## 8. Escalabilidad

- **Cuello de botella = navegadores** (~300 MB c/u). Con `MAX_SESSIONS=3` y `mem_limit: 1.5g` cubre varias transportadoras consultando cada 5 min.
- **Escalar horizontalmente** requiere que los jobs de una cuenta siempre caigan en la misma réplica (sesión en memoria). Se resuelve en el backend enrutando por `account.id` (hash → réplica). No se necesita para el MVP.
- **Siguiente paso natural:** si se descubre el endpoint JSON que usa la web de Satrack, `fetch_positions` pasa a ser una petición HTTP con las cookies de la sesión (sin tocar el contrato con el backend). Lo mismo si Satrack ofrece API oficial: es otro `Provider`.

## 9. Manejo de errores

| Situación | Comportamiento |
|---|---|
| Login rechazado | `AUTH_FAILED`; se cierra la sesión. El backend deja de consultar la cuenta |
| Captcha / 2FA | `CAPTCHA_REQUIRED` + evidencia. El backend aplica backoff |
| Selectores no encontrados | `PROVIDER_CHANGED` + evidencia |
| Error de red / Chrome no arranca | `PROVIDER_UNAVAILABLE`; se descarta la sesión |
| Job demasiado largo | `TIMEOUT`; se cierra el navegador de la cuenta |
| Error inesperado | Se registra con traza y se reporta como `PROVIDER_UNAVAILABLE` (el job **siempre** produce callback) |
| Backend no responde el callback | Reintentos a los 2 s, 10 s y 30 s; luego se descarta y se registra. El backend lo detecta por timeout de la consulta |
| Fallo extrayendo un vehículo | Se omite ese vehículo y se sigue con los demás (comportamiento original) |

## 10. Pruebas

- `pytest` con el proveedor simulador y un servidor de callback falso: contrato del endpoint, 401/409/422, firma HMAC, reintentos del callback, filtro de placas y `VEHICLE_NOT_FOUND`, serialización por cuenta y timeout.
- El crawler real no se prueba en CI (requiere credenciales); se valida en local con `PROVIDER=satrack HEADLESS=false`.
