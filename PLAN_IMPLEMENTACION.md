# Plan de implementación del MVP operativo

> **Referencia histórica del primer entregable de monitoreo.** El [Plan maestro del MVP](backend/PLAN.md) es la fuente de verdad del proyecto; este documento no amplía ni reemplaza su alcance.

Fecha: 5 de octubre de 2026. Este plan se escribe antes de implementar y complementa los planes de Claude en `satrack-service/PLAN.md`, `backend/PLAN.md` y `web/PLAN.md`.

## Alcance y decisiones

Construir el recorrido login → configurar Satrack → registrar un viaje → verificar la placa → iniciar ruta → consultar posiciones → ver la flota y el historial → marcar entrega o cancelar con motivo. La primera iteración corresponde al núcleo de monitoreo de los planes existentes. Las comunicaciones por OpenWA, voz, reglas de alertas y cumplidos/RNDC pertenecen a las siguientes iteraciones; las APIs oficiales siguen siendo futuras.

Se conservan Python y Selenium del scraper, FastAPI en ambos servicios, PostgreSQL, React + TypeScript + Vite y el sistema de diseño Liquida. No se incorpora Redis, Celery, OAuth, JWT ni refresh tokens. Un proceso Uvicorn por servicio simplifica la coordinación en memoria. Todas las fechas persistidas son UTC; la interfaz muestra hora de Colombia.

## 1. Microservicio independiente del scraper

### Arquitectura y tecnologías

FastAPI + Pydantic para HTTP y contrato, httpx para callbacks y Selenium + Chromium para el proveedor real. El servicio no conoce viajes y no escribe en la base del backend. Conservaremos `crawler.py` original como referencia y reutilizaremos su extracción y selectores en `app/crawler.py`.

Cada petición se valida, se deduplica por UUID y se acepta en una cola acotada. Un lock por cuenta impide consultas simultáneas de la misma sesión; un semáforo limita los trabajos globales. El backend consulta una cuenta por trabajo y el servicio filtra las placas solicitadas.

**Ajuste al plan original:** cancelar `asyncio.to_thread` no detiene Selenium. Para el proveedor real usaremos un proceso por sesión/cuenta con un navegador reutilizable. El trabajo bloqueante se ejecuta fuera del proceso HTTP; ante timeout se termina el proceso y su grupo de procesos. Esto permite un timeout efectivo y evita reutilizar un navegador que continúa trabajando. Las sesiones se limitan y se cierran por inactividad. El simulador no necesita navegador.

### Endpoints y contrato

| Método | Endpoint | Respuesta |
|---|---|---|
| GET | `/health` | Proveedor, trabajos activos/en espera y sesiones |
| POST | `/v1/jobs` | 202 con `job_id`; requiere `X-Api-Key` |

`JobRequest`: UUID, `type` (`vehicles` o `positions`), cuenta (`id`, usuario, contraseña secreta) y placas. `positions` exige al menos una placa. No se permite elegir la URL de callback desde la petición.

Callback: `{job_id, type, status, finished_at, positions, vehicles, errors}`, con `X-Job-Id` y HMAC-SHA256 del body exacto. Tipos y nombres siguen los planes de Claude. Coordenadas, velocidad y hora GPS pueden ser nulas: una captura reciente nunca prueba que el GPS reportó recientemente. Se conserva el texto de fecha original y la hora de captura por separado.

### Carpetas

```text
satrack-service/
  app/{main,config,schemas,errors,jobs,callback,crawler}.py
  app/providers/{base,satrack,simulator}.py
  tests/
  crawler.py                  # original conservado
  pyproject.toml, uv.lock, Dockerfile, .env.example
```

### Errores y escalabilidad

401 para clave inválida, 409 para UUID repetido, 422 para contrato inválido y 503 para cola llena o apagado. Errores del proveedor: `AUTH_FAILED`, `CAPTCHA_REQUIRED`, `PROVIDER_CHANGED`, `PROVIDER_UNAVAILABLE`, `TIMEOUT`, `VEHICLE_NOT_FOUND` y `POSITION_UNAVAILABLE` cuando faltan datos espaciales. Evidencia de fallos dentro del volumen privado, con limpieza por antigüedad. Nunca registrar credenciales ni devolver excepciones crudas del navegador.

Callbacks con cuatro intentos y pausas 2/10/30 segundos, usando siempre el mismo payload firmado. Jobs y deduplicación en memoria se pierden al reiniciar; el backend conserva las consultas y las recupera por timeout. No se promete entrega exactamente una vez. La primera versión usa una réplica; más adelante, enrutamiento por cuenta permite conservar afinidad de sesión.

### Implementación y verificación

1. Schemas/configuración y simulador con placas conocidas.
2. Extracción normalizada y aislamiento de navegadores.
3. Cola, límites, expiración, timeout y cierre de sesiones.
4. API, autenticación y callback firmado.
5. Tests de contrato, filtrado, duplicados, cola, serialización y timeout.

## 2. Backend

### Stack y estructura

Python 3.12, FastAPI, SQLAlchemy 2, psycopg, Alembic y PostgreSQL 16. SQLAlchemy síncrono con trabajo del scheduler en hilos; las operaciones HTTP se realizan fuera de transacciones abiertas. `lifespan` administra el scheduler y su apagado, siguiendo la [documentación de FastAPI](https://fastapi.tiangolo.com/advanced/events/).

```text
backend/
  app/{main,config,db,models,schemas,security,deps,validators,cli,scheduler}.py
  app/routers/{auth,viajes,flota,cuenta_satelital,panel,internal}.py
  app/services/{viajes,satrack_client,monitoreo}.py
  alembic/versions/, alembic.ini
  tests/
  pyproject.toml, uv.lock, Dockerfile, .env.example
```

### Modelos y base de datos

Transportadoras, usuarios, sesiones, cuentas satelitales, conductores, vehículos, viajes, remesas, posiciones, consultas satelitales y eventos. Los modelos mantienen los campos del plan de Claude y claves de transportadora para limitar acceso. Restricciones: manifiesto único por transportadora, placa y cédula únicas por transportadora, remesa única por viaje, posición única por vehículo y hora GPS conocida, una consulta pendiente por cuenta y un viaje activo por conductor/vehículo.

Se considera también `registrado` como reserva activa del conductor y vehículo para impedir que dos viajes pendientes se programen simultáneamente cuando se verifica la flota. Las carreras se resuelven con restricciones de base de datos y respuestas 409; no solo mediante un `SELECT` previo. Alembic crea un esquema inicial explícito y versionado. La [documentación de SQLAlchemy](https://docs.sqlalchemy.org/en/20/core/constraints.html) sustenta constraints e índices.

Las contraseñas satelitales se cifran con Fernet derivado de `SECRET_KEY`. Las posiciones guardan hora GPS nullable y hora de captura; no se inventa velocidad ni coordenadas. Un resultado fuera de orden no sustituye una posición más reciente ni modifica una configuración posterior de credenciales.

### Autenticación mínima

Usuario + contraseña, hash bcrypt y sesión aleatoria opaca. En la base solo se guarda SHA-256 del token, con vencimiento configurable de siete días. Logout elimina la sesión. El frontend envía Bearer; no hay registro público, roles, OAuth, JWT ni refresh. CLI para crear usuario, bootstrap y demo. El mensaje de login fallido es genérico y se acotan intentos repetidos.

### Endpoints

| Método | Ruta | Uso |
|---|---|---|
| POST | `/api/auth/login` | Usuario + password, token y usuario |
| GET | `/api/auth/me` | Sesión y transportadora |
| POST | `/api/auth/logout` | Revocar sesión |
| GET | `/api/panel` | Conteos, conexión y flota |
| GET/POST | `/api/viajes` | Buscar/paginar y crear viaje con remesas |
| GET | `/api/viajes/{id}` | Detalle y eventos |
| GET | `/api/viajes/{id}/posiciones` | Historial acotado de posiciones |
| POST | `/api/viajes/{id}/transiciones` | Iniciar, entregar o cancelar |
| GET | `/api/vehiculos` | Flota y última posición |
| GET | `/api/conductores` | Conductores de la transportadora |
| GET/PUT | `/api/cuenta-satelital` | Consultar estado y guardar credenciales |
| POST | `/api/cuenta-satelital/sincronizar` | Verificar vehículos |
| POST | `/api/cuenta-satelital/consultar` | Consultar posiciones ahora para operación/pruebas |
| POST | `/internal/satrack/callback` | Recepción firmada e idempotente |
| GET | `/health` | Conexión a base de datos |

Validaciones de placa, cédula, teléfono, pesos, remesas, origen/destino y fechas en schemas; reutilización de conductor/vehículo, unicidad y transiciones en servicios. Errores en español con campo y mensaje. Los eventos identifican usuario, motivo y cambio.

### Integración y scheduler

Persistir y hacer commit del job antes de enviarlo al scraper. La API recibe callbacks incluso antes de que finalice el envío. El callback valida firma y coincidencia de UUID/tipo, bloquea la consulta y procesa todo en una transacción. Responde 200 a repetidos ya procesados. Una actualización de credenciales incrementa la versión de cuenta; callbacks anteriores quedan registrados sin aplicar resultados obsoletos.

Scheduler cada 60 segundos, consulta de posiciones según frecuencia 5–10 minutos, `programado` desde una hora antes de salida y `en_ruta`. Recupera consultas sin callback. Se usa timeout de consulta de 240 segundos para cubrir espera, ejecución de 120 segundos y los reintentos del callback. Credenciales inválidas detienen consulta; captcha/cambio web aplican backoff de 15 minutos. Consultas manuales facilitan el primer uso y el piloto.

### Verificación

Tests de sesiones/revocación, separación de transportadoras, validaciones, carreras/constraints, transiciones, callback duplicado y fuera de orden, fechas GPS desconocidas, timeout y selección del scheduler. Pruebas de integración contra PostgreSQL en un esquema temporal aislado y demo de extremo a extremo con el simulador.

## 3. Frontend

### Stack y diseño

React 19, TypeScript, Vite, React Router, TanStack Query, Leaflet/react-leaflet, Lucide y Tailwind 4. SPA de uso operativo y un solo origen `/api`: Vite proxy en desarrollo y nginx en Docker. Se usan los tokens, logo y pautas Liquida; fondo papel cálido, azul ruta, tipografía Inter/Inter Tight, estados con icono y texto, navegación lateral en escritorio e inferior en móvil. La [guía de Vite](https://vite.dev/guide/) documenta el flujo de build.

### Carpetas y pantallas

```text
web/
  src/api/{client,types,hooks}.ts
  src/auth/{AuthContext,RequireAuth}.tsx
  src/components/{ui,layout,map}/
  src/features/{login,panel,viajes,flota,ajustes}/
  src/lib/format.ts
  public/brand/
  package.json, package-lock.json, tsconfig.json, vite.config.ts
  index.html, nginx.conf, Dockerfile
```

Login; panel con indicadores, estado Satrack y viajes; lista con búsqueda/filtro/paginación; creación con múltiples remesas y errores por campo; detalle con acciones, recorrido, datos y eventos; flota; ajustes Satrack y logout. Autenticación mediante Context, token en `sessionStorage` para persistir recarga de pestaña y limpieza en 401. Las rutas protegidas preservan el destino al volver a entrar. TanStack Query mantiene los datos del servidor y se vacía al salir/cambiar usuario.

Mapas solo con coordenadas válidas y atribución OpenStreetMap. Las teselas requieren conexión y no constituyen evidencia de precisión del GPS. Fechas mostradas en Colombia y datos de captura distinguidos del reporte GPS. Actualización cada 60 segundos en pantallas activas; consultas manuales permiten observar cambios del simulador.

Responsive: móvil una columna y navegación inferior; escritorio contenido amplio y barra lateral. Formularios accesibles, focos visibles, estados de carga/error/vacío y confirmaciones para transiciones.

### Verificación

TypeScript/build y tests de cliente HTTP, fechas y formulario de remesas. Prueba del navegador: login, crear viaje, verificar placa, iniciar, consultar posición y finalizar; captura de escritorio y móvil para revisar layout.

## 4. Docker, puertos y documentación

Cuatro servicios: `db` PostgreSQL 5432 interno; `satrack` FastAPI + Chromium 8080 interno, 8081 local; `api` FastAPI + scheduler 8000 interno/local; `web` nginx con SPA y proxy, 80 interno y 8080 local. Volúmenes de PostgreSQL y evidencia del scraper. Healthchecks, reinicio y una única réplica por servicio con coordinación en memoria.

Un archivo `DOCKER.md` describirá exactamente imágenes, contenido de contenedores, variables, rutas, puertos, comandos, demo, pruebas y operación real. `.env.example` contiene valores de ejemplo y un script genera secretos locales sin imprimirlos. `.env`, archivos de runtime y dependencias se ignoran en Git. No se publicará el sitio ni se usarán credenciales satelitales sin que el usuario las configure.

## Criterio de entrega

Planes escritos primero, código de los tres componentes, Compose documentado, build y pruebas de integración completas. La verificación con Satrack real requiere credenciales del piloto; la demo y pruebas automatizadas usan `PROVIDER=simulator`. Los resultados reales de pruebas y sus límites se anotarán al terminar.
