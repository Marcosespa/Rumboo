# Rumboo — Implementación del MVP

> Documento técnico de implementación. La visión de producto está en [IDEA.md](IDEA.md).
> **Referencia técnica subordinada al [Plan maestro del MVP](backend/PLAN.md).** El alcance, las decisiones y los criterios vigentes se definen allí. Este documento conserva el detalle de reglas propuesto; sus discrepancias no autorizan requisitos adicionales.

---

## 1. Decisiones de arquitectura

| Decisión | Elección MVP |
|---|---|
| Infraestructura | **Un solo servidor**, todo con `docker compose` |
| Monolito | API FastAPI + scheduler + motor de reglas ([backend/PLAN.md](backend/PLAN.md)) |
| Bandeja web | SPA React + Vite + Tailwind ([web/PLAN.md](web/PLAN.md)) |
| Satrack | **Microservicio aparte en Python + FastAPI** (`satrack-service`) que envuelve el crawler Selenium existente ([satrack-service/PLAN.md](satrack-service/PLAN.md)) |
| Comunicación monolito ↔ Satrack | **Request + callback HTTP**. Sin colas ni Redis |
| Base de datos | Un Postgres  que **solo usa el monolito**. |
| Archivos | Volumen local del servidor (`/data`) |

```
┌──────────────────────── Servidor único (docker compose) ───────────────────────┐
│                                                                                │
│  NGIX (HTTPS) ──▶ Bandeja web ──▶ Monolito ──── 1. POST /v1/jobs ───────────▶ │
│                                    (API +         satrack-service (Python)     │
│                                    scheduler +    ◀─ 2. POST callback ──────── │
│                                    reglas)                                     │
│                                       │                                        │
│                                    Postgres + PostGIS      OpenWA      /data   │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Microservicio `satrack-service`

### 2.1 Responsabilidad

**Recibe una petición, consulta Satrack y le devuelve el resultado al monolito por callback.**

- No tiene base de datos, no tiene scheduler y no sabe qué es un viaje.
- **El monolito decide** cuándo consultar y qué hacer con las posiciones.
- Si se reinicia, solo pierde la sesión de Satrack en memoria y vuelve a iniciar sesión en la siguiente petición.

### 2.2 Stack

- Python 3.12
- FastAPI + Uvicorn (HTTP) + Pydantic (validación de payloads)
- **Selenium 4 + Chromium headless**: el crawler existente (`crawler.py`) hace el login y lee la lista de vehículos del DOM
- httpx (callback al monolito con reintentos)
- `logging` estándar (logs)

Se eligió Python + Selenium para **reutilizar el crawler que ya funciona** y tener un solo lenguaje con el monolito. El plan detallado está en [satrack-service/PLAN.md](satrack-service/PLAN.md).

### 2.3 Flujo

```
Monolito                                   satrack-service                    Satrack
   │  POST /v1/jobs {job_id, type, account, plates}                               │
   │──────────────────────────────────────────▶│                                  │
   │  202 Accepted {job_id}                    │                                  │
   │◀──────────────────────────────────────────│                                  │
   │                                           │── login (si no hay sesión) ─────▶│
   │                                           │── consulta posiciones ──────────▶│
   │                                           │◀───────────────────────────────── │
   │  POST {CALLBACK_URL} {job_id, status, positions, errors}                     │
   │◀──────────────────────────────────────────│                                  │
   │  200 OK                                   │                                  │
   │──────────────────────────────────────────▶│                                  │
```

### 2.4 API

Todas las peticiones llevan el header `X-Api-Key: <SATRACK_SERVICE_API_KEY>`.

#### `POST /v1/jobs`

```json
{
  "job_id": "7f1c2e9a-...",              // UUID generado por el monolito (idempotencia)
  "type": "positions",                   // "positions" | "vehicles"
  "account": {
    "id": "transp_12",                   // id de la cuenta en el monolito (clave del caché de sesión)
    "username": "usuario_satrack",
    "password": "********"
  },
  "plates": ["ABC123", "XYZ789"]         // solo para type = positions
}
```

Respuestas:

- `202 Accepted {"job_id": "..."}`: el job quedó aceptado.
- `422`: el payload es inválido (validación de FastAPI).
- `401`: el API key es inválido.
- `409`: el `job_id` ya fue recibido; no se procesa dos veces.

Tipos de job:

- **`positions`**: devuelve la última posición de cada placa pedida.
- **`vehicles`**: devuelve todas las placas que ve la cuenta. Se usa para validar la placa al registrar un viaje.

#### `GET /health`

Responde `{"status":"ok","provider":"satrack","running_jobs":1,"queued_jobs":0,"sessions":2}`.

### 2.5 Callback al monolito

El microservicio hace `POST` a la URL fija `CALLBACK_URL` (variable de entorno, nunca viene en la petición) con estos headers:

- `X-Job-Id: <job_id>`
- `X-Signature: sha256=<HMAC del body con CALLBACK_SECRET>`

```json
{
  "job_id": "7f1c2e9a-...",
  "type": "positions",
  "status": "ok",                        // ok | partial | failed
  "finished_at": "2026-10-05T14:05:12Z",
  "positions": [
    {
      "plate": "ABC123",
      "lat": 4.6097,
      "lng": -74.0817,
      "speed_kmh": null,                       // la lista de Satrack no muestra velocidad (el simulador sí la envía)
      "status": "on",                          // clase del ícono de estado en Satrack
      "address": "Vía Bogotá - Girardot km 23",
      "reported_at": "2026-10-05T14:02:00Z",   // hora del GPS normalizada a UTC; null si no se reconoce
      "reported_at_raw": "05/10/2026 09:02:00" // texto original que muestra Satrack
    }
  ],
  "vehicles": [],                         // solo para type = vehicles: [{plate, device_id}]
  "errors": [
    { "plate": "XYZ789", "code": "VEHICLE_NOT_FOUND", "message": "..." }
  ]
}
```

Códigos de error:

| Código | Significado | Nivel |
|---|---|---|
| `AUTH_FAILED` | Usuario o contraseña de Satrack inválidos | job |
| `CAPTCHA_REQUIRED` | Satrack pidió captcha o 2FA | job |
| `PROVIDER_CHANGED` | No se pudo leer la respuesta; Satrack cambió su web | job |
| `PROVIDER_UNAVAILABLE` | Satrack caído o con timeout | job |
| `TIMEOUT` | El job superó `JOB_TIMEOUT_S` (120 s) | job |
| `VEHICLE_NOT_FOUND` | La placa no está en la cuenta | placa |

**Reintentos del callback:** si el monolito no responde 2xx, se reintenta a los 2 s, 10 s y 30 s. Después se descarta y se registra en el log. El monolito lo detecta por timeout (ver §3.3).

### 2.6 Reglas internas del microservicio

1. **Un job a la vez por cuenta.** Hay un mutex por `account.id`. Si llega otro job de la misma cuenta, espera en fila.
2. **Máximo 3 jobs en paralelo** en total (configurable con `MAX_CONCURRENCY`).
3. **Una consulta por cuenta, no por placa.** Se piden todos los vehículos de la cuenta en una sola llamada y se filtran las placas pedidas.
4. **Caché de sesión en memoria:** un Chrome logueado por `account.id` (y hash de las credenciales). En cada job se recarga la página; solo se hace login si no hay sesión o si Satrack devolvió al formulario de login.
5. **Lectura del DOM con Selenium** (el crawler actual). Si más adelante se identifica el endpoint JSON de la web de Satrack, las posiciones pasan a pedirse por HTTP con las cookies de la sesión, sin cambiar este contrato.
6. **Máximo `MAX_SESSIONS` (3) navegadores** abiertos; se cierran tras `SESSION_IDLE_S` (15 min) sin uso.
7. **Timeout duro de `JOB_TIMEOUT_S` (120 s)** por job; al vencerse se cierra el navegador de la cuenta. Es mayor que los 90 s originales porque Selenium espera hasta 60 s la lista de vehículos tras el login.
8. **Evidencia en fallos.** Ante `PROVIDER_CHANGED` o `CAPTCHA_REQUIRED` se guarda un screenshot y el HTML en `/data/satrack/failures/` y se borran a los 7 días.
9. **Nunca registrar contraseñas** en los logs. Las credenciales solo viven en memoria durante el job.
10. Los `job_id` recibidos se recuerdan en memoria durante 1 h para responder `409` a duplicados.

### 2.7 Estructura del código

```
satrack-service/
├── app/
│   ├── main.py              # FastAPI: rutas, auth por API key, lifespan
│   ├── config.py            # Settings (pydantic-settings)
│   ├── schemas.py           # JobRequest, Position, Vehicle, CallbackPayload
│   ├── errors.py            # ProviderError + códigos
│   ├── jobs.py              # dedupe, lock por cuenta, concurrencia, timeout
│   ├── callback.py          # POST al monolito con HMAC y reintentos
│   ├── crawler.py           # crawler Selenium existente (refactorizado)
│   └── providers/
│       ├── base.py          # BaseProvider (ABC) + registro por nombre
│       ├── satrack.py       # SessionPool + adaptador del crawler
│       └── simulator.py     # flota falsa en rutas reales (desarrollo y demos)
├── tests/
├── Dockerfile               # python:3.12-slim + chromium + chromium-driver
└── pyproject.toml
```

```python
class BaseProvider(ABC):                                                # SatrackProvider, SimulatorProvider
    @abstractmethod
    def list_vehicles(self, account: Account) -> list[Vehicle]: ...
    def fetch_positions(self, account: Account) -> list[Position]: ...  # plantilla: toda la flota de la cuenta, normalizada
    def abort(self, account_id: str) -> None: ...                       # corta un job vencido
```

Todo el sistema usa el mismo estilo orientado a clases (clase base abstracta + hijas por proveedor + registro por nombre); ver [backend/PLAN.md §4](backend/PLAN.md#4-arquitectura-orientada-a-clases).

`PROVIDER=simulator` permite desarrollar el monitoreo completo sin credenciales de Satrack.

### 2.8 Variables de entorno

```
PORT=8080
SATRACK_SERVICE_API_KEY=...
CALLBACK_URL=http://api:8000/internal/satrack/callback
CALLBACK_SECRET=...
PROVIDER=satrack            # satrack | simulator
MAX_CONCURRENCY=3
JOB_TIMEOUT_S=120
MAX_SESSIONS=3
SESSION_IDLE_S=900
HEADLESS=true
CHROME_BINARY=/usr/bin/chromium        # en Docker; vacío = Selenium Manager
CHROMEDRIVER_PATH=/usr/bin/chromedriver
```

### 2.9 docker compose (extracto)

```yaml
satrack:
  build: ./satrack-service
  env_file: .env.satrack
  volumes: [satrack_data:/data/satrack]
  mem_limit: 1.5g
  restart: unless-stopped
  # sin "ports": solo accesible como http://satrack:8080 dentro de la red interna
```

---

## 3. Lado del monolito

### 3.1 Tablas nuevas o ajustadas

| Tabla | Campos |
|---|---|
| `cuentas_satelitales` | id, transportadora_id, proveedor, usuario, password_cifrado, estado (ok / credenciales_invalidas / bloqueada / falla), fallos_consecutivos, ultima_consulta_ok |
| `vehiculos` | + cuenta_satelital_id |
| `consultas_satelitales` | job_id (PK), cuenta_satelital_id, tipo, placas, enviado_en, respondido_en, estado (pendiente / ok / parcial / fallido / timeout), error |
| `posiciones` | + `UNIQUE(vehiculo_id, reported_at)` para no duplicar puntos |

La contraseña de Satrack se guarda cifrada en el monolito y solo se descifra para armar el request.

### 3.2 Job de consulta (scheduler, cada 1 min)

1. Buscar las cuentas satelitales que tengan viajes en estado **Programado** (desde 1 h antes de la salida), **En ruta** o **Con novedad**.
2. Elegir las que ya cumplieron su frecuencia (§4.3) y que **no tengan una consulta `pendiente`**.
3. Por cada cuenta: crear la fila en `consultas_satelitales` y enviar `POST /v1/jobs` con todas las placas activas de esa cuenta.

### 3.3 Endpoint de callback `POST /internal/satrack/callback`

1. Validar la firma HMAC. Si no es válida, responder `401`.
2. Si el `job_id` ya fue procesado, responder `200` sin hacer nada (idempotencia).
3. Guardar las posiciones; los duplicados se ignoran por el `UNIQUE`.
4. Actualizar el estado de la consulta y de la cuenta satelital.
5. Ejecutar el motor de reglas (§4.4) para los viajes afectados.
6. Responder `200`.

**Timeout:** si una consulta lleva más de **3 min** en `pendiente`, el scheduler la marca `timeout` y cuenta como fallo técnico (§4.5).

---

## 4. Reglas del producto

> Los valores entre `[ ]` son **parámetros configurables por transportadora** con su valor por defecto (§4.12).
> Las reglas marcadas con **(propuesta)** no estaban en IDEA.md y deben confirmarse.

### 4.1 Registro de viajes

| # | Regla |
|---|---|
| REG-01 | El **número de manifiesto es único** por transportadora |
| REG-02 | Un viaje tiene **al menos una remesa**, y cada número de remesa es único dentro del viaje |
| REG-03 | **Placa** del vehículo con formato `AAA999` (3 letras + 3 dígitos); se normaliza a mayúsculas y sin espacios ni guiones |
| REG-04 | **Cédula** del conductor: solo dígitos, entre 6 y 10 |
| REG-05 | **Teléfono/WhatsApp** del conductor: celular colombiano de 10 dígitos que empiece por 3; se guarda como `+57XXXXXXXXXX` |
| REG-06 | **Peso** de cada remesa > 0 kg. El peso de salida del viaje es la suma de sus remesas |
| REG-07 | Origen ≠ destino, y la llegada estimada debe ser posterior a la salida estimada |
| REG-08 | La placa debe **existir en la cuenta de Satrack** de la transportadora (se valida con un job `vehicles`). Si no existe, el viaje se puede guardar pero no pasa a Programado |
| REG-09 | Un vehículo **no puede tener dos viajes activos** a la vez (Programado, En ruta o Con novedad) |
| REG-10 | Un conductor no puede tener dos viajes activos a la vez |
| REG-11 | Sin **autorización del conductor** (Ley 1581: ubicación, llamadas, grabación y WhatsApp) no se activan llamadas ni mensajes. El viaje se monitorea solo por satelital y queda marcado |
| REG-12 | La ruta planificada se define con una de tres opciones: trazado, ciudades intermedias o ruta calculada (decisión pendiente). Sin ruta, las reglas de desvío no aplican y el viaje queda marcado |
| REG-13 | La carga por Excel valida fila por fila: las filas válidas se crean y las inválidas se devuelven con el motivo |

### 4.2 Estados del viaje

```
Registrado → Programado → En ruta ⇄ Con novedad → Entregado → Cumplido pendiente → Cumplido RNDC → Cerrado
     └──────────┴────────────┴──────────→ Cancelado
```

| De → A | Disparador |
|---|---|
| Registrado → Programado | Datos completos y validados (REG-01 a REG-12) |
| Programado → En ruta | El vehículo **sale de la geocerca de origen** |
| En ruta → Con novedad | Existe al menos una alerta abierta de severidad media o alta |
| Con novedad → En ruta | Todas las alertas de severidad media o alta quedaron cerradas |
| En ruta / Con novedad → Entregado | Regla de llegada (MON-05) |
| Entregado → Cumplido pendiente | Se pidió la foto del cumplido al conductor |
| Cumplido pendiente → Cumplido RNDC | Aprobación humana y transmisión exitosa al RNDC (o marcado como cargado manualmente) |
| Cumplido RNDC → Cerrado | Confirmación enviada a la transportadora |
| Cualquiera antes de Entregado → Cancelado | Acción manual de un operador, con motivo obligatorio |

- **EST-01:** las transiciones solo ocurren por las reglas de esta tabla o por un operador. Toda transición manual exige usuario y motivo.
- **EST-02:** cada transición se registra en el log de eventos.
- **EST-03 (propuesta):** si el viaje sigue en Programado `[2 h]` después de la salida estimada, se genera la alerta "Viaje no ha iniciado".

### 4.3 Frecuencia de consulta satelital

| # | Regla |
|---|---|
| FRE-01 | Se consulta cada `[5 min]`; el rango permitido es de 5 a 10 min |
| FRE-02 | Solo se consultan cuentas con viajes en Programado (desde 1 h antes de la salida), En ruta o Con novedad |
| FRE-03 | Se deja de consultar un vehículo cuando su viaje pasa a Entregado o Cancelado |
| FRE-04 | Nunca hay más de una consulta pendiente por cuenta |

### 4.4 Motor de reglas de monitoreo

Es determinístico y no usa IA. Se ejecuta con cada callback.

| # | Regla | Condición | Severidad | Acción |
|---|---|---|---|---|
| MON-01 | **Desvío de ruta** | A más de `[5 km]` del corredor planificado en `[2]` lecturas consecutivas | Alta | Alerta inmediata + WhatsApp al conductor |
| MON-02 | **Detención prolongada** | Velocidad < `[5 km/h]` por más de `[60 min]` fuera de un punto autorizado | Media | Llamada al conductor; si no hay explicación, alerta a la transportadora |
| MON-03 | **Retraso** | ETA > llegada pactada + `[60 min]` | Baja | Se incluye en el reporte de 3 h |
| MON-04 | **Sin señal** | El `reported_at` del vehículo no cambia en más de `[30 min]` **y** las consultas a Satrack sí funcionan | Alta | Alerta inmediata + llamada al conductor |
| MON-05 | **Llegada** | Dentro de la geocerca de destino (radio `[1 km]`) en `[2]` lecturas consecutivas | — | Estado Entregado + inicio del cierre (§4.9) |
| MON-06 (propuesta) | **Exceso de velocidad** | Velocidad > `[80 km/h]` en `[2]` lecturas consecutivas | Media | Se registra y se incluye en el reporte |

- **Puntos autorizados** (para MON-02): origen, destino, y paraderos o estaciones configurados por la transportadora `[lista]`.
- **ETA:** distancia restante por la ruta ÷ velocidad promedio de las últimas `[2 h]` en movimiento. Si no hay datos, se usa la velocidad de referencia `[50 km/h]`.
- **Avance %:** distancia recorrida sobre la ruta ÷ distancia total de la ruta.

### 4.5 Fallas técnicas del satelital

Una falla técnica **no es** "sin señal" del vehículo y nunca debe disparar una alerta MON-04 a la transportadora.

| # | Regla |
|---|---|
| TEC-01 | Una consulta con `status = failed` o `timeout` suma 1 a `fallos_consecutivos` de la cuenta. Una `ok` o `partial` lo reinicia en 0 |
| TEC-02 | Con `[3]` fallos consecutivos se envía una **alerta interna** al equipo de Rumboo |
| TEC-03 | Si la falla supera `[30 min]`, se avisa a la transportadora: "Monitoreo satelital degradado". Las llamadas al conductor continúan |
| TEC-04 | Con `AUTH_FAILED`: la cuenta pasa a `credenciales_invalidas`, se deja de consultar y se pide a la transportadora actualizar la contraseña |
| TEC-05 | Con `CAPTCHA_REQUIRED` o `PROVIDER_CHANGED`: alerta interna inmediata y backoff de `[15 min]` antes de volver a consultar esa cuenta |
| TEC-06 | Con `VEHICLE_NOT_FOUND` para una placa de un viaje activo: alerta a la transportadora |

### 4.6 Alertas

| # | Regla |
|---|---|
| ALE-01 | Las alertas tienen tipo, severidad (alta / media / baja), estado (abierta / atendida / cerrada) y timestamp |
| ALE-02 | **No se duplican:** si ya hay una alerta abierta del mismo tipo para el viaje, no se crea otra |
| ALE-03 | **Cierre automático:** cuando la condición desaparece (vuelve al corredor, se mueve, vuelve la señal), la alerta se cierra sola y queda registrado |
| ALE-04 | Si una alerta de severidad alta sigue abierta y nadie la atiende, se re-notifica cada `[30 min]` |
| ALE-05 | Severidad alta → notificación inmediata. Media → notificación inmediata a la bandeja y en el reporte. Baja → solo en el reporte |
| ALE-06 | Atender una alerta exige usuario y comentario |
| ALE-07 | Meta: menos de 10 min desde la anomalía hasta la notificación |

### 4.7 Comunicación con el conductor

#### Llamadas

| # | Regla |
|---|---|
| CON-01 | Llamada **cada `[60 min]`** mientras el viaje está En ruta o Con novedad |
| CON-02 | Si hubo cualquier contacto con el conductor en los últimos `[30 min]` (llamada contestada o WhatsApp respondido), se omite la llamada programada |
| CON-03 | La llamada es corta: máximo `[3]` preguntas y `[2 min]` |
| CON-04 | Si no contesta: reintento a los `[10 min]`, luego WhatsApp. Tras `[2]` intentos fallidos, alerta media a la transportadora |
| CON-05 | La respuesta se transcribe y la IA la clasifica: sin novedad, retraso, avería, accidente, problema con la carga u otro |
| CON-06 | Si la IA tiene baja confianza en la clasificación, se marca "otro" y queda para revisión humana |
| CON-07 | Accidente o problema con la carga → alerta **alta** inmediata. Avería → alerta **media**. Retraso → baja |
| CON-08 (propuesta) | **Horario de descanso:** entre `[22:00 y 05:00]`, si el vehículo está detenido en un punto autorizado no se llama |
| CON-09 | Las llamadas disparadas por reglas (MON-02, MON-04) ignoran CON-01 y CON-02, pero respetan CON-08 |

#### WhatsApp

| # | Regla |
|---|---|
| WA-01 | Solo se escribe a conductores con autorización (REG-11) |
| WA-02 | Se reciben texto, audio y fotos. Los audios se transcriben y pasan por la misma clasificación que CON-05 |
| WA-03 | Todo mensaje entrante se asocia al viaje activo del conductor. Si no tiene viaje activo, va a la bandeja como "sin viaje" |
| WA-04 | Se usa un número dedicado por operación (riesgo de baneo de OpenWA) |
| WA-05 (propuesta) | Máximo `[1]` mensaje automático cada `[15 min]` al conductor, salvo en el cierre del viaje |

#### Instalación de OpenWA (desarrollo)

OpenWA corre como servicio aparte desde su propio repositorio ([rmyndharis/OpenWA](https://github.com/rmyndharis/OpenWA)), fuera de este repo:

```bash
git clone https://github.com/rmyndharis/OpenWA.git
cd OpenWA
docker compose -f docker-compose.dev.yml up -d
```

La integración con el monolito (envío de mensajes, webhook de mensajes entrantes y reglas WA-01 a WA-05) está planificada para la semana 5 (§5) y no forma parte del MVP inicial. Al implementarla hay que definir:

- Si OpenWA se agrega como servicio del `docker compose` principal o se sigue levantando desde su repo.
- La URL interna y la autenticación entre el monolito y OpenWA, y la URL del webhook de mensajes entrantes.
- El número dedicado (WA-04) y dónde se guarda la sesión de WhatsApp, para no tener que escanear el QR en cada reinicio.

### 4.8 Reportes a la transportadora

| # | Regla |
|---|---|
| REP-01 | **Cada `[3 h]`:** un resumen **consolidado por transportadora** con todos sus viajes activos: ubicación, avance %, ETA, retraso y novedades del periodo |
| REP-02 | **Inmediato:** alertas de severidad alta y media (ALE-05) |
| REP-03 | Canal: WhatsApp del coordinador + bandeja web; email opcional `[canal]` |
| REP-04 | Si la transportadora no tiene viajes activos, no se envía el reporte |
| REP-05 | Al cerrar un viaje se envía la confirmación con los documentos del cumplido |

### 4.9 Cierre del viaje y cumplido

| # | Regla |
|---|---|
| CUM-01 | Al detectar la llegada (MON-05) se pide por WhatsApp la foto del cumplido (remesa firmada y sellada) |
| CUM-02 | Si no llega la foto, se envía un recordatorio cada `[2 h]`; a las `[6 h]`, alerta media; a las `[24 h]`, alerta alta |
| CUM-03 | Un LLM de visión extrae: número de remesa o manifiesto, firma, sello, fecha, peso o cantidades recibidas y observaciones |
| CUM-04 | **Coincidencia de documento:** el número de remesa o manifiesto extraído debe coincidir con el viaje |
| CUM-05 | **Firma y sello** deben estar presentes |
| CUM-06 | **Fecha:** igual o posterior a la salida del viaje y no futura |
| CUM-07 | **Peso:** el RNDC trabaja con peso; se compara el peso de salida vs. el entregado. Diferencia > `[0,5 %]` (propuesta) → excepción. Las cantidades (cajas) se registran como dato complementario |
| CUM-08 | Observaciones de faltantes o averías → excepción |
| CUM-09 | Si la foto es ilegible o la IA tiene baja confianza en un campo crítico, se pide una nueva foto al conductor |
| CUM-10 | Si todo cuadra, queda "listo para aprobar". Si no, va como excepción a la bandeja |
| CUM-11 | **Aprobación humana obligatoria** para todo lo que va al RNDC (con un clic, registrando usuario y hora) |
| CUM-12 | La transmisión al RNDC se reintenta `[3]` veces. Si falla, el cumplido queda como "preparado" para carga manual y se alerta a la transportadora |
| CUM-13 | Un viaje con varias remesas solo se cierra cuando todas tienen cumplido |

### 4.10 Cumplimiento regulatorio

| # | Regla |
|---|---|
| REGU-01 | Indicador por transportadora: **% de cumplidos pendientes** sobre los manifiestos de los últimos 30 días (Res. 20263040016075 de 2026, umbral 20 %) |
| REGU-02 (propuesta) | Alerta preventiva a la transportadora al llegar al `[15 %]` y alerta alta al `[18 %]` |
| REGU-03 | Contador de **días hábiles** desde la entrega, para el pago del saldo en máximo 5 días hábiles (Decreto 1017 de 2025). Excluye fines de semana y festivos de Colombia |
| REGU-04 (propuesta) | Alerta al día hábil `[3]` si el cumplido no se ha transmitido |

### 4.11 Seguridad, datos y auditoría

| # | Regla |
|---|---|
| SEG-01 | **Aislamiento por transportadora:** cada usuario solo ve los viajes, conductores y alertas de su transportadora |
| SEG-02 | Roles: **admin de transportadora** (configuración y usuarios) y **operador** (viajes, alertas y aprobaciones) |
| SEG-03 | **Log inmutable** de eventos: posiciones, llamadas, mensajes, alertas, transiciones, aprobaciones (quién y cuándo). No se edita ni se borra |
| SEG-04 | Las credenciales de Satrack se guardan cifradas y nunca se muestran después de guardarlas |
| SEG-05 | Las grabaciones, fotos y audios se guardan en `/data` y solo se acceden por URLs firmadas de la bandeja |
| SEG-06 | La autorización del conductor (REG-11) se guarda con fecha y canal de aceptación |
| SEG-07 | La IA interpreta y extrae, pero **no decide**: alertas, validaciones y transiciones son código determinístico |

### 4.12 Parámetros configurables por transportadora

| Parámetro | Default |
|---|---|
| Frecuencia de consulta satelital | 5 min |
| Corredor de desvío | 5 km |
| Lecturas consecutivas para desvío y llegada | 2 |
| Velocidad para considerar detenido | 5 km/h |
| Tiempo de detención prolongada | 60 min |
| Puntos autorizados de parada | origen + destino |
| Margen de retraso | 60 min |
| Tiempo sin señal | 30 min |
| Radio de geocerca de destino | 1 km |
| Límite de velocidad (propuesta) | 80 km/h |
| Frecuencia de llamadas | 60 min |
| Horario de descanso (propuesta) | 22:00–05:00 |
| Frecuencia del reporte | 3 h |
| Canal de reportes | WhatsApp + bandeja |
| Contactos para alertas | coordinador(es) |
| Tolerancia de peso del cumplido (propuesta) | 0,5 % |
| Umbral de alerta de cumplidos pendientes (propuesta) | 15 % |

---

## 5. Plan de trabajo

| Semanas | Entregable |
|---|---|
| 1 | Investigar Satrack (¿captcha o 2FA? ¿endpoint JSON? ¿una cuenta ve toda la flota?). Acceso al RNDC. Servidor con docker compose, Postgres y el monolito base |
| 2 | `satrack-service` con el proveedor `simulator`, el callback y el job de consulta del monolito |
| 3 | Adaptador real de Satrack + registro de viajes (web + Excel) con REG-01 a REG-13 |
| 4 | Motor de reglas (MON, TEC, ALE) y bandeja web con viajes y alertas |
| 5 | OpenWA (WA-01 a WA-05) |
| 6 | Agente de voz (CON-01 a CON-09) |
| 7 | Reportes (REP-01 a REP-05) |
| 8–9 | Cierre y cumplido (CUM-01 a CUM-13), conector RNDC e indicadores (REGU) |
| 10–12 | Piloto: primero en sombra, luego asistido |

---

## 6. Pendientes por resolver

- [ ] ¿El login de Satrack tiene captcha o 2FA? (define si el scraping es viable)
- [ ] ¿Satrack ofrece web service o API para clientes? (reemplazaría el scraping sin tocar el contrato con el monolito)
- [ ] Autorización escrita de la transportadora para usar sus credenciales de forma automatizada
- [ ] Credenciales de Satrack: ¿por transportadora o por vehículo?
- [ ] Cómo se carga la ruta planificada (REG-12)
- [ ] Proveedor de telefonía y agente de voz
- [ ] Canal principal de reportes
- [ ] Validar con la transportadora piloto todas las reglas marcadas **(propuesta)**
