# Rumboo — Plan maestro del MVP

**Fuente de verdad del proyecto · Versión 1 · 6 de octubre de 2026**

**Estado: backend separado en módulos ortogonales (M0, §3 y §8.1); siguiente hito M1.** El microservicio Satrack queda fuera de los cambios: se integra mediante su contrato HTTP existente. El código existente es trabajo en curso y no acredita que un épico esté terminado.

## 1. Objetivo, alcance y autoridad

> **Ayudamos a tu equipo de tráfico a recuperar, revisar y cerrar los cumplidos con menos trabajo manual, integrándonos con sus herramientas actuales.**

El MVP completo conecta registro de viajes, seguimiento con Satrack, comunicación con el conductor, recuperación del cumplido y cierre asistido. El primer entregable de monitoreo es una parte del MVP; por sí solo no valida la promesa de recuperar y cerrar cumplidos.

**Decisiones de alcance:** scraper Selenium de Satrack; WhatsApp mediante OpenWA; login con usuario y contraseña; aprobación humana antes de transmitir al RNDC. Las APIs oficiales de Satrack y WhatsApp quedan para después. Las llamadas del MVP son al conductor; los agentes que contactan al cliente y resuelven problemas cuando tú no estás pertenecen a una evolución futura.

Este documento gobierna backend, scraper, frontend e infraestructura. Cualquier cambio de alcance debe actualizar aquí el épico afectado, sus dependencias y su criterio de aceptación **antes de implementarlo**.

| Documento | Función y autoridad |
|---|---|
| Este `PLAN.md` | Alcance, épicos, arquitectura, contratos principales, orden y criterios de entrega vigentes |
| [ARQUITECTURA_BACKEND.md](../docs/ARQUITECTURA_BACKEND.md) | Detalle de fronteras, propiedad de datos, contratos públicos y recuperación del backend; complementa este plan |
| [TESIS.md](../TESIS.md) y [IDEA.md](../IDEA.md) | Contexto de negocio y visión; no amplían automáticamente el alcance técnico |
| [IMPLEMENTACION.md](../IMPLEMENTACION.md), [plan del scraper](../satrack-service/PLAN.md), [plan web](../docs/PLAN_WEB_PRODUCTO.md) y [plan previo general](../PLAN_IMPLEMENTACION.md) | Referencias subordinadas; sus discrepancias se resuelven a favor de este plan |
| [REFERENCIA_PLAN_ANTERIOR.md](REFERENCIA_PLAN_ANTERIOR.md) | Archivo histórico, especialmente del diseño de voz; no agrega requisitos al MVP |

**Fuera del MVP:** agentes autónomos de atención al cliente, correo, app para conductores, pagos/facturación, otros satelitales, OAuth, roles complejos, JWT y refresh tokens. Tampoco se construirá un framework genérico de agentes o un catálogo de herramientas editable en producción.

## 2. Lista completa de épicos

Esta lista constituye el alcance completo. Un épico termina cuando cumple su criterio y las pruebas de la sección 9; una pantalla o clase aislada no bastan.

| EP | Descripción y alcance | Por qué se incluye | Criterio de aceptación |
|---|---|---|---|
| **EP-01 · Plataforma y operación** | Docker Compose, configuración, PostgreSQL, migraciones, volúmenes, healthchecks, bootstrap y manual de arranque/puertos | Instalar y operar el producto de forma reproducible | Un entorno limpio arranca; migraciones repetibles; datos persistentes tras reinicio; respaldo y restauración documentados |
| **EP-02 · Acceso y aislamiento** | Login/logout, sesiones simples, usuarios por CLI y acceso limitado a su transportadora | Proteger información sin complicar la autenticación | Sesiones revocables y con vencimiento; ningún endpoint permite leer/modificar otra transportadora |
| **EP-03 · Registro de la operación** | Conductores, vehículos, viajes y remesas; consentimiento; formulario y plantilla Excel; ruta y puntos autorizados opcionales | Obtener los datos para seguir el viaje y asociar el cumplido | Manifiesto único; peso calculado; catálogos reutilizados; conflictos activos rechazados; importación devuelve creados/errores sin duplicados |
| **EP-04 · Microservicio del scraper** | Crawler convertido en API independiente; proveedores real/simulado; sesiones reutilizables, concurrencia acotada, errores y callback firmado; consulta de resultados y colección Postman para operación independiente | Reutilizar el acceso a Satrack y aislar Selenium del backend | Jobs `vehicles`/`positions` funcionan y devuelven datos disponibles de la ficha; resultados consultables con API key; colección Postman ejecutable sin backend; timeout libera navegador; duplicados/cola llena tienen respuesta definida; sin credenciales expuestas |
| **EP-05 · Cuenta satelital y consultas** | Credenciales cifradas por transportadora; sincronización de toda la flota con datos disponibles; scheduler, consulta manual, callbacks idempotentes y reconciliación mediante el GET existente del scraper; consulta de resultados persistidos en backend | Automatizar seguimiento sin consultas duplicadas o bloqueadas, incluyendo el scraper independiente sin callback | Una consulta pendiente por cuenta; flota y resultados persistentes; verificación programa viajes; resultados antiguos no alteran configuraciones nuevas; GET recupera trabajos sin callback; timeout permite una consulta posterior y cada fallo se cuenta una vez |
| **EP-06 · Posiciones e historial** | Última ubicación por vehículo, recorrido por viaje y horas GPS/captura separadas | Aportar contexto y una base verificable para las reglas | Sin coordenadas, velocidad o frescura inventadas; puntos repetidos no duplican historial; datos antiguos no reemplazan los recientes |
| **EP-07 · Reglas y alertas** | Desvío, detención, retraso, pérdida de señal y llegada; severidad, atención, cierre y deduplicación | Convertir el seguimiento en una acción útil | Reglas probadas con casos reproducibles; datos faltantes → no evaluable; alerta única por viaje/tipo; atención/cierre auditados |
| **EP-08 · WhatsApp con OpenWA** | Número dedicado; envío/recepción de texto, audio y fotos; asociación a viaje; autorización y estado de sesión | Obtener novedades y recuperar documentos por el canal inicial elegido | Entradas deduplicadas; archivos privados; mensajes sin viaje visibles; desconexión visible; reintentos sin envíos duplicados |
| **EP-09 · Voz al conductor** | Llamadas programadas, por alerta y manuales; transcripción, clasificación y herramientas para consultar, registrar novedades, actualizar ETA o solicitar seguimiento | Obtener información que el satelital no entrega y reducir llamadas manuales | Respeta autorización/horarios/límites; política de no respuesta; acciones validadas/auditadas; agente sin aprobación documental ni transmisión RNDC |
| **EP-10 · Reportes operativos** | Resumen consolidado por transportadora, avisos inmediatos y confirmación de cierre por bandeja/WhatsApp | Informar al equipo sin revisar cada viaje | Resumen solo con viajes activos; ETA/novedades con fuente visible; reportes/notificaciones registrados y sin duplicados |
| **EP-11 · Recuperación y revisión de cumplidos** | Solicitud de fotos, recordatorios, asociación a remesa, extracción con visión, validaciones, excepciones y aprobación humana | Resolver el trabajo principal de la tesis: conseguir y revisar el soporte | Documento ilegible/incierto exige revisión; diferencias visibles; aprobación registra usuario/hora/versión; soporte para todas las remesas |
| **EP-12 · RNDC y cierre asistido** | Preparación, transmisión con acceso validado, reconciliación y alternativa de carga manual confirmada | Completar el recorrido hasta un cierre verificable | Solo transmite lo aprobado; resultado incierto se consulta antes de reenviar; carga manual con evidencia; cierre tras confirmar todas las remesas y notificar |
| **EP-13 · Indicadores de pendientes** | Pendientes documentales, antigüedad, días hábiles y métricas por transportadora | Priorizar trabajo y medir el valor | Cálculos trazables/probados; calendario explícito; indicador regulatorio solo tras validar definición y contrastar con RNDC del cliente |
| **EP-14 · Bandeja web responsive** | Login, panel, viajes, flota, conexión, alertas, mensajes sin viaje, cumplidos e indicadores | Dar al coordinador una operación completa desde computador/móvil | Flujos conectados al backend; carga/error/vacío y confirmaciones; diseño `liquida-design`; fechas de Colombia y controles accesibles |
| **EP-15 · Calidad y piloto** | Simuladores de integraciones, datos demo, pruebas y piloto en sombra seguido de operación asistida | Comprobar utilidad y estabilidad con evidencia | Flujos/fallos externos probados; integraciones reales verificadas aparte; límites documentados; línea base y ahorro/costo por viaje medidos |

No se incluye exceso de velocidad en esta versión. Las referencias `REG`, `FRE`, `MON`, `TEC`, `ALE`, `CON`, `WA`, `REP` y `CUM` de `IMPLEMENTACION.md` orientan el detalle, pero este plan prevalece. Los umbrales son parámetros de piloto, no garantías ni afirmaciones normativas.

## 3. Arquitectura del backend

**Principio rector: arquitectura ortogonal.** Un cambio queda contenido en el módulo responsable mientras conserve su contrato público. Las dependencias de negocio son explícitas; separar carpetas por sí solo no garantiza independencia. Las fronteras y los recorridos se detallan en [ARQUITECTURA_BACKEND.md](../docs/ARQUITECTURA_BACKEND.md). Se aplica en dos niveles.

1. **Entre servicios desplegables:** se separa cuando lo justifiquen aislamiento de fallos, escala o runtime y exista un contrato estable.
2. **Dentro del backend:** módulos por dominio, con fronteras que verifica una herramienta.

### 3.1 Topología y microservicios

**Monolito modular FastAPI, más microservicio satelital, OpenWA y PostgreSQL**, en un servidor con Docker Compose.

```text
           ┌──────────────────────────┐        ┌──────────────┐
 Web ─────►│ api (backend)            │───────►│  PostgreSQL  │
   /api    │  routers + core/tareas   │        └──────────────┘
           └───┬──────────────────▲───┘
   POST jobs   │  enviar          │ webhooks firmados
               ▼         ▼        │ (callback Satrack, eventos OpenWA)
       satrack-service   OpenWA ──┘
```

**Criterio para crear un microservicio.** Debe cumplir las cuatro condiciones:

- tiene un runtime distinto o pesado;
- sus fallos deben quedar aislados;
- no necesita transacciones con datos de negocio;
- su contrato es estable.

| Componente | Decisión | Motivo |
|---|---|---|
| `satrack-service` | Microservicio propio, **ya existe y no se modifica** | Usa Chrome y Selenium, aísla los fallos del navegador, no tiene BD y su contrato es `/v1/jobs` |
| OpenWA | Contenedor de terceros, sin código nuestro | Ya aísla el transporte de WhatsApp. Lo usamos desde el adaptador `mensajeria/openwa.py` |
| `whatsapp-service` propio | **No** | Sería un envoltorio sobre OpenWA: un salto de red más sin aislar ningún runtime. Además, los mensajes se guardan junto a los viajes |
| Tareas de fondo | **Dentro de la API en el MVP** | `core/tareas.py` no depende de FastAPI. Separarlo reutiliza la lógica, pero también requiere configuración, supervisión y heartbeat compartido (§3.5) |
| `voz-service` (futuro) | Microservicio cuando se implemente la voz | Audio en tiempo real, websockets y telefonía. Las decisiones y herramientas del agente quedan en el backend (§3.6) |

**Reparto de responsabilidades:**

- **Backend:** es el dueño exclusivo de las tablas de Rumboo, las reglas, las transiciones, la autorización y la programación. OpenWA administra su persistencia propia; no se accede a ella desde el backend.
- **Scraper:** no conoce viajes, usuarios ni reglas.
- **OpenWA:** solo transporta mensajes.
- **Frontend:** no decide reglas críticas.

### 3.2 Módulos por dominio y reglas de ortogonalidad

Cada módulo es una carpeta con sus propios `models.py`, `schemas.py`, `servicio.py` y `router.py`. El `__init__.py` documenta propiedad, contratos y dependencias. Las funciones implementan los casos de uso; las clases se reservan para adaptadores y estructuras de datos. Un cambio que conserva el contrato no obliga a modificar consumidores.

Capas, de arriba hacia abajo:

```text
app.main · app.cli · app.modelos      raíz de composición: el único lugar que conecta módulos
app.agentes                           clientes de IA de los servicios; nadie los importa
app.indicadores                       vistas de solo lectura
app.monitoreo | app.mensajeria | app.documentos   hermanos independientes: no se importan entre sí
app.satelital
app.operacion
app.acceso
app.auditoria
app.core                              infraestructura sin dominio
```

1. **Cada módulo es dueño de sus tablas.** Otro módulo solo usa sus `servicio` y `schemas`, nunca sus `models`. La API pública devuelve DTO validados, no entidades ORM mutables; las relaciones entre módulos usan identificadores y contexto de transportadora.
2. **Las dependencias solo bajan.** Los módulos de una misma capa marcada con `|` no se conocen entre sí.
3. **Las reacciones entre módulos se enlazan en `app/main.py`**, nunca por llamadas hacia arriba:
   - **Eventos durables:** el cambio y sus entregas a consumidores se guardan en una misma transacción. El runner despacha después del commit. La verificación de un viaje y la evaluación de posiciones no dependen únicamente del bus en memoria.
   - **`core/tareas`:** tareas periódicas registradas por cada módulo en su `enlaces.py`. `EntregaPendiente` conserva destinatario, deduplicación, intentos y vencimiento de reclamación. El bus en memoria puede despertar el runner, pero no es la fuente de recuperación.
   - **Consultas compuestas:** una función enlazada por instancia combina DTO de operación y satelital por lotes para devolver vehículo y ubicación. Se sustituye la extensión global `registrar_datos_vehiculo`; no se comparten objetos ORM con el proveedor.
4. **Las particularidades de cada sistema externo se concentran en su adaptador:**
   - `satelital/cliente.py` (`satrack-service`);
   - `mensajeria/openwa.py` (OpenWA);
   - `documentos/almacenamiento.py` (disco);
   - `agentes/llm.py` (proveedor de IA).
   Sustituir un proveedor exige comprobar autenticación, eventos y capacidades mediante pruebas de contrato; no se promete que siempre baste cambiar un archivo.
5. **Los servicios no conocen HTTP.** Lanzan errores de `core/errores.py`, y `core/web.py` los traduce a 401, 404, 409 o 422. Así el mismo caso de uso sirve a routers, tareas y agentes.
6. **Las fronteras se verifican automáticamente.** Los contratos de `import-linter` están en `pyproject.toml`: capas, privacidad de `models` y que ni la lógica de negocio ni `core` dependan de FastAPI. `tests/test_arquitectura.py` hace fallar las pruebas si se rompe una frontera, o si las migraciones dejan de coincidir con los modelos.
7. **Las pruebas se agrupan por módulo** (`tests/<modulo>/`) y corren sobre PostgreSQL, con adaptadores falsos para los sistemas externos.

**Deuda conocida:** `vehiculos.en_satelital` y `vehiculos.ultima_posicion_id` son datos de satelital guardados en la tabla de operacion. Satelital solo los cambia mediante funciones de `operacion.servicio`. Una migración futura los moverá a `vehiculos_satelitales`.

**Fronteras por completar:** los servicios actuales pueden devolver ORM y usan una extensión global; el bus actual no persiste eventos y el runner adquiere liderazgo al inicio. M1 completa DTO, composición por instancia, reacción durable a `viaje_registrado` y comprobación de liderazgo. Estas capacidades no se consideran resueltas por la separación inicial de carpetas.

### 3.3 Stack y decisiones

| Pieza | Elección | Motivo y límite |
|---|---|---|
| API | Python 3.12, FastAPI y Pydantic | Mismo lenguaje que el crawler. Contratos validados, OpenAPI y REST |
| Datos | PostgreSQL 16, SQLAlchemy 2 síncrono, psycopg 3 y Alembic | Transacciones, restricciones e índices |
| Geometría | shapely y haversine en Python, **sin PostGIS en el MVP** | GeoJSON y puntos manuales. `geo.py` transforma a coordenadas métricas antes de medir corredores; no compara kilómetros con grados |
| Programación | Runner `core/tareas.py` dentro de la API, con advisory lock y heartbeat | Un solo ejecutor aunque haya réplicas. El trabajo pendiente persiste en la BD |
| Integraciones | httpx y un adaptador por sistema externo | Timeouts, firmas, errores e idempotencia aislados en cada integración |
| Sesión y secretos | bcrypt, token opaco y Fernet | Login revocable. Las credenciales de Satrack y OpenWA se descifran solo en el backend |
| Archivos | Volumen privado más metadatos en la BD | Suficiente para el piloto. `LocalFileStorage` se puede cambiar por almacenamiento de objetos |
| Arquitectura | import-linter | Las fronteras entre módulos se verifican en las pruebas |
| Web | React, TypeScript, Vite, Tailwind, React Router, TanStack Query y Leaflet | SPA con `liquida-design`, en el mismo origen `/api` |

**Sin Redis, Celery, Kubernetes ni broker genérico en el MVP.**

### 3.4 Estructura del código

**Estado:** el árbol de trabajo contiene una separación inicial por dominios. Las fronteras pendientes se señalan en §3.2. Los módulos marcados con «M2» o posterior existen solo como paquete documentado: un `__init__.py` con su responsabilidad, sin modelos, rutas ni código simulado.

```text
backend/app/
├── main.py         Raíz de composición: routers, enlaces, tareas, errores y /health.
├── modelos.py      Registro de tablas para SQLAlchemy y Alembic.
├── cli.py          Bootstrap de usuarios y datos de demo.
├── core/           config, db, seguridad, errores, eventos, tareas, paginacion; web (único con FastAPI).
├── auditoria/      eventos (solo inserción) · registrar_evento.
├── acceso/         transportadoras, usuarios, sesiones · login/me/logout · deps.User.
├── operacion/      conductores, vehiculos, viajes, remesas · alta, reservas, transiciones, catálogos
│                   · /api/viajes, /api/vehiculos, /api/conductores. Próximo: Excel (M1).
├── satelital/      cuentas, consultas, posiciones · cliente.py (único que conoce satrack-service)
│                   · enlaces.py · /api/cuenta-satelital, /api/viajes/{id}/posiciones, callback.
│                   Próximo (M1): GET de reconciliación, resultado guardado, flota completa.
├── indicadores/    /api/panel. Próximo: pendientes y antigüedad (M2), reportes (M4).
├── documentos/     M2 · archivos privados y cumplidos versionados; revision.py solo para humanos.
├── mensajeria/     M3 · OpenWA, mensajes, bandeja sin viaje y recordatorios.
├── monitoreo/      M3–M4 · puntos de control, reglas puras, alertas, novedades y rutas GeoJSON.
└── agentes/        Pendiente · convención para agentes de IA (§3.6).
```

### 3.5 Crecimiento y límites

Al inicio hay una réplica de la API y una del scraper.

- **Estado y volatilidad:** PostgreSQL guarda consultas, resultados y acciones pendientes de Rumboo. El scraper conserva jobs en memoria; si pierde un UUID, el backend reenvía una consulta todavía vigente con reintentos acotados. No se garantiza recuperar un resultado que nunca llegó a persistirse.
- **Entrega:** no se promete entrega exactamente una vez.
- **Liderazgo:** el runner mantiene y comprueba el advisory lock en una conexión dedicada. Si la pierde, detiene reclamaciones hasta recuperarlo. Las entregas tienen reclamaciones con vencimiento y deduplicación. El heartbeat distingue último intento de último éxito por tarea.
- **Separar las tareas en un proceso propio** se hace sin tocar la lógica:
  1. Crear `app/worker.py`, que arma el mismo `Runner` con `<modulo>.enlaces.tasks(...)`.
  2. Poner `SCHEDULER_ENABLED=false` en la API.
  3. Agregar el servicio `worker` en Compose con la misma imagen.
  4. Mover el heartbeat de memoria a la BD.
- **Crecer más:** replicar la API y enrutar cada cuenta a una réplica del scraper con afinidad. La cola persistida en PostgreSQL llega con las reacciones críticas; un broker externo y el almacenamiento de objetos se agregan cuando el volumen lo justifique.
- **Volumen de datos:** listas paginadas, historial acotado e índices por transportadora, viaje y fecha desde el inicio. La capacidad se fija después de medir.

### 3.6 Agentes de IA del negocio

Ningún agente está implementado: la voz, la extracción automática y el RNDC siguen pendientes. Esta sección y `app/agentes/__init__.py` fijan cómo se crearán. **Un agente es un cliente de los módulos, igual que un router**: no es dueño de reglas de negocio ni de tablas ajenas.

```text
agentes/
├── llm.py            Único archivo con el SDK del proveedor de IA; el modelo se configura por agente.
├── herramientas.py   Herramienta = nombre, descripción, schema Pydantic y función de servicio; valida y audita.
├── models.py         acciones_agente: herramienta, argumentos validados, resultado, error, contexto.
└── <agente>/         instrucciones.md (prompt en Git), contexto.py (lo inyecta el servidor),
                      herramientas.py (lista FIJA), agente.py (contexto + llm + herramientas).
```

| Agente previsto | Disparador | Herramientas | Nunca puede |
|---|---|---|---|
| Voz al conductor (EP-09) | Tarea programada o alerta | Consultar viaje, registrar novedad, actualizar ETA, solicitar seguimiento | Aprobar documentos ni transmitir al RNDC |
| Clasificador de mensajes de WhatsApp | Evento `mensaje_recibido` | Proponer viaje y novedad para revisión humana | Asociar sin confirmación cuando hay ambigüedad |
| Extracción de cumplidos (visión) | Evento de versión creada | Proponer datos declarados con origen «ia» | Aprobar o rechazar |

**Reglas:**

1. **Solo usan `<modulo>.servicio` y `schemas`.** Pasan las mismas validaciones y el mismo aislamiento por transportadora que la API.
2. **El contexto lo fija el servidor.** Las herramientas no reciben `transportadora_id` ni ids libres.
3. **Las acciones solo humanas** (`documentos/revision.py` y la transmisión al RNDC) quedan prohibidas para `app.agentes` mediante un contrato de import-linter, que se agrega junto con ese archivo.
4. **Se activan por eventos o tareas enlazados en `app/main.py`.** Ningún módulo de negocio los llama.
5. **Cada llamada a una herramienta se registra** en `acciones_agente` y en `auditoria`.
6. **No hay framework genérico:** ni catálogo dinámico, ni agentes anidados, ni suspensiones genéricas, ni varios LLM activos a la vez.
7. **El audio en tiempo real va en `voz-service`.** Las decisiones y las herramientas quedan en `agentes/voz_conductor/`, porque necesitan transacciones con los datos del negocio.
8. **Se prueban con un LLM falso.** Las herramientas son funciones deterministas.

### 3.7 Cómo agregar piezas sin romper la ortogonalidad

- **Módulo de negocio:**
  1. Crear la carpeta con `__init__.py` documentado, `models`, `schemas`, `servicio`, `router` y, si hace falta, `enlaces`.
  2. Registrar sus `models` en `app/modelos.py`.
  3. Incluir su router y sus enlaces en `app/main.py`.
  4. Ubicarlo en la capa correcta y agregar su contrato de privacidad de `models` en `pyproject.toml`.
  5. Crear una migración nueva que no reemplace datos.
  6. Crear `tests/<modulo>/`.
- **Reacción entre módulos:**
  1. El módulo de origen publica un evento con datos simples (ids y valores).
  2. El módulo destino expone una función async.
  3. `app/main.py` los suscribe.
  4. Guardar la entrega en la misma transacción que el cambio cuando la reacción sea necesaria para el negocio; el consumidor debe deduplicarla.
- **Sistema externo:**
  1. Un solo archivo adaptador traduce a los schemas propios.
  2. Se crea un falso para pruebas.
  3. Su configuración va solo en `core/config.py`.
- **Agente:** seguir §3.6. Primero la herramienta, como función de servicio probada; después el agente.
- **Microservicio:** solo si cumple los cuatro criterios de §3.1. Debe tener un contrato HTTP versionado, colección Postman y un adaptador en el módulo dueño.

## 4. Datos, seguridad e invariantes

### 4.1 Modelo de datos

| Grupo (módulo dueño) | Entidades/datos esenciales | Restricciones |
|---|---|---|
| Acceso (`acceso`) | `transportadoras`, `usuarios`, `sesiones` | Usuario único; SHA-256 del token; transportadora obtenida de sesión |
| Operación (`operacion`) | `conductores`, `vehiculos`, `viajes`, `remesas` | Cédula/placa únicas por transportadora; manifiesto único por transportadora; remesa única por viaje; pesos positivos |
| Satelital (`satelital`) | `cuentas_satelitales`, `consultas_satelitales`, `posiciones`; `vehiculos_satelitales` en M1 | Una cuenta Satrack por transportadora; versión de credenciales; una consulta pendiente por cuenta; UUID único; punto único por vehículo/hora GPS conocida |
| Monitoreo (`monitoreo`) | `puntos_control`, `alertas`, `novedades`; `rutas_viaje` (GeoJSON) en M4 | Una alerta abierta por viaje/tipo; atención auditada; ruta/coordenadas opcionales |
| Comunicación (`mensajeria`, `core.tareas`) | `canales_whatsapp`, `mensajes`; `entregas_pendientes` (cola persistida de core) | ID externo/idempotencia únicos por integración; intentos/próximo intento/resultado persistidos |
| Documentos (`documentos`) | `archivos_privados`, `cumplidos`, `versiones_cumplido` (+ archivos) | Soporte versionado; aprobación ligada a versión; cambios invalidan aprobación pendiente |
| Reportes (`indicadores`) | `reportes` (M4) | Período, viajes incluidos y estado de envío |
| Agentes (`agentes`, pendiente) | `acciones_agente` | Solo documentado hasta definir proveedor; consume servicios de negocio |
| Voz y RNDC (módulos futuros, pendientes) | `llamadas`, `transmisiones_rndc` | Dueños separados de sus datos; sin implementar hasta definir proveedores y acceso RNDC |
| Trazabilidad | `eventos` | Solo inserción desde aplicación; actor/entidad/motivo/fecha; sin edición/borrado por API |

Entidades de negocio con `transportadora_id`; relaciones y accesos dentro de esa empresa. Webhooks resuelven la transportadora desde el canal/cuenta autenticado, no desde un ID libre del payload. Fechas UTC, presentación `America/Bogota`. Aislamiento y carreras se prueban sobre PostgreSQL.

### 4.2 Autenticación mínima y secretos

Usuarios por CLI; login con bcrypt; token aleatorio de 32 bytes, hash SHA-256 en BD y vencimiento de siete días. Navegador usa `sessionStorage` y Bearer; `401` limpia sesión/caché; logout revoca la fila. Sin registro público, roles, OAuth, JWT ni refresh tokens. Intentos de login limitados y error genérico.

Secretos por variables de entorno, fuera de Git/logs/respuestas. Satrack cifrado con Fernet; respaldar `SECRET_KEY` con BD para conservar acceso a credenciales. Archivos privados con límites de tamaño/tipo, nombres generados y acceso autorizado o enlaces firmados breves.

### 4.3 Invariantes de negocio

- Placa `AAA999`; cédula de 6–10 dígitos; celular colombiano `+57`; origen distinto de destino; llegada posterior a salida; al menos una remesa; peso total calculado en servidor. Excel agrupa filas por manifiesto y valida el viaje completo antes de crearlo; un grupo inválido no genera un viaje parcial.
- `registrado`, `programado`, `en_ruta`, `con_novedad` reservan conductor/vehículo. Restricciones de BD impiden reservas simultáneas, incluidas pendientes de verificación. Entregar/cancelar libera la reserva aunque el cierre documental siga pendiente.
- Sin Satrack se puede guardar el viaje `registrado`; `programado` requiere placa confirmada con la configuración vigente.
- Hora GPS nullable: **nunca se sustituye por captura**. Coordenadas ausentes/`0,0`, velocidad desconocida y fechas ilegibles significan dato no disponible, no señal GPS reciente.
- Sin ruta no hay desvío/avance; sin coordenadas no hay geocerca; sin velocidad/estimación fiable no hay detención/ETA. La UI muestra qué no se puede evaluar, sin inventar normalidad o anomalías.
- Falla del scraper no genera «sin señal del vehículo». Las reglas usan muestras GPS distintas; repetir la misma hora no cuenta como dos lecturas consecutivas.
- Autorización registrada con fecha/canal antes de llamadas/mensajes automáticos; ausencia o revocación bloquea contactos y señala el viaje.
- IA interpreta; código valida herramientas/reglas; humano aprueba lo transmitido al RNDC. El contexto de viaje/transportadora se inyecta por servidor, nunca lo elige libremente el agente.

### 4.4 Ciclo de vida

```text
Operación:   registrado → programado → en_ruta ↔ con_novedad → entregado
             registrado / programado / en_ruta / con_novedad → cancelado
Documentos:  pendiente → en_revision → aprobado o rechazado (por versión y remesa)
RNDC:        pendiente de integración; su confirmación es un estado separado
```

`operacion` es dueño del estado operativo; `documentos`, del documental. El resumen del viaje combina esos estados sin permitir escrituras ajenas. Se conserva el campo HTTP `estado` operativo durante la reorganización; los estados adicionales se incorporan al implementar su hito.

Verificar placa programa; inicio y entrega se confirman manualmente. Detectar llegada por geocerca crea evidencia y aviso, no pasa el viaje a `entregado`. Alerta media/alta abre `con_novedad` mediante la operación pública; cerradas todas, vuelve a `en_ruta`. Cancelar exige motivo. Transiciones registran usuario/motivo o regla/job. Aprobar el soporte no confirma RNDC; el cierre definitivo sigue pendiente hasta confirmar todas las remesas y notificar.

## 5. Contratos principales

### 5.1 API del backend

Rutas `/api` con sesión salvo login. Callback satelital privado; webhooks externos de voz/WhatsApp solo al implementar su épico y con firma/autenticación del adaptador. La tabla describe el contrato objetivo: voz y RNDC siguen pendientes y no se publican endpoints simulados para esas capacidades.

| Contrato | Responsabilidad |
|---|---|
| POST `/api/auth/login`; GET `/api/auth/me`; POST `/api/auth/logout` | Acceso, usuario y revocación |
| GET `/api/panel`, `/api/indicadores` | Operación, conexión, pendientes y métricas |
| GET/POST `/api/viajes`; POST `/api/viajes/importar` | Lista/filtros/paginación, alta con remesas e importación por viaje |
| GET `/api/viajes/{id}`; POST `/api/viajes/{id}/transiciones` | Detalle y cambio válido |
| GET `/api/viajes/{id}/posiciones`; PUT `/api/viajes/{id}/ruta` | Historial acotado y ruta/puntos de control |
| GET `/api/vehiculos`, `/api/conductores` | Catálogos y última posición |
| GET/PUT `/api/cuenta-satelital`; POST `/api/cuenta-satelital/sincronizar`, `/api/cuenta-satelital/consultar` | Credenciales/estado, verificación de placas y consulta manual |
| GET `/api/alertas`; POST `/api/alertas/{id}/atender`, `/api/alertas/{id}/cerrar` | Lista, comentario/atención y resolución justificada |
| GET/POST `/api/viajes/{id}/mensajes`, `/api/viajes/{id}/llamadas` | Historial/contacto manual autorizado |
| GET `/api/mensajes/sin-viaje`; POST `/api/mensajes/{id}/asociar` | Revisión/asociación de entradas dentro de la empresa |
| GET/POST `/api/viajes/{id}/cumplidos` | Documentos y carga manual de soporte |
| POST `/api/cumplidos/{id}/aprobar`, `/api/cumplidos/{id}/rechazar` | Revisión humana de una versión específica |
| POST `/api/cumplidos/{id}/transmitir`, `/api/cumplidos/{id}/confirmar-carga-manual` | RNDC aprobado o evidencia de carga manual |
| POST `/internal/satrack/callback`, `/internal/whatsapp/eventos`, `/internal/voz/{proveedor}/estado` | Eventos autenticados/deduplicados |
| WS `/internal/voz/{proveedor}/stream/{llamada_id}` | Audio si lo requiere el proveedor; autenticación de integración |
| GET `/health` | Disponibilidad API/BD sin secretos |

Alta de viaje: manifiesto, origen/destino, fechas con zona horaria, conductor, vehículo y remesas. Sin CRUD genérico de tablas. Errores: `401` sesión/firma, `404` recurso inaccesible, `409` conflicto, `422` validación con campo/mensaje, `503` indisponibilidad temporal y `500` genérico sin datos sensibles.

### 5.2 Scraper y resultados

`POST /v1/jobs`, con `X-Api-Key`: UUID `job_id`, `type` (`vehicles`/`positions`), `account` (`id`, `username`, `password`) y `plates`. `202` aceptado, `409` UUID repetido, `503` cola llena. `GET /health`: proveedor/trabajos/sesiones. Callback URL fijo por configuración, nunca por request.

`GET /v1/jobs/{job_id}`, también con `X-Api-Key`, permite consultar estado (`queued`/`running`/`done`), entrega del callback y resultado sin devolver credenciales. Resultados en memoria durante una hora, con límite de retención configurable; reiniciar elimina ese historial. `CALLBACK_URL` vacío permite usar el scraper de forma independiente. La colección Postman crea jobs y consulta sus resultados; credenciales solo en variables locales. Un job `vehicles` incluye ubicación, velocidad, estado y hora GPS cuando la ficha de Satrack los expone; campos ausentes permanecen `null`.

Callback: `job_id`, `type`, `status` (`ok`/`partial`/`failed`), `finished_at`, `positions`, `vehicles`, `errors`. Posición: placa, coordenadas/velocidad/hora GPS nullable, dirección, estado y texto original de fecha. HMAC-SHA256 del body exacto en `X-Signature`; `X-Job-Id` debe coincidir.

1. Backend reserva y confirma consulta en BD **antes** de enviar HTTP, fuera de la transacción; scraper acepta/ejecuta en segundo plano.
2. Una consulta por cuenta y todas sus placas; scheduler cada 60 s, consulta cada 5–10 min; programados desde una hora antes de salida y viajes en ruta/con novedad. Sin placas activas no se pide ubicación; verificar flota es un job aparte.
3. Scraper: tres jobs/sesiones, cola de 50, inactividad 15 min y timeout 120 s incluyendo espera. Selenium en proceso cancelable por cuenta: cancelar un hilo no garantiza parar el navegador.
4. Callback: cuatro intentos con pausas 2/10/30 s. Backend valida firma/UUID/tipo/versión de cuenta, bloquea consulta y confirma datos/eventos en una transacción. Duplicado aplicado → `200` sin repetir efectos.
5. A los 240 s sin respuesta: timeout/recuperación. Callback tardío válido aporta historial, sin reemplazar datos/estado recientes. Cambiar credenciales invalida resultados anteriores.
6. El backend reconcilia consultas pendientes con `GET /v1/jobs/{job_id}` cada cinco segundos. Un resultado terminado pasa por el mismo procesamiento idempotente del callback; si el scraper no conoce el UUID, se reenvía el mismo job mientras esté pendiente y su configuración siga vigente. Esto permite usar el servicio independiente con callback desactivado, sin cambiarlo. Los resultados completos validados se guardan en PostgreSQL, sin credenciales, y se consultan con sesión y aislamiento por transportadora.
7. Sincronizar `vehicles` incorpora todas las placas válidas de la cuenta, conserva alias/identificador y guarda sus datos satelitales disponibles. Una respuesta parcial no marca como ausentes vehículos que no incluye. El historial y la última posición se actualizan con las mismas reglas que `positions`.

Errores: `AUTH_FAILED`, `CAPTCHA_REQUIRED`, `PROVIDER_CHANGED`, `PROVIDER_UNAVAILABLE`, `TIMEOUT`, `VEHICLE_NOT_FOUND`, `POSITION_UNAVAILABLE`. Auth inválida detiene consulta; captcha/cambio aplica 15 min de backoff; tres fallos marcan conexión degradada. El mismo fallo se cuenta una vez aunque coincidan timeout local y callback tardío.

### 5.3 Efectos externos y voz

Mensajes/reportes/recordatorios/transmisiones reservados en BD con idempotencia; la intención se confirma junto al cambio que la origina. El trabajador reclama, ejecuta fuera de transacción y registra resultado/reintento. Las reclamaciones vencen para recuperar tareas tras un reinicio. Envío ambiguo exige reconciliar o revisar; una clave de deduplicación vencida no autoriza un reenvío automático. La aceptación del proveedor y la entrega al destinatario son estados distintos.

Voz: adaptador de telefonía y handler del proveedor elegido, herramientas iniciales fijas, validadas/auditadas y contexto inyectado. Sin agentes anidados, suspensiones genéricas, múltiples LLM activos ni catálogo dinámico. El diseño histórico conserva esas posibilidades futuras.

## 6. Parámetros iniciales del piloto

Defaults configurables por transportadora; se verifican antes de activar acciones automáticas.

| Área | Valores iniciales |
|---|---|
| Ubicación/reglas | Consulta 5 min; corredor 5 km; llegada 1 km; dos muestras distintas; detención <5 km/h durante 60 min; señal sin actualizar 30 min; margen de retraso 60 min |
| Contacto | Llamada cada 60 min; omitir con contacto hace <30 min; máximo 2 min/3 preguntas; dos intentos separados 10 min; descanso 22:00–05:00 en parada autorizada |
| WhatsApp/reportes | Un mensaje automático cada 15 min salvo cierre documental; resumen cada 3 h; avisos graves inmediatos; re-notificación alta cada 30 min |
| Cumplidos | Recordatorio cada 2 h; escalamiento a 6/24 h; tolerancia de peso propuesta 0,5 %; documento coincidente, firma/sello, fecha válida y observaciones revisadas |
| RNDC/indicadores | Hasta tres intentos de fallos inequívocos; reconciliar resultados inciertos; calendario colombiano; ventanas/umbrales oficiales por validar |

ETA solo con ruta/muestras suficientes y etiquetada como estimación. ETA del conductor separada de llegada pactada; velocidad de referencia nunca presentada como medición GPS.

## 7. Contenedores y configuración

| Servicio | Contenido | Puerto interno | Acceso local previsto | Persistencia |
|---|---|---|---|---|
| `web` | React + nginx + proxy `/api` | 80 | `localhost:8080` | Build reproducible |
| `api` | FastAPI, módulos de negocio, runner de tareas (`core/tareas`), Alembic | 8000 | `localhost:8000` diagnóstico | BD + documentos privados |
| `satrack` | FastAPI, Selenium, Chromium, sesiones en procesos | 8080 | `localhost:8081` diagnóstico | Evidencias; sesiones/jobs volátiles |
| `db` | PostgreSQL 16, sin PostGIS en el MVP | 5432 | Sin puerto público | `pg_data` |
| `openwa` | Repositorio OpenWA elegido + sesión del número dedicado | Por verificar en EP-08 | Sin exposición pública por defecto | Sesión/credenciales |

Diagnóstico enlazado solo a loopback; PostgreSQL/callback satelital en red privada. Puerto, autenticación y eventos de OpenWA se comprueban contra la revisión elegida antes del adaptador. Para piloto externo: HTTPS y únicamente webhooks necesarios.

Configuración base: `DATABASE_URL`, `SECRET_KEY`, `SATRACK_SERVICE_URL`, `SATRACK_SERVICE_API_KEY`, `CALLBACK_SECRET`, `PROVIDER`, límites del scraper, `SCHEDULER_ENABLED`, `SCHEDULER_INTERVAL_S`, `CONSULTA_TIMEOUT_S`, `SESSION_DAYS` y directorios privados. Los épicos de integración agregan solo configuración de proveedores activos; `.env.example` sin secretos reales.

EP-01 entregará `DOCKER.md` con comandos, puertos definitivos, contenido/volúmenes, bootstrap, demo, logs y respaldo/restauración; manual operativo subordinado a este plan.

## 8. Orden y dependencias

| Entrega | Épicos/dependencias | Resultado verificable |
|---|---|---|
| **A · Núcleo operativo** | EP-01–06; parte de EP-14/15 para login, viajes, flota, ajustes y demo | Login → Satrack → crear/verificar viaje → iniciar → consultar/mapear → entregar/cancelar |
| **B · Seguimiento asistido** | EP-07 sobre EP-06/ruta/datos; EP-08 sobre EP-02/03; EP-09 sobre EP-07/08; EP-10 sobre alertas/contactos; ampliar EP-14/15 | Regla → alerta → contacto → novedad → reporte, con trazabilidad |
| **C · Cumplido y piloto completo** | EP-11 sobre EP-03/08; EP-12 sobre EP-11/acceso RNDC; EP-13 sobre documentos/transmisiones; completar EP-14/15 | Pedir soporte → revisar/aprobar → RNDC o carga manual confirmada → cerrar → medir |

Validar acceso Satrack/campos GPS y acceso RNDC desde A para detectar bloqueos temprano. Simuladores permiten desarrollar, pero no acreditan integración real. Carga manual RNDC es una alternativa del MVP; si es la única disponible, el piloto se presenta como cierre asistido con carga manual.

### 8.1 Plan de ejecución del backend por hitos

**Alcance:** completar el backend por módulos, en hitos que se puedan verificar. Cada hito termina con un recorrido completo, pruebas en verde y contratos de arquitectura cumplidos. El microservicio Satrack se conserva sin cambios: código, endpoints, configuración y despliegue. El frontend operativo es una entrega aparte. Ningún paso pendiente se presenta como implementado.

| Hito | Módulos | Trabajo | Resultado verificable |
|---|---|---|---|
| **M0 · Separación** ✅ | `core`, `auditoria`, `acceso`, `operacion`, `satelital`, `indicadores`, y los paquetes documentados `documentos`, `mensajeria`, `monitoreo` y `agentes` | Módulos por dominio; errores de dominio; `core/eventos` y `core/tareas` (advisory lock y heartbeat); extensión de datos del vehículo; contratos de import-linter; pruebas por módulo sobre PostgreSQL. **Sin cambios de esquema ni de API** | `uv run lint-imports` con 6 contratos cumplidos; `uv run pytest` en verde; `alembic check` sin diferencias |
| **M1 · Núcleo** | `satelital`, `operacion` | **Consultas persistentes:** la consulta se registra antes del POST; si el POST es ambiguo, no se marca `fallido` y decide la reconciliación; se reconcilia con `GET /v1/jobs/{id}` cada 5 s (callback y GET pasan por el mismo `apply_result` idempotente); un UUID desconocido se reenvía mientras siga vigente y con reintentos acotados; el timeout de 240 s cuenta el fallo una sola vez. **Persistencia y flota:** se guarda el resultado completo sin credenciales; la sincronización trae toda la flota sin marcar ausentes los vehículos de una respuesta parcial; `vehiculos_satelitales` resuelve la deuda de §3.2; nuevo `GET /api/consultas-satelitales/{job_id}`. **Operación y API:** importación Excel atómica por manifiesto; listados paginados; `GET /api/configuracion`; colección Postman | login → conectar Satrack → flota completa → registrar viaje → `programado` → ubicación → entregar, **con el callback desactivado y reiniciando la API a mitad de un job** |
| **M2 · Cumplido manual** | `documentos`, `indicadores` | Archivos privados; cumplido por remesa con versiones; datos declarados por una persona con su procedencia; validaciones; aprobar o rechazar una versión concreta; `estado_documental` del viaje; pendientes por antigüedad en días hábiles (estimación) | Viaje entregado con 2 remesas → subir fotos → rechazar v1 → aprobar v2 → el pendiente desaparece |
| **M3 · WhatsApp y alertas** | `mensajeria` (primero un spike de OpenWA), `monitoreo` | Cola de envíos persistida con `Idempotency-Key`; webhook firmado; bandeja sin viaje; recordatorios de cumplido; puntos de control; reglas de señal, detención, llegada detectada y llegada pactada vencida; atender y cerrar alertas | login → registrar viaje → alerta atendida → pedir soporte por WhatsApp → foto recibida → revisar y aprobar su versión → pendientes al día |
| **M4 · Rutas y reportes** | `monitoreo`, `indicadores` | Ruta en GeoJSON con shapely: desvío, avance y ETA; resumen periódico y avisos | Desvío detectado y resumen enviado |
| Pendiente | `agentes`, `voz-service` | Voz, extracción y RNDC cuando se definan proveedor y acceso (§3.6) | — |

**Fronteras adicionales en M1:** las APIs internas devuelven DTO; las consultas compuestas se enlazan por instancia, sin registro global de extensiones. Se persiste la reacción a `viaje_registrado` junto al viaje y se comprueba la vigencia del liderazgo del runner. M3 amplía esa misma cola a mensajes y alertas; no introduce una segunda infraestructura de eventos.

**Decisiones de modelo para los hitos:**

- **Sin tabla `EstadoMonitoreo`:** las reglas se recalculan desde las posiciones guardadas.
- **La revisión del cumplido va en `VersionCumplido`:** decisión, motivo, quién revisó y cuándo; hay una sola decisión por versión.
- **Sin tabla `DiaNoLaboral`:** se usan los festivos de Colombia con la librería `holidays`.
- **`Reporte` y `RutaViaje` llegan en M4.**
- **La llegada a la geocerca no pasa el viaje a `entregado`.**
- **Sin velocidad de referencia para la ETA.**

### 8.2 Integraciones posteriores del backend

Las decisiones pendientes de la sección 10 se resuelven antes de implementar cada adaptador afectado. La revisión humana de los soportes y la aprobación de la transmisión al RNDC siguen siendo parte del flujo de negocio. Ningún agente puede reemplazarlas (§3.6).

## 9. Calidad y criterios de entrega

- **Backend:** sesión/vencimiento/logout, aislamiento, validaciones/Excel, reservas concurrentes, estados/aprobaciones, scheduler y migraciones sobre PostgreSQL.
- **Arquitectura:** `uv run lint-imports` sin contratos rotos; `tests/test_arquitectura.py` (fronteras + `alembic check`); runner de tareas probado sin FastAPI; cada módulo con sus pruebas en `tests/<modulo>/`.
- **Integraciones:** firmas, duplicados, resultados tardíos/fuera de orden, credenciales cambiadas, navegador bloqueado, reinicio sin callback, OpenWA desconectado, llamada fallida y RNDC incierto.
- **Reglas/documentos:** datos incompletos/obsoletos/repetidos, sin ruta, desvío/llegada, deduplicación de alertas, foto ilegible, remesa incorrecta, diferencias de peso y aprobación invalidada por cambio del soporte.
- **Frontend:** build TypeScript, errores por campo, sesión vencida, remesas múltiples, flujo completo escritorio/móvil y acceso autorizado a documentos.
- **Operación:** arranque limpio, reinicio, respaldo/restauración con claves/archivos, healthchecks, recursos y secretos ausentes de logs/respuestas.
- **Piloto:** integración real y límites visibles; sombra → asistido; línea base de minutos manuales, demora documental/cierre, errores, uso y costo por viaje. Metas acordadas antes de iniciar y resultados medidos.

**Definition of Done:** criterio del épico cumplido, pruebas con evidencia, contratos/documentación actualizados y ningún error crítico abierto. MVP completo = EP-01–15 y recorrido C; A no se etiqueta como producto completo.

## 10. Decisiones pendientes

| Decisión | Capacidad afectada | Resolver antes de implementar |
|---|---|---|
| Acceso/campos Satrack | Scraper real/reglas GPS | Cuenta piloto: login/captcha/2FA, placas, coordenadas, hora y velocidad; registrar disponibilidad real |
| Ruta/puntos de control | Desvío/avance/geocercas | GeoJSON cargado + coordenadas de origen/destino/paradas, calculado con shapely (sin PostGIS); definir de dónde salen las coordenadas (pin manual o geocodificación) con el coordinador |
| Contrato OpenWA | Mensajes/fotos | Fijar repositorio/revisión, número, endpoints, autenticación, webhooks, puerto y sesión |
| Telefonía/voz/visión | Llamadas/extracción real | Un proveedor inicial por función; validar acceso, costos, formatos, firmas y latencia |
| RNDC/indicadores | Transmisión/indicador regulatorio | Verificar acceso, campos, confirmación/idempotencia y definiciones oficiales; mantener alternativa manual |
| Transportadora piloto | Utilidad | Acordar contactos/autorizaciones, parámetros, línea base y criterios de avance |

No bloquean planificación/demo; las capacidades afectadas no se consideran listas con datos inventados o pruebas exclusivamente simuladas.
