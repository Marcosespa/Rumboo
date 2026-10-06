# Referencia histórica — Plan anterior del backend

> **Archivo de consulta, sin autoridad sobre el desarrollo.** Conserva el diseño anterior, incluidas propuestas detalladas de voz y herramientas. El alcance, las decisiones y los criterios vigentes están exclusivamente en [PLAN.md](PLAN.md). Las afirmaciones de estado que aparecen a continuación son históricas.

> Monolito que registra viajes, decide cuándo consultar Satrack, guarda posiciones, sirve la bandeja web y, en la fase 2, opera el agente de voz.
> Las reglas de [IMPLEMENTACION.md §4](../IMPLEMENTACION.md#4-reglas-del-producto) se citan por su código (REG-01, FRE-02, CON-04…).
>
> **Estado:** plan. Aún no hay código.

## 1. Alcance

**Fase 1: MVP inicial (núcleo de monitoreo)**
- Login con usuario + contraseña (sin roles, sin OAuth, sin refresh tokens).
- Cuenta de Satrack de la transportadora (contraseña cifrada).
- Registro de viajes con conductor, vehículo y remesas, con las validaciones REG-01 a REG-10.
- Scheduler que pide posiciones al `satrack-service` y endpoint de callback que las guarda.
- Historial de posiciones por vehículo y viaje, y vista de flota con la última posición.
- Transiciones manuales de estado y log de eventos.
- **Arquitectura orientada a clases (§4) desde el primer commit**, para que las fases siguientes se agreguen sin reescribir.

**Fase 2: agente de voz con tool calls (§10)**
- Llamadas al conductor con un Voice Agent que **ejecuta acciones reales mediante herramientas** (registrar novedades, actualizar ETA, programar rellamadas, enviar WhatsApp, escalar al coordinador).
- Proveedores de LLM intercambiables (`OpenAIChatHandler`, `AnthropicChatHandler`, …) y de telefonía (`TwilioProvider`, …).

**Fuera de este plan (fases siguientes)**: motor de reglas y alertas (MON, ALE), WhatsApp (OpenWA; instalación en [IMPLEMENTACION.md §4.7](../IMPLEMENTACION.md#instalación-de-openwa-desarrollo)), reportes, cumplidos/RNDC, carga por Excel (REG-13), ruta planificada (REG-12), usuarios administradores. La fase 2 asume que existen las tablas de alertas y la integración con OpenWA, o las deja como `TODO` detrás de su interfaz (§4).

## 2. Stack

| Pieza | Elección | Por qué |
|---|---|---|
| Lenguaje / framework | Python 3.12 + FastAPI | Mismo lenguaje que el scraper; validación con Pydantic, OpenAPI en `/docs` y WebSockets para el audio de las llamadas |
| ORM | SQLAlchemy 2.0 (síncrono) + psycopg 3 | Estándar, tipado; síncrono es más simple y suficiente para este volumen |
| Migraciones | Alembic | El esquema va a crecer (llamadas, alertas, cumplidos): mejor tener migraciones desde el día 1 |
| Base de datos | PostgreSQL 16 | Ya definido en IMPLEMENTACION.md. PostGIS se agrega cuando lleguen geocercas y desvíos |
| Scheduler | Tarea `asyncio` en el *lifespan* de FastAPI (cada 60 s) | Sin Celery ni Redis: un solo proceso basta para el MVP |
| Cliente HTTP | httpx | `satrack-service`, OpenWA y webhooks |
| Contraseñas | `bcrypt` | Hash de contraseñas de usuarios |
| Cifrado | `cryptography` (Fernet) | Contraseña de Satrack cifrada en BD (SEG-04) |
| LLM (fase 2) | SDKs oficiales `openai` y `anthropic`, **solo dentro de su handler** | Ningún otro módulo importa un SDK de proveedor |
| Telefonía (fase 2) | Twilio (Media Streams por WebSocket) como primera implementación | Proveedor aún por decidir (IMPLEMENTACION.md §6); queda detrás de `TelephonyProvider` |
| Dependencias | uv + `pyproject.toml` | Igual que el scraper. Los SDKs de LLM y telefonía van como *extras* opcionales |

## 3. Estructura del proyecto

```
backend/
├── app/
│   ├── main.py                     # app, routers, CORS, manejo de errores, lifespan (scheduler)
│   ├── config.py                   # Settings (variables de entorno)
│   ├── db.py                       # engine, SessionLocal, Base, get_db
│   ├── models.py                   # modelos ORM
│   ├── schemas.py                  # Pydantic de entrada/salida de la API
│   ├── security.py                 # bcrypt, tokens de sesión, Fernet
│   ├── deps.py                     # get_current_user, fábricas de servicios
│   ├── validators.py               # normalizar placa, cédula, teléfono
│   ├── core/
│   │   └── registry.py             # Registry[T]: registra implementaciones por nombre y las crea
│   ├── routers/                    # HTTP: solo entrada/salida, sin reglas de negocio
│   │   ├── auth.py, viajes.py, flota.py, cuenta_satelital.py, panel.py
│   │   ├── internal.py             # callback del satrack-service
│   │   └── voz.py                  # [fase 2] webhooks y WebSocket de telefonía
│   ├── services/                   # reglas de negocio
│   │   ├── base.py                 # BaseService
│   │   ├── auth.py                 # AuthService
│   │   ├── viajes.py               # ViajeService
│   │   ├── cuenta_satelital.py     # CuentaSatelitalService
│   │   ├── monitoreo.py            # MonitoreoService (tick del scheduler)
│   │   └── llamadas.py             # [fase 2] LlamadaService
│   ├── callbacks/                  # procesamiento del callback del scraper, uno por tipo de job
│   │   ├── base.py                 # CallbackHandler
│   │   ├── positions.py            # PositionsCallbackHandler
│   │   └── vehicles.py             # VehiclesCallbackHandler
│   ├── integrations/               # sistemas externos, siempre detrás de una clase base
│   │   ├── satelital/              # SatelliteClient → SatrackServiceClient
│   │   ├── mensajeria/             # MessagingProvider → OpenWAProvider        [fase WhatsApp]
│   │   └── telefonia/              # TelephonyProvider → TwilioProvider        [fase 2]
│   ├── llm/                        # [fase 2] motor de conversación (§11)
│   │   ├── base.py                 # ChatHandler: estado de la conversación y ciclo de tool calls
│   │   ├── types.py                # tipos neutrales: Message, ToolCall, Etapa, UsoTokens, Turno
│   │   ├── factory.py              # ChatHandlerFactory: crea el handler y fija sus capacidades
│   │   ├── seudonimizacion.py      # reemplaza y restaura datos personales (§11.8)
│   │   ├── openai_chat_handler.py  # OpenAIChatHandler
│   │   ├── anthropic_chat_handler.py  # AnthropicChatHandler
│   │   └── fake_chat_handler.py    # FakeChatHandler (pruebas, respuestas guionadas)
│   ├── voice/                      # [fase 2]
│   │   ├── base.py                 # VoiceHandler
│   │   ├── realtime.py             # RealtimeVoiceHandler → OpenAIRealtimeHandler
│   │   ├── pipeline.py             # PipelineVoiceHandler (STT + ChatHandler + TTS)
│   │   ├── speech.py               # SpeechToText / TextToSpeech
│   │   ├── agent.py                # VoiceAgent: arma objetivo, contexto y herramientas de la llamada
│   │   └── prompts.py              # plantillas de objetivo por motivo de llamada
│   ├── tools/                      # [fase 2] herramientas del agente (§10.3)
│   │   ├── handler.py              # ToolCallHandler: instancia única; catálogo, permisos y ejecución
│   │   ├── context.py              # ToolContext: llamada, viaje, conductor y servicios (lo arma el handler)
│   │   ├── templates/              # una clase por plantilla
│   │   │   ├── base.py             # BaseToolTemplate
│   │   │   ├── consultar_viaje.py  # TemplateConsultarViaje
│   │   │   ├── registrar_novedad.py   # TemplateRegistrarNovedad
│   │   │   ├── enviar_whatsapp.py  # TemplateEnviarWhatsapp (una plantilla, muchas herramientas)
│   │   │   └── …                   # resto de plantillas de §10.4
│   │   └── mcp.py                  # [futuro] herramientas de servidores MCP (§10.3.6)
│   ├── scheduler.py                # bucle asyncio cada 60 s
│   └── cli.py                      # crear-usuario, seed-demo
├── alembic/ + alembic.ini
├── tests/
├── Dockerfile                      # ejecuta `alembic upgrade head` y luego uvicorn
├── pyproject.toml
└── .env.example
```

Capas: **routers** (HTTP) → **services** (reglas) → **integrations / llm / voice** (sistemas externos) y **models** (datos). Las dependencias van solo hacia abajo: un handler de LLM no conoce la base de datos y un router nunca llama a un SDK.

## 4. Arquitectura orientada a clases

### 4.1 Principios

1. **Clase base abstracta + clases hijas por implementación.** Cada punto donde hay, o habrá, más de una implementación se define con una clase base abstracta (`abc.ABC`) y una hija por proveedor.
2. **Método plantilla.** La clase base implementa el flujo común: reintentos, timeouts, logs, métricas y normalización. Las hijas solo implementan los pasos que cambian por proveedor (p. ej. `chat` y `stream_chat` en los handlers de LLM), así que el comportamiento transversal no se duplica.
3. **Tipos neutrales.** Entre capas solo viajan modelos propios (`Message`, `ToolCall`, `Etapa`, `Position`…), nunca objetos de un SDK.
4. **Registro por nombre.** Cada familia tiene un `Registry` y la implementación se elige por variable de entorno (`LLM_PROVIDER=anthropic`). Agregar un proveedor **no modifica código existente**.
5. **Sin herencia por herencia.** Routers, modelos y schemas siguen siendo funciones y clases planas. Las jerarquías se usan donde aportan extensibilidad (proveedores, handlers, herramientas, servicios), con un solo nivel de herencia salvo casos justificados como `RealtimeVoiceHandler`.

### 4.2 Familias de clases

| Familia | Clase base | Implementaciones | Fase |
|---|---|---|---|
| Servicios de negocio | `BaseService` | `AuthService`, `ViajeService`, `CuentaSatelitalService`, `MonitoreoService`, `LlamadaService` | 1 (llamadas: 2) |
| Callbacks del scraper | `CallbackHandler` | `PositionsCallbackHandler`, `VehiclesCallbackHandler` | 1 |
| Cliente satelital | `SatelliteClient` | `SatrackServiceClient` (más adelante, API oficial de Satrack u otro satelital) | 1 |
| Mensajería | `MessagingProvider` | `OpenWAProvider` (más adelante, `MetaWhatsAppProvider`) | WhatsApp |
| LLM | `ChatHandler` | `OpenAIChatHandler`, `AnthropicChatHandler`, `FakeChatHandler` (más adelante, `GeminiChatHandler`, `GrokChatHandler`) | 2 |
| Voz | `VoiceHandler` | `RealtimeVoiceHandler` → `OpenAIRealtimeHandler`; `PipelineVoiceHandler` | 2 |
| STT / TTS | `SpeechToText`, `TextToSpeech` | Una por proveedor elegido | 2 |
| Telefonía | `TelephonyProvider` | `TwilioProvider` (más adelante, SIP propio u otro operador) | 2 |
| Plantillas de herramientas | `BaseToolTemplate` | `TemplateConsultarViaje`, `TemplateRegistrarNovedad`, `TemplateEnviarWhatsapp`, … (§10.4) | 2 |

### 4.3 Contratos principales

| Clase base | Qué resuelve la clase base (común a todas las hijas) | Qué implementa cada hija |
|---|---|---|
| `Registry` | Registra implementaciones por nombre con un decorador y las crea a partir de la configuración; si el nombre no existe, falla al arrancar con un error claro | — (no se hereda) |
| `BaseService` | Sesión de BD, transportadora y usuario actuales; toda consulta filtra por transportadora (SEG-01); registro de eventos (SEG-03) | Las reglas de su dominio (viajes, cuenta satelital, monitoreo, llamadas) |
| `CallbackHandler` | Flujo del callback: idempotencia, estado de la cuenta (TEC-01 a TEC-06), eventos y transacción | Cómo procesar los datos de su tipo de job (`positions` o `vehicles`) |
| `SatelliteClient` | Reintentos, timeout y registro de la consulta | Cómo enviar el job a su servicio |
| `ChatHandler` | Estado de la conversación, armado del historial, ciclo de tool calls, etapas, uso de tokens, seudonimización y suspensiones (§11) | `chat` (sin streaming) y `stream_chat` (con streaming): traducir mensajes y herramientas al formato del proveedor, llamar a su SDK y devolver etapas neutrales |
| `VoiceHandler` | Ciclo de la llamada: abrir sesión, enrutar audio, límite de 2 min (CON-03), despachar tool calls al `ToolCallHandler` y cerrar | Cómo conectarse al modelo de voz y mover el audio |
| `TelephonyProvider` | Registro de estados y del id externo de la llamada | Marcar, validar la firma de sus webhooks, interpretar estados y adaptar su audio al formato neutral |
| `BaseToolTemplate` | Validación de argumentos, contexto inyectado, progreso, mensajes pendientes, reintentos solo si es idempotente (§10.3) | La acción concreta de la plantilla |

Las hijas nunca reimplementan el flujo común: solo los pasos que cambian por proveedor. Los SDKs de proveedores solo se importan dentro de su hija.

### 4.4 Cómo se agrega un proveedor nuevo (ej. Gemini)

1. Crear `app/llm/gemini_chat_handler.py` con `GeminiChatHandler`, hija de `ChatHandler`, e implementar `chat` y `stream_chat` (traducción de mensajes, herramientas y respuestas al formato de Gemini), y declarar sus capacidades (p. ej. si admite varias tool calls por turno).
2. Registrarla con el nombre `gemini` en el registro de handlers.
3. Agregar su SDK como extra en `pyproject.toml` y `GEMINI_API_KEY` en `.env.example`.
4. Pasar la **suite de contrato** (§15), que se ejecuta automáticamente sobre todos los handlers registrados.
5. Activarlo con `LLM_PROVIDER=gemini`.

No se toca ningún servicio, herramienta ni router. Igual para Grok, un nuevo operador de telefonía (`TelephonyProvider`) o un satelital distinto de Satrack (`SatelliteClient`).

## 5. Modelo de datos

Todas las fechas en UTC (`timestamptz`). Toda tabla de negocio lleva `transportadora_id` para el aislamiento (SEG-01).

### 5.1 Fase 1

| Tabla | Campos | Restricciones |
|---|---|---|
| `transportadoras` | id, nombre, nit, frecuencia_consulta_min (5), creado_en | — |
| `usuarios` | id, transportadora_id, usuario, nombre, password_hash, activo, creado_en | `usuario` único |
| `sesiones` | token_hash (PK), usuario_id, creado_en, expira_en | Se guarda el SHA-256 del token, nunca el token |
| `cuentas_satelitales` | id, transportadora_id, proveedor (`satrack`), usuario, password_cifrado, estado (`sin_verificar` / `ok` / `credenciales_invalidas` / `falla`), fallos_consecutivos, ultima_consulta_ok, ultimo_error, backoff_hasta | Una por transportadora y proveedor |
| `conductores` | id, transportadora_id, nombre, cedula, telefono, autoriza_contacto, autorizado_en | `UNIQUE(transportadora_id, cedula)` |
| `vehiculos` | id, transportadora_id, placa, propietario, en_satelital (null = sin verificar), ultima_posicion_id | `UNIQUE(transportadora_id, placa)` |
| `viajes` | id, transportadora_id, manifiesto, conductor_id, vehiculo_id, origen, destino, salida_estimada, llegada_estimada, peso_salida_kg, estado, motivo_cancelacion, creado_en, actualizado_en | `UNIQUE(transportadora_id, manifiesto)` (REG-01) |
| `remesas` | id, viaje_id, numero, cliente, peso_kg, cantidad | `UNIQUE(viaje_id, numero)` (REG-02) |
| `posiciones` | id, vehiculo_id, viaje_id (nullable), consulta_id, lat, lng, velocidad_kmh, direccion, estado_gps, reportado_en, reportado_texto, capturado_en | `UNIQUE(vehiculo_id, reportado_en)` evita duplicados; índice `(viaje_id, reportado_en)` |
| `consultas_satelitales` | job_id (UUID, PK), cuenta_satelital_id, tipo (`positions` / `vehicles`), placas (JSON), enviado_en, respondido_en, estado (`pendiente` / `ok` / `parcial` / `fallido` / `timeout`), error_codigo, error_detalle | — |
| `eventos` | id, transportadora_id, viaje_id, usuario_id, tipo, detalle (JSON), creado_en | Solo inserción (SEG-03) |

Notas:
- `peso_salida_kg` = suma de las remesas (REG-06), calculado al crear.
- `reportado_en`: hora del GPS si el scraper la pudo leer; si no, la hora de captura. El texto original queda en `reportado_texto`.
- `vehiculos.ultima_posicion_id` es solo un atajo para la vista de flota; la verdad está en `posiciones`.

### 5.2 Fase 2 (agente de voz)

| Tabla | Campos | Notas |
|---|---|---|
| `llamadas` | id, transportadora_id, viaje_id, conductor_id, motivo (`programada` / `detencion` / `sin_senal` / `rellamada` / `manual`), estado (`programada` / `marcando` / `en_curso` / `completada` / `no_contesta` / `fallida`), intento, programada_para, inicio, fin, duracion_s, proveedor_telefonia, id_externo, llm_proveedor, transcripcion, clasificacion, confianza, resumen, grabacion_path | `motivo` sale de CON-01, MON-02, MON-04 o del operador |
| `agentes` | id, transportadora_id (null = global), nombre (`llamada_programada`, `llamada_detencion`, …), prompt, herramientas_habilitadas (lista), proveedor_llm, modelo, activo | Perfil del agente por motivo: qué sabe hacer cada uno es **configuración**, no código |
| `herramientas` | id, nombre, descripcion, parametros (JSON Schema), plantilla, configuracion (JSON), efecto (`lectura` / `accion`), idempotente, max_por_llamada, activa, actualizado_en | Catálogo de herramientas que ve el modelo (§10.3) |
| `conversaciones` | id, transportadora_id, viaje_id, canal (`llamada` / `whatsapp`), llamada_id, agente_id, estado (`activa` / `suspendida` / `cerrada`), creado_en | Una por llamada o hilo de WhatsApp |
| `turnos` | id, conversacion_id, orden, rol (`usuario` / `asistente`), contenido, tokens_entrada, tokens_salida, creado_en | Historial que el `ChatHandler` reconstruye en cada turno (§11) |
| `tool_calls` | id, turno_id, llamada_id, herramienta, argumentos (JSON), resultado (JSON), estado (`ok` / `rechazada` / `error` / `suspendida`), motivo_rechazo, orden, creado_en | Auditoría de **cada** acción del agente; solo inserción. `suspendida` es un estado propio, no se disfraza de `ok` |
| `suspensiones` | id, tool_call_id, conversacion_id, espera_a (`coordinador` / …), payload (JSON), estado (`pendiente` / `resuelta` / `vencida`), vence_en, resuelta_por, resultado | Pausas del agente esperando a una persona (§11.6) |
| `novedades` | id, transportadora_id, viaje_id, tipo (`sin_novedad` / `retraso` / `averia` / `accidente` / `problema_carga` / `otro`), descripcion, origen (`llamada` / `whatsapp` / `operador`), llamada_id, creado_en | Las clasificaciones de CON-05 |
| `viajes` | + eta_reportada, eta_reportada_en | La ETA que reporta el conductor no reemplaza la llegada pactada |

### 5.3 Estados del viaje en el MVP

```
registrado ──▶ programado ──▶ en_ruta ──▶ entregado
     └────────────┴──────────────┴──────▶ cancelado (motivo obligatorio)
```

| Transición | Disparador en el MVP |
|---|---|
| registrado → programado | Automática cuando la placa se confirma en Satrack (REG-08) |
| programado → en_ruta | Manual ("Iniciar ruta"). La geocerca de origen llega con PostGIS |
| en_ruta → entregado | Manual ("Marcar entregado"). MON-05 llega con el motor de reglas |
| cualquiera antes de entregado → cancelado | Manual con motivo (EST-01) |

Los estados `con_novedad`, `cumplido_pendiente`, `cumplido_rndc` y `cerrado` ya existen en el enum pero aún no tienen transiciones. Toda transición crea un `evento` con usuario y motivo (EST-02). **El agente de voz no puede cambiar estados** (§10.5).

## 6. Autenticación (mínima)

1. Los usuarios se crean por CLI: `python -m app.cli crear-usuario --transportadora "Transportes X" --usuario marcos`. No hay registro público.
2. `POST /api/auth/login {usuario, password}` → `AuthService` verifica bcrypt y genera un **token opaco aleatorio** (32 bytes). Se guarda su SHA-256 en `sesiones` con vencimiento de 7 días.
3. El frontend envía `Authorization: Bearer <token>` en cada petición.
4. `get_current_user` busca el hash, valida que no esté vencido y devuelve el usuario con su `transportadora_id`.
5. `POST /api/auth/logout` borra la sesión.

**Por qué un token opaco y no JWT:** es igual de simple de implementar, se puede revocar borrando la fila (logout real) y evita manejar firmas, expiración en el cliente o refresh tokens. Respuesta `401` genérica ("Usuario o contraseña incorrectos") para no revelar qué usuarios existen.

## 7. Endpoints

Prefijo `/api` (lo que expone nginx al navegador). Las rutas internas viven fuera de ese prefijo:
- `/internal/satrack/callback`: nginx **no** la publica; solo la alcanza el `satrack-service` dentro de la red de docker.
- `/internal/voz/*` (fase 2): nginx **sí** la publica, porque el proveedor de telefonía llama desde internet, pero cada petición se valida con la firma del proveedor (`TelephonyProvider.verify_webhook`).

Todos los endpoints requieren sesión salvo login, health y las rutas internas. Todo filtra por la transportadora del usuario.

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/auth/login` | `{usuario, password}` → `{token, usuario}` |
| POST | `/auth/logout` | Cierra la sesión |
| GET | `/auth/me` | Usuario actual y transportadora |
| GET | `/panel` | Conteo de viajes por estado, estado de la cuenta Satrack, última consulta OK, vehículos con posición |
| GET | `/viajes?estado=&q=` | Lista paginada; `q` busca por manifiesto, placa o conductor |
| POST | `/viajes` | Crea el viaje con conductor, vehículo y remesas (ver §8) |
| GET | `/viajes/{id}` | Detalle: remesas, conductor, vehículo, última posición, eventos |
| GET | `/viajes/{id}/posiciones` | Recorrido del viaje (para la línea en el mapa) |
| POST | `/viajes/{id}/transiciones` | `{estado, motivo?}` |
| GET | `/vehiculos` | Flota con última posición y `en_satelital` |
| GET | `/conductores` | Para autocompletar en el formulario |
| GET | `/cuenta-satelital` | Usuario, estado, último error. **Nunca** la contraseña |
| PUT | `/cuenta-satelital` | `{usuario, password}`: guarda cifrado y lanza un job `vehicles` para verificar |
| POST | `/cuenta-satelital/sincronizar` | Relanza la verificación de placas |
| POST | `/internal/satrack/callback` *(sin `/api`)* | Callback del scraper (firma HMAC, sin sesión) |
| GET | `/health` | Estado de la API y la BD |
| **Fase 2** | | |
| GET | `/viajes/{id}/llamadas` | Llamadas del viaje con transcripción, clasificación y acciones ejecutadas |
| POST | `/viajes/{id}/llamar` | Llamada manual del operador (respeta REG-11 y CON-08) |
| POST | `/internal/voz/{proveedor}/estado` *(sin `/api`)* | Webhook de estado de la llamada (contestó, no contestó, colgó) |
| WS | `/internal/voz/{proveedor}/stream/{llamada_id}` *(sin `/api`)* | Audio en tiempo real entre telefonía y el `VoiceHandler` |

**Formato de errores**: `{"detail": "mensaje en español"}`. Los errores de validación devuelven `422` con `{"detail": "...", "errores": [{"campo": "conductor.telefono", "mensaje": "..."}]}` para que el frontend marque cada campo.

## 8. Registro de viajes

`POST /api/viajes` recibe todo en un solo formulario (como lo describe IDEA.md) y lo procesa `ViajeService.crear()`:

```json
{
  "manifiesto": "12345",
  "origen": "Bogotá", "destino": "Cali",
  "salida_estimada": "2026-10-06T06:00:00-05:00",
  "llegada_estimada": "2026-10-06T18:00:00-05:00",
  "conductor": { "nombre": "Juan Pérez", "cedula": "1012345678", "telefono": "3001234567", "autoriza_contacto": true },
  "vehiculo": { "placa": "abc-123", "propietario": "Pedro Gómez" },
  "remesas": [{ "numero": "R-001", "cliente": "Almacenes X", "peso_kg": 12000, "cantidad": 300 }]
}
```

Validaciones:
- **En el schema:** placa `AAA999` normalizada (REG-03), cédula de 6–10 dígitos (REG-04), celular de 10 dígitos que empiece por 3 → `+57…` (REG-05), peso > 0 (REG-06), origen ≠ destino y llegada > salida (REG-07), al menos una remesa sin números repetidos (REG-02).
- **En el servicio:** manifiesto único (REG-01); el vehículo y el conductor no tienen otro viaje activo (REG-09, REG-10).
- Conductor y vehículo se **reutilizan por cédula y placa** (se actualizan nombre, teléfono y propietario si cambiaron).
- **REG-08:** si la placa ya está verificada en Satrack, el viaje nace `programado`; si no, nace `registrado` y se lanza un job `vehicles`. Sin cuenta Satrack, queda `registrado` y la bandeja pide configurarla.
- **REG-11:** se guarda `autoriza_contacto` y su fecha. Sin autorización, el agente de voz nunca llama a ese conductor.

## 9. Integración con el `satrack-service`

Sigue el contrato de [IMPLEMENTACION.md §2–§3](../IMPLEMENTACION.md#3-lado-del-monolito): request + callback HTTP, sin colas. El backend solo habla con él a través de `SatelliteClient` (implementación `SatrackServiceClient`).

### 9.1 Envío de un job

1. Crear la fila en `consultas_satelitales` en `pendiente` y **hacer commit antes de enviar** (el simulador responde tan rápido que el callback puede llegar antes de que termine la petición).
2. `SatrackServiceClient.enviar_job()` → `POST {SATRACK_SERVICE_URL}/v1/jobs` con `X-Api-Key` y la contraseña descifrada solo en memoria.
3. Si el servicio no responde o devuelve error → consulta `fallido` con `SERVICE_UNAVAILABLE` y cuenta como fallo técnico.

### 9.2 Scheduler (cada 60 s): `MonitoreoService.tick()`

1. **Timeouts:** consultas `pendiente` con más de 3 min pasan a `timeout` y suman un fallo a la cuenta.
2. **Cuentas a consultar** (FRE-01 a FRE-04): estado distinto de `credenciales_invalidas`, sin `backoff_hasta` vigente, sin consulta pendiente y con la última consulta enviada hace más de `frecuencia_consulta_min`.
3. **Placas activas** de cada cuenta: viajes `en_ruta`, o `programado` desde 1 h antes de la salida (FRE-02). Si no hay placas, no se consulta.
4. Un job `positions` por cuenta con todas sus placas.
5. **[Fase 2]** `LlamadaService.programar_pendientes()`: decide qué llamadas tocan según CON-01, CON-02, CON-08 y CON-09 (ver §10.2).

Corre en el mismo proceso que la API, por lo que se despliega **con un solo worker** de uvicorn. Si más adelante se escala la API, el scheduler pasa a un proceso propio (`SCHEDULER_ENABLED=false` en las réplicas).

### 9.3 Callback `POST /internal/satrack/callback`

1. Validar `X-Signature` (HMAC-SHA256 del body crudo con `CALLBACK_SECRET`, comparación en tiempo constante) → `401` si no coincide.
2. Buscar la consulta por `job_id`. Si ya tiene `respondido_en` → `200` sin hacer nada (idempotencia). Si llegó después del timeout, se procesa igual: las posiciones siguen siendo válidas.
3. Elegir el `CallbackHandler` según `payload.type` (registro por tipo de job):
   - **`PositionsCallbackHandler`:** por cada posición, buscar el vehículo por placa dentro de la transportadora; insertar ignorando duplicados por `(vehiculo_id, reportado_en)`; asociar el viaje activo; actualizar `ultima_posicion_id` si es más reciente.
   - **`VehiclesCallbackHandler`:** marcar `en_satelital` en las placas registradas y pasar a `programado` los viajes `registrado` cuya placa quedó verificada (con evento).
4. **Estado de la cuenta**, común a ambos en la clase base (TEC-01, TEC-04, TEC-05, TEC-06):
   - `ok` / `partial` → `fallos_consecutivos = 0`, `ultima_consulta_ok = ahora`, estado `ok`.
   - `AUTH_FAILED` → `credenciales_invalidas` y se deja de consultar hasta que el usuario actualice la contraseña.
   - `CAPTCHA_REQUIRED` / `PROVIDER_CHANGED` → `backoff_hasta = ahora + 15 min`.
   - Otros fallos → `fallos_consecutivos += 1`; con 3 seguidos, estado `falla`.
   - `VEHICLE_NOT_FOUND` → `en_satelital = false` y evento en el viaje.
5. Responder `200`. Todo en una transacción: si algo falla se responde `500` y el scraper reintenta.

## 10. Fase 2 — Agente de voz con tool calls

### 10.1 Arquitectura

```
Scheduler / operador
   │  MonitoreoService decide CUÁNDO llamar (código determinístico: CON-01, CON-02, CON-08, CON-09, MON-02, MON-04)
   ▼
LlamadaService ── crea la fila `llamadas` y pide la llamada ──▶ TelephonyProvider.place_call()  (TwilioProvider)
   │                                                                     │
   │                                                    el conductor contesta; audio por WebSocket
   ▼                                                                     ▼
VoiceAgent ── arma objetivo + contexto + herramientas ──▶ VoiceHandler.run()
                                                          ├─ RealtimeVoiceHandler (speech-to-speech, p. ej. OpenAIRealtimeHandler)
                                                          └─ PipelineVoiceHandler (STT → ChatHandler → TTS: OpenAI, Anthropic, Gemini…)
                                                                     │
                                                       tool calls neutrales (ToolCall)
                                                                     ▼
                                                          ToolCallHandler ── permite, valida, ejecuta y audita ──▶ BD / OpenWA / alertas
                                                                     │
                                                          resultado de la herramienta → de vuelta al modelo
   ▼
LlamadaService.procesar_resultado() ── aplica CON-04, CON-06, CON-07 (código) ──▶ novedades, alertas, rellamadas
```

- **Dos modos de voz** detrás de `VoiceHandler`, elegidos con `VOICE_MODE`:
  - `realtime`: un modelo speech-to-speech; menor latencia.
  - `pipeline`: STT + cualquier `ChatHandler` con tool calling + TTS. Así **Anthropic, Gemini o Grok pueden llevar la llamada** aunque no ofrezcan voz nativa, y se reutilizan los mismos handlers de texto.
- `VoiceAgent` no depende del proveedor: carga el perfil de `agentes` según el motivo de la llamada (prompt y herramientas habilitadas) y recibe un `VoiceHandler` ya construido.

### 10.2 Quién decide qué (SEG-07)

| Decisión | La toma | Regla |
|---|---|---|
| Cuándo llamar | Código (`LlamadaService`) | CON-01, CON-02, CON-08, CON-09; nunca sin autorización (REG-11) |
| Qué preguntar y cómo conversar | Agente (prompt con objetivo y contexto) | Máx. 3 preguntas y 2 min (CON-03) |
| Qué acción ejecutar durante la llamada | **Agente, mediante tool calls** | Solo herramientas registradas y con los límites de §10.4 |
| Si la acción es válida | Código (`ToolCallHandler` + la plantilla) | Habilitada para ese agente, esquema, viaje activo, límites, frecuencia |
| Severidad de la alerta | Código | CON-07: accidente o problema con la carga → alta; avería → media; retraso → baja |
| Qué pasa si no contesta | Código | CON-04: reintento a los 10 min → WhatsApp → alerta tras 2 intentos |

El agente tiene **poderes reales** (ejecuta acciones en el sistema), pero cada poder es una herramienta acotada y auditada; no hay herramientas para cambiar estados ni para tocar el RNDC.

### 10.3 Herramientas: `ToolCallHandler` y plantillas

Como el proceso va a necesitar **muchas herramientas**, se separa lo que es configuración de lo que es código. El diseño sigue un `ToolCallHandler` que el equipo ya usa en otro proyecto, adaptado a Rumboo.

#### 10.3.1 Dos niveles: herramienta y plantilla

- **Plantilla** (código): una clase hija de `BaseToolTemplate` que sabe hacer **un tipo de acción**: consultar el viaje, registrar una novedad, enviar un WhatsApp.
- **Herramienta** (configuración, tabla `herramientas`): lo que ve el modelo, es decir nombre, descripción y esquema de parámetros. Indica qué plantilla la ejecuta y con qué configuración.
- **Una plantilla puede servir a muchas herramientas.** Por ejemplo, `TemplateEnviarWhatsapp` respalda `pedir_foto_cumplido`, `enviar_ubicacion_entrega` y `confirmar_rellamada`. Cada una es una fila con su texto aprobado y su descripción, **sin escribir código nuevo**.
- Así se cumple la regla de diseño de IDEA.md: "cada transportadora es configuración, no código". Una transportadora puede tener su propia variante de una herramienta.

#### 10.3.2 Perfil del agente y lista de herramientas habilitadas

Cada conversación nace de un perfil de `agentes` (p. ej. `llamada_programada` o `llamada_detencion`) con su prompt y su **lista de herramientas habilitadas**. El modelo solo recibe esas herramientas y, al ejecutar, se vuelve a verificar que la herramienta pedida esté en la lista. Un modelo que "inventa" el nombre de otra herramienta recibe un rechazo, aunque esa herramienta exista en el catálogo.

#### 10.3.3 Responsabilidades del `ToolCallHandler`

Existe **una sola instancia** en el proceso, creada al arrancar la API. No guarda estado de ninguna conversación, solo cachés.

1. **Preparar las herramientas de un turno:**
   - Recibe la lista habilitada del agente y devuelve sus definiciones en formato neutral; cada `ChatHandler` las traduce a su proveedor.
   - Usa un **caché** de definiciones para no leer la BD en cada turno. Si una herramienta de la lista no existe o está inactiva, falla de inmediato con un error claro.
2. **Ejecutar una tool call:**
   1. Verifica que esté habilitada para ese agente. Si no, la rechaza.
   2. Interpreta los argumentos: si vienen vacíos se toman como objeto vacío; si no son JSON válido, la rechaza con el motivo.
   3. Busca la plantilla en el **registro de plantillas** y crea **una instancia nueva por ejecución**, para que no haya estado compartido entre llamadas.
   4. Inyecta en la instancia:
      - el **contexto**: llamada, viaje, conductor y servicios, ya filtrados por transportadora;
      - un canal de **progreso**;
      - un canal de **mensajes pendientes**.
   5. Ejecuta y normaliza el resultado a un texto corto en español.
   6. Registra la fila en `tool_calls` y un evento en el viaje.
3. **Reintentos con backoff, pero solo si es seguro:**
   - Las herramientas de lectura y las marcadas `idempotente` se reintentan.
   - Las acciones como enviar un WhatsApp o escalar al coordinador **no** se reintentan a ciegas: usan el id de la tool call como llave de idempotencia para no duplicar el efecto.

#### 10.3.4 Qué recibe cada plantilla

- **Argumentos ya validados** contra el esquema de la herramienta.
- **Su configuración**: el texto de la plantilla de WhatsApp, límites y destinatarios.
- **El contexto inyectado.** El viaje, el conductor y la transportadora **salen de la llamada, nunca de los argumentos del modelo**. Aunque el conductor diga "revisa el viaje 999" o intente manipular al agente, la plantilla solo puede actuar sobre el viaje de esa conversación.
- **El canal de progreso**, para informar avances ("buscando la última posición…"). Durante la llamada, el agente lo usa para decir una frase de espera.
- **El canal de mensajes pendientes**, para dejar preparado un mensaje que debe ir después de los resultados del turno (p. ej. la imagen del cumplido para que el modelo la vea).
- **Contexto de ejecución:** profundidad y pila de agentes, por si la plantilla invoca a otro agente (§11.7).

#### 10.3.5 Agregar una herramienta

- **Si ya existe una plantilla que la cubre:** se inserta una fila en `herramientas`, se agrega su nombre a la lista del agente y queda disponible. No hay despliegue.
- **Si es un tipo de acción nuevo:** se crea una clase hija de `BaseToolTemplate`, se registra con su nombre en el registro de plantillas y después se crean las herramientas que la usan. A diferencia de la referencia, donde el diccionario de plantillas está escrito dentro del handler, aquí **el handler no se modifica**: las plantillas se registran solas.
- **Caché:** a diferencia de la referencia, que nunca lo invalida, aquí se invalida al editar una herramienta o tras `TOOL_CATALOG_CACHE_S`.

#### 10.3.6 Herramientas externas (MCP, futuro)

El mismo handler podrá exponer herramientas de servidores MCP, por ejemplo un ERP de la transportadora o un servicio del RNDC:
- Se nombran `servidor__herramienta` para distinguirlas de las propias.
- Se habilitan por servidor en el perfil del agente y su definición se cachea.
- Si fallan, devuelven al modelo un resultado de error en lugar de cortar el turno.

No entra en el MVP de voz; el diseño lo permite sin cambiar el `ChatHandler`.

### 10.4 Herramientas del MVP de voz

| Herramienta | Plantilla | Efecto | Qué hace | Límites (código) |
|---|---|---|---|---|
| `consultar_viaje` | `TemplateConsultarViaje` | lectura | Origen, destino, llegada pactada, última posición, novedades abiertas | Solo el viaje de la conversación |
| `registrar_novedad` | `TemplateRegistrarNovedad` | acción | Crea la `novedad`; el código asigna la severidad y crea la alerta (CON-07) | `tipo` de un enum cerrado |
| `actualizar_eta` | `TemplateActualizarEta` | acción | Guarda `eta_reportada` (no cambia la llegada pactada) | Entre ahora y +72 h |
| `programar_rellamada` | `TemplateProgramarRellamada` | acción | Agenda otra llamada | 10–180 min; respeta CON-08; máx. 1 por llamada |
| `pedir_foto_cumplido`, `enviar_ubicacion_entrega`, … | `TemplateEnviarWhatsapp` | acción | Envía un mensaje aprobado por `MessagingProvider`; cada herramienta es una fila con su texto | WA-01 y WA-05; idempotente por tool call |
| `escalar_a_coordinador` | `TemplateEscalarCoordinador` | acción | Notifica al coordinador con el resumen y el enlace; puede **suspender** al agente esperando su decisión (§11.6) | Máx. 1 por llamada |
| `finalizar_llamada` | `TemplateFinalizarLlamada` | acción | Cierra la conversación con la clasificación de CON-05 | **Obligatoria**; si la confianza es menor al umbral → `otro` y revisión humana (CON-06) |

Todos los `ChatHandler` exponen estas herramientas al modelo en el formato de su proveedor, sin cambios.

### 10.5 Lo que el agente NO puede hacer

No existen herramientas para: cambiar el estado del viaje, cancelar, aprobar cumplidos, transmitir al RNDC, modificar datos del conductor o del vehículo, consultar otros viajes ni llamar a otros números. Esas acciones siguen siendo humanas o de reglas (EST-01, CUM-11).

### 10.6 Ciclo de una llamada

1. `LlamadaService` crea `llamadas` en `programada` y llama a `TelephonyProvider.place_call()` → `marcando`.
2. El proveedor avisa por webhook: si no contesta → `no_contesta` y se aplica CON-04. Si contesta → abre el WebSocket de audio → `en_curso`.
3. `VoiceAgent` crea la `conversacion`, carga el perfil del agente según el motivo (prompt y herramientas habilitadas), agrega el contexto del viaje y ejecuta el `VoiceHandler`.
4. Cada tool call pasa por el `ToolCallHandler` y su resultado vuelve al modelo; cada turno se guarda en `turnos` (§11.3).
5. Al terminar (por `finalizar_llamada`, porque cuelgan o por el límite de 2 min) se guarda la transcripción y el resultado → `completada`.
6. `LlamadaService.procesar_resultado()`: si el agente no llamó `finalizar_llamada`, se clasifica la transcripción con un `ChatHandler` sin herramientas como respaldo; luego se aplican CON-06 y CON-07.

## 11. Motor de conversación del agente (patrón `ChatHandler`)

El agente de voz, y después el de WhatsApp, se apoya en una clase base `ChatHandler` que concentra todo lo que no depende del proveedor. Cada hija (`OpenAIChatHandler`, `AnthropicChatHandler`, `GeminiChatHandler`…) solo sabe hablar con su API. El diseño sigue un `ChatHandler` que el equipo ya usa en otro proyecto, adaptado a Rumboo.

### 11.1 Estado que guarda un handler

Se crea **un handler por conversación en curso** (nunca compartido entre peticiones) y guarda:

| Estado | Para qué |
|---|---|
| Historial de la sesión | Turnos anteriores de la conversación: lo que dijo el conductor, lo que respondió el agente y las herramientas que usó con sus resultados |
| Prompt de sistema | Objetivo y reglas del agente, del perfil en `agentes` más el contexto del viaje |
| Entrada actual | Lo último que dijo o escribió el conductor |
| Respuesta en curso | El texto que el modelo va generando en este turno |
| Tool calls del turno | Las herramientas pedidas en este turno, con su estado y resultado |
| Respuestas guardadas | Los turnos cerrados de esta ejecución, listos para persistirse en `turnos` |
| Uso de tokens | Consumo del turno, para medir el costo por llamada (riesgo 5 de IDEA.md) |
| Contexto de ejecución | Profundidad y pila de agentes, para limitar agentes anidados (§11.7) |

### 11.2 Qué hace la clase base y qué la hija

| Clase base `ChatHandler` | Clase hija (por proveedor) |
|---|---|
| Reconstruye la lista de mensajes desde el historial: sistema, usuario (texto o imagen), asistente con sus tool calls, resultados de herramientas y respuesta final | Traduce esa lista neutral al formato de su API |
| Ejecuta las tool calls del turno a través del `ToolCallHandler` y ordena sus resultados | Declara si su proveedor puede pedir **varias tool calls en un mismo turno** |
| Procesa las **etapas** de la respuesta: texto, uso de tokens y tool calls | Convierte la respuesta (o el stream) de su SDK en esas etapas neutrales |
| Guarda cada turno como una respuesta (texto + tool calls) y lo deja listo para persistir | Implementa `chat` (sin streaming) y `stream_chat` (con streaming) |
| Seudonimiza y restaura datos personales (§11.8) | Puede sobrescribir una etapa propia de su proveedor; la base la rechaza por defecto para que no se use donde no aplica |
| Gestiona las suspensiones (§11.6) | — |

### 11.3 Ciclo de un turno

1. La base arma los mensajes desde el historial y les agrega la entrada actual.
2. La hija llama al modelo con los mensajes y las herramientas habilitadas.
3. La respuesta llega como etapas: fragmentos de texto, uso de tokens y tool calls.
4. Si hay tool calls, se ejecutan como un **lote** (§11.4).
5. Los resultados se agregan a la conversación **en el orden en que el modelo los pidió**, no en el orden en que terminaron. Se agregan en dos pasadas:
   - primero todos los resultados de herramientas, seguidos y sin nada en medio, porque OpenAI y Anthropic lo exigen;
   - después los mensajes pendientes que alguna plantilla haya dejado preparados (p. ej. una imagen).
6. Se vuelve a llamar al modelo con los resultados. Esto se repite hasta que responde sin pedir herramientas o se llega a `AGENT_MAX_TURNS`.
7. Cada vuelta se guarda como un turno: si ya había texto cuando llegan nuevas tool calls, ese texto se cierra como una respuesta propia.

### 11.4 Ejecución de herramientas en lote

- Cada tool call del lote se ejecuta a través del `ToolCallHandler` (§10.3), y su resultado se normaliza a texto para que todos los proveedores lo reciban igual.
- **Paralelo solo cuando todos están de acuerdo:**
  - el modelo pidió varias;
  - el proveedor admite varias por turno;
  - el canal puede guardar suspensiones;
  - la bandera `TOOL_CALL_PARALLEL_ENABLED` está activa.

  Rumboo agrega una quinta condición: **todas las del lote son de lectura**. Por defecto se ejecutan en secuencia.
- Si una herramienta falla por un error de negocio (argumentos inválidos, límite superado), el error vuelve al modelo como resultado para que corrija o se lo explique al conductor. Si falla por un error del sistema, se corta el turno y se registra.

### 11.5 Streaming y etapas

- Con streaming, la base emite cada etapa a medida que llega. Las tool calls pasan por los estados **ejecutando → progreso → completada / fallida**.
- **Uso en la voz (modo `pipeline`):**
  - el texto se envía al TTS mientras se genera, así el conductor no espera la respuesta completa;
  - mientras una herramienta está "ejecutando", el agente dice una frase de espera ("Dame un momento, lo reviso").
- **Uso en la bandeja (futuro):** el operador podría ver en vivo la conversación y las acciones del agente.
- **Si el consumidor se va** (el conductor cuelga), el lote en curso termina igual y sus resultados se registran. No quedan acciones a medias sin auditar.
- Los errores que lleguen a un cliente se **sanean** desde el inicio (en la referencia es trabajo pendiente).

### 11.6 Suspensiones (humano en el loop)

- **Qué es:** una herramienta puede **pausar al agente** cuando necesita algo que no está disponible en ese momento, típicamente una decisión del coordinador ("¿autorizo que espere al cliente hasta mañana?").
- **Qué se guarda:** la suspensión va en `suspensiones` con la herramienta, sus argumentos y a quién se espera. Si varias herramientas del mismo turno se suspenden, se agrupan en una sola espera.
- **Reanudación:** cuando llega la respuesta, la conversación continúa como si la herramienta hubiera terminado con ese resultado. Si nadie responde antes de `vence_en`, la suspensión **vence** y el agente sigue con un resultado por defecto.
- **Quién puede suspender:** solo se permite si el canal puede guardar suspensiones. Esa capacidad la fija la fábrica al crear el handler y no viaja en los parámetros de la petición, así una herramienta no puede "otorgársela".
- **En una llamada:** no se puede dejar al conductor en línea minutos. El agente avisa ("el coordinador te devuelve la llamada o te escribe") y la conversación se reanuda por WhatsApp o en una rellamada.
- **Más adelante**, sirve para los cumplidos con diferencias que necesitan aprobación (CUM-10, CUM-11).

### 11.7 Agentes anidados

- Un agente puede usar a otro como herramienta; por ejemplo, el agente de la llamada le pide a un "lector de cumplidos" con visión que revise una foto.
- El contexto de ejecución lleva la **pila de agentes y la profundidad** para impedir ciclos y limitar el anidamiento (`AGENT_MAX_DEPTH`, por defecto 2).
- No se necesita en el primer agente de voz, pero queda soportado.

### 11.8 Datos personales: seudonimización (Ley 1581)

- **Antes de enviar texto al proveedor**, los nombres, cédulas, teléfonos y placas se reemplazan por marcadores. Al recibir la respuesta se restauran.
- **En streaming**, un búfer retiene el texto hasta tener el marcador completo antes de restaurarlo, para no enviar al TTS ni al cliente un marcador partido.
- Se activa por transportadora (`PII_SEUDONIMIZAR`). Sin sesión de seudonimización, el texto pasa igual.
- **Limitación:** en modo `realtime` (audio directo) la voz no se puede seudonimizar. Se minimiza el contexto enviado (sin cédula ni teléfono) y se usa el modo `pipeline` cuando la transportadora lo exija.

### 11.9 Fábrica

`ChatHandlerFactory`:
- elige la hija según el proveedor del perfil del agente (o `LLM_PROVIDER`);
- la crea con el historial, el prompt y el contexto de ejecución;
- fija sus **capacidades del canal**: si puede guardar suspensiones y si se seudonimiza.

El resto del sistema solo pide "un handler para esta conversación".

### 11.10 Qué se adopta de la referencia y qué se ajusta

| Se adopta | Se ajusta en Rumboo |
|---|---|
| Clase base con el estado y el ciclo; hijas solo con `chat` y `stream_chat` | Un handler por conversación, nunca compartido |
| Ejecutor central de herramientas de instancia única con caché | El caché se invalida al editar herramientas |
| Herramientas como configuración + plantillas de código | Las plantillas se registran solas; el handler no tiene un diccionario fijo |
| Lista de herramientas habilitadas verificada al ejecutar | Además, el contexto (viaje, conductor) siempre se inyecta, nunca lo elige el modelo |
| Orden de resultados en dos pasadas | Igual |
| Paralelo con cuatro condiciones | Quinta condición: solo herramientas de lectura |
| Reintentos con backoff | Solo para herramientas idempotentes o con llave de idempotencia |
| Suspensiones agregadas por turno | `suspendida` es un estado real en `tool_calls`, con vencimiento |
| Seudonimización con búfer en streaming | Obligatoria según la configuración de la transportadora (Ley 1581) |
| Errores de herramientas visibles para el cliente | Se sanean siempre |

## 12. Configuración

| Variable | Ejemplo | Uso |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg://rumboo:rumboo@db:5432/rumboo` | Conexión |
| `SECRET_KEY` | aleatoria | Deriva la llave Fernet para la contraseña de Satrack |
| `SATRACK_SERVICE_URL` | `http://satrack:8080` | Microservicio |
| `SATRACK_SERVICE_API_KEY` | aleatoria | Igual que en el scraper |
| `CALLBACK_SECRET` | aleatoria | Igual que en el scraper |
| `CORS_ORIGINS` | `http://localhost:5173` | Solo para desarrollo sin proxy |
| `SESSION_DAYS` | `7` | Vida del token |
| `SCHEDULER_ENABLED` / `SCHEDULER_INTERVAL_S` | `true` / `60` | Scheduler |
| `CONSULTA_TIMEOUT_S` | `180` | Timeout de consultas pendientes |
| **Fase 2** | | |
| `LLM_PROVIDER` / `LLM_MODEL` | `anthropic` / *(modelo vigente del proveedor)* | Handler de texto (clasificación, modo `pipeline`) |
| `VOICE_MODE` / `VOICE_PROVIDER` | `realtime` / `openai` | Modo y handler de voz |
| `TELEPHONY_PROVIDER` | `twilio` | Operador de telefonía |
| `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER` | — | Credenciales; solo las del proveedor activo son obligatorias |
| `PUBLIC_BASE_URL` | `https://rumboo.example.com` | URL pública para los webhooks de telefonía |
| `CALL_MAX_SECONDS` / `CLASIFICACION_CONFIANZA_MIN` | `120` / `0.7` | CON-03 y CON-06 |
| `AGENT_MAX_TURNS` / `AGENT_MAX_DEPTH` | `8` / `2` | Vueltas modelo ↔ herramientas por entrada y anidamiento de agentes |
| `TOOL_CALL_PARALLEL_ENABLED` | `false` | Permite lotes en paralelo (§11.4) |
| `TOOL_CATALOG_CACHE_S` | `300` | Vida del caché de definiciones de herramientas |
| `PII_SEUDONIMIZAR` | `true` | Valor por defecto; cada transportadora puede exigirlo |

`config.py` valida al arrancar que el proveedor elegido esté registrado y que existan sus credenciales; si no, el servicio no arranca y explica qué falta.

## 13. Despliegue y desarrollo (docker compose en la raíz)

| Servicio | Imagen | Puerto | Notas |
|---|---|---|---|
| `db` | postgres:16-alpine | interno | Volumen `pg_data` |
| `satrack` | build `./satrack-service` | interno | `PROVIDER=simulator` por defecto en desarrollo |
| `api` | build `./backend` | 8000 | Migra al arrancar; un worker |
| `web` | build `./web` (nginx) | 8080 | Sirve el build y hace proxy de `/api` (y de `/internal/voz/` en fase 2) a `api` |

`python -m app.cli seed-demo` crea una transportadora de demo, un usuario y viajes con placas del simulador, para ver el monitoreo funcionando sin Satrack real. Las credenciales de demo quedan en `.env.example`.

En desarrollo de la fase 2, la telefonía necesita alcanzar `PUBLIC_BASE_URL`: se usa un túnel (p. ej. ngrok o cloudflared). Con `LLM_PROVIDER=fake` y `TELEPHONY_PROVIDER=fake` se prueba el flujo completo sin llamadas reales.

## 14. Errores y robustez

| Situación | Comportamiento |
|---|---|
| Scraper caído | La consulta queda `fallido`; el scheduler reintenta en el siguiente ciclo según la frecuencia |
| Callback que nunca llega | Timeout a los 3 min; no bloquea la cuenta para siempre |
| Callback duplicado | Idempotente por `job_id` y por `UNIQUE(vehiculo_id, reportado_en)` |
| Posición de una placa desconocida | Se ignora y se registra en el log |
| Violación de unicidad al crear un viaje (carrera) | `409` con mensaje claro |
| Error inesperado | `500` genérico; el detalle va al log, nunca al cliente |
| **Fase 2** | |
| Proveedor de LLM caído o lento | Reintentos y timeout en `ChatHandler`. Opcional: `LLM_FALLBACK_PROVIDER` (un handler que envuelve a otros dos) |
| Falla la voz antes de conversar | Se trata como no contestada → CON-04 (reintento y WhatsApp) |
| La llamada se corta a mitad | Se guarda lo transcrito y se clasifica como respaldo (§10.6) |
| El modelo pide una herramienta inexistente, no habilitada para su agente o con argumentos inválidos | `rechazada` con motivo; el modelo puede corregir. Todo queda en `tool_calls` |
| Una acción falla a mitad (p. ej. OpenWA no responde) | No se reintenta a ciegas: llave de idempotencia por tool call; el agente informa que no se pudo |
| Suspensión sin respuesta | Vence en `vence_en` y el agente continúa con el resultado por defecto |
| Bucle de tool calls | `max_por_llamada` por herramienta, `AGENT_MAX_TURNS` por entrada y tope global de 10 por llamada |
| Webhook de telefonía sin firma válida | `401`, se registra y no se procesa |

## 15. Pruebas

`pytest` contra un Postgres de prueba (servicio `db` de compose) y `httpx` con el cliente de FastAPI:
- Auth: login correcto e incorrecto, token vencido, logout.
- Aislamiento: un usuario no ve viajes de otra transportadora (`BaseService._query`).
- Registro: cada validación REG con su mensaje, reutilización de conductor y vehículo.
- Callback: firma inválida, idempotencia, duplicados, `AUTH_FAILED` y backoff.
- Scheduler: selección de cuentas y placas, timeouts (con `SatelliteClient` falso).
- **Fase 2:**
  - **Suite de contrato de `ChatHandler`**, que corre sobre todos los handlers registrados: reconstrucción del historial, traducción de herramientas al formato del proveedor, conversión de respuestas grabadas (fixtures) a etapas neutrales y orden de resultados en dos pasadas. Un handler nuevo pasa esta suite antes de activarse.
  - `ToolCallHandler`: herramienta no habilitada, argumentos vacíos o inválidos, límites, viaje inyectado desde la conversación aunque el modelo pida otro, reintento solo en idempotentes, caché e invalidación, auditoría en `tool_calls`.
  - Plantillas: cada `BaseToolTemplate` con su configuración (p. ej. varias herramientas sobre `TemplateEnviarWhatsapp`).
  - Suspensiones: agregación de varias en un turno, reanudación y vencimiento.
  - Seudonimización: ida y vuelta, incluido un marcador partido entre fragmentos del stream.
  - Flujo completo con `FakeChatHandler` (respuestas guionadas) y `FakeTelephonyProvider`: contesta, registra novedad, finaliza; no contesta → reintento → WhatsApp.

## 16. Siguientes pasos naturales

1. Motor de reglas y alertas (MON-01 a MON-05, ALE) sobre los mismos callbacks.
2. PostGIS para geocercas de origen/destino y desvíos de ruta.
3. Integración OpenWA (`OpenWAProvider`) y carga por Excel (REG-13).
4. Agente de voz (§10) con el motor de conversación (§11), sobre la arquitectura de clases de §4.
5. Scheduler en un proceso aparte cuando se escale la API.
