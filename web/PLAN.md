# Plan de implementación — Web (bandeja web Rumboo)

> Bandeja web donde el coordinador de tráfico de la transportadora entra con usuario y contraseña, registra viajes y ve dónde va cada camión.
> Consume la API de [backend/PLAN.md](../backend/PLAN.md). Diseño según la skill [`.claude/skills/liquida-design`](../.claude/skills/liquida-design/SKILL.md) (marca Rumbo), de uso obligatorio en esta carpeta (ver §2 y [CLAUDE.md](CLAUDE.md)).
>
> **Referencia técnica subordinada al [Plan maestro del MVP](../backend/PLAN.md).** Ese documento gobierna alcance, contratos y decisiones; esta referencia conserva el diseño previo y no acredita el estado de la implementación.

## 1. Stack

| Pieza | Elección | Por qué |
|---|---|---|
| Base | React 19 + Vite + TypeScript | SPA detrás de login; no necesita SSR. Mismo stack que el design system |
| Estilos | Tailwind CSS 4 con los tokens de la marca en `@theme` | Los tokens (`--color-primary`, radios, sombras) ya existen en `liquida-design/tokens/` |
| Rutas | React Router 7 | Rutas protegidas simples |
| Datos del servidor | TanStack Query | Caché, estados de carga/error y **refresco automático** de posiciones (`refetchInterval`) sin escribirlo a mano |
| Mapa | Leaflet + react-leaflet con teselas de OpenStreetMap | Gratis, sin API key |
| Iconos | lucide-react | Única librería de iconos permitida por la marca |
| Formularios | Estado controlado de React + errores del backend | Un solo formulario grande (viaje): no justifica una librería |
| Fechas | `Intl.DateTimeFormat('es-CO', { timeZone: 'America/Bogota' })` | Sin dependencias |

Sin Redux ni librería de componentes: el estado global es solo la sesión (React Context) y el resto vive en TanStack Query.

## 2. Design system: skill `liquida-design`

Toda la interfaz se construye con la skill del proyecto en [`.claude/skills/liquida-design/`](../.claude/skills/liquida-design/). **Antes de crear o cambiar cualquier pantalla o componente se carga la skill** (en Claude Code: skill `liquida-design`) y se siguen su `readme.md` (CONTENT FUNDAMENTALS, VISUAL FOUNDATIONS, ICONOGRAPHY) e `INTEGRACION.md`. Esto queda fijado en [web/CLAUDE.md](CLAUDE.md) para que se aplique automáticamente.

### 2.1 Qué se toma de la skill y a dónde va

| De la skill | A `web/` | Cómo |
|---|---|---|
| `tokens/colors.css`, `typography.css`, `spacing.css`, `effects.css`, `base.css` | `src/index.css` (bloque `@theme` de Tailwind 4) | Se traduce cada `--color-*`, `--radius-*`, `--shadow-*` a tokens de Tailwind con **los mismos nombres y valores**. No se inventan colores ni radios nuevos |
| `tokens/fonts.css` | `index.html` | `@import` de Google Fonts: Inter (UI) + Inter Tight (display) |
| `components/*/<Nombre>.jsx` + `.d.ts` + `.prompt.md` | `src/components/ui/<Nombre>.tsx` | Son la **especificación**: mismas props, variantes, estados y copy. Se reescriben en TSX + Tailwind, no se copian las clases `.r-*` |
| `components/liquida-ui.css` | — | Referencia exacta de medidas y estados cuando haya duda |
| `components/navigation/AppHeader`, `BottomNav` | `src/components/layout/` | Base del `AppShell`; la barra lateral de escritorio reutiliza los mismos ítems e iconos |
| `assets/logos/condor-sm.png`, `icon.png`, `condor.svg` | `public/brand/` | Logo del login, header y favicon |
| `guidelines/*.card.html` | — | Especímenes para revisar colores, tipografía, espaciado y voz de marca |
| `_adherence.oxlintrc.json` | `web/.oxlintrc.json` | Reglas de adherencia a la marca, ejecutadas con `npx oxlint` en el script `lint` |

### 2.2 Componentes de la skill por pantalla

| Componente | Uso en la bandeja |
|---|---|
| `Button`, `IconButton` | Acciones ("Entrar al panel", "Guardar viaje", "Iniciar ruta"); variante `accent` solo para "Conecta tu cuenta de Satrack" |
| `Field`, `SelectField`, `TextAreaField`, `SegmentedControl` | Login, formulario de viaje, ajustes de Satrack, motivo de cancelación |
| `StatusPill` | Estado del viaje y de la cuenta Satrack (color + icono + texto) |
| `FilterChip` | Filtros por estado en Viajes |
| `AlertCard` | Errores de la API, Satrack con credenciales inválidas |
| `EmptyState` | Listas vacías con la siguiente acción |
| `HeroPanel` + `Metric` | Cifra protagonista del panel (viajes en ruta) |
| `StatTile` | Conteos por estado |
| `SectionCard`, `ListRow` | Tarjetas de detalle, listas de viajes y vehículos |
| `Icon` | Adaptador de `lucide-react` |

### 2.3 Reglas de la marca que aplican aquí

- Paleta: papel `#FAF8F4`, tinta `#1C1C1A`, primario azul ruta `#1A4F8B`. El **ámbar `#F5A623` se reserva a la acción humana pendiente** (con texto `#3D2A05`, nunca blanco).
- Sin gradientes, imágenes de fondo ni emoji; solo iconos Lucide; el cóndor es el único arte.
- Copy en español colombiano con tuteo, sentence case, botones verbo + objeto, placeholders "Ej. …", placas en mayúsculas.
- Estados siempre con color + icono + texto.

### 2.4 Huecos de la skill a resolver al implementar

- `ui_kits/bandeja/` está vacío: no hay referencia de pantalla para la bandeja, así que las pantallas se componen con los componentes de la skill siguiendo §4. Conviene diseñarlas primero con la skill (prototipo HTML) y guardarlas ahí.
- La skill es mobile-first (contenido máx. 520 px) y está pensada para conductores; la bandeja la usa un coordinador en computador, así que se amplía el ancho (§7) sin cambiar tokens ni componentes.
- El `readme.md` menciona `rumbo-ui.css` y `ui_kits/rumbo-app/`, pero en la carpeta están `liquida-ui.css` y `ui_kits/bandeja/`.

## 3. Estructura de carpetas

```
web/
├── public/brand/              # condor-sm.png, icon.png (de liquida-design/assets/logos)
├── src/
│   ├── main.tsx               # QueryClient, Router, AuthProvider
│   ├── index.css              # Tailwind + @theme con tokens de marca + fuentes
│   ├── api/
│   │   ├── client.ts          # fetch con base /api, Bearer token, manejo de 401 y errores
│   │   ├── types.ts           # tipos de la API (Viaje, Posicion, Vehiculo…)
│   │   └── hooks.ts           # useViajes, useViaje, useCrearViaje, useFlota, usePanel…
│   ├── auth/
│   │   ├── AuthContext.tsx    # token en localStorage, login(), logout(), usuario actual
│   │   └── RequireAuth.tsx    # redirige a /login si no hay sesión
│   ├── components/
│   │   ├── ui/                # Button, Field, SelectField, StatusPill, FilterChip,
│   │   │                      # SectionCard, HeroPanel, StatTile, ListRow, EmptyState, AlertCard
│   │   ├── layout/            # AppShell, Sidebar (escritorio), BottomNav (móvil), AppHeader
│   │   └── map/               # FleetMap, TripMap (marcadores + recorrido)
│   ├── features/
│   │   ├── login/LoginPage.tsx
│   │   ├── panel/PanelPage.tsx
│   │   ├── viajes/            # ViajesPage, NuevoViajePage, ViajeDetallePage, EstadoViajePill
│   │   ├── flota/FlotaPage.tsx
│   │   └── ajustes/AjustesPage.tsx
│   └── lib/format.ts          # fechas, pesos ("12.000 kg"), "hace 5 min", placas
├── CLAUDE.md                  # obliga a usar la skill liquida-design en esta carpeta
├── .oxlintrc.json             # reglas de adherencia a la marca (de la skill)
├── index.html
├── vite.config.ts             # proxy /api → http://localhost:8000 en desarrollo
├── nginx.conf                 # producción: sirve el build y hace proxy de /api
└── Dockerfile                 # build con Node 22 → nginx:alpine
```

Los componentes de `components/ui/` se reescriben en TSX + Tailwind usando como especificación los `.jsx` y `.d.ts` de `liquida-design/components/` (ver §2).

## 4. Pantallas

| Ruta | Pantalla | Pregunta que responde | Contenido |
|---|---|---|---|
| `/login` | Login | — | Cóndor + "Rumboo", campos **Usuario** y **Contraseña**, botón "Entrar al panel", error "Usuario o contraseña incorrectos" |
| `/` | Panel | ¿Cómo va mi operación ahora? | Panel héroe oscuro con **viajes en ruta**; tiles por estado (programados, sin verificar, entregados hoy); tarjeta del estado de Satrack; mapa de la flota activa; lista de viajes activos |
| `/viajes` | Viajes | ¿Qué viajes tengo y en qué van? | Chips de filtro por estado, búsqueda por manifiesto/placa/conductor, lista con estado, ruta, placa y "último reporte hace X min" |
| `/viajes/nuevo` | Nuevo viaje | — | Formulario en 4 secciones: Viaje, Remesas (agregar/quitar filas, total de peso), Conductor, Vehículo |
| `/viajes/:id` | Detalle | ¿Dónde va este camión? | Encabezado con manifiesto, ruta y estado + acciones; mapa con recorrido y última posición; datos de conductor y vehículo; remesas; historial de eventos |
| `/flota` | Flota | ¿Dónde están mis vehículos? | Mapa con todos los vehículos con posición + lista con placa, dirección, hora del último reporte y si está verificado en Satrack |
| `/ajustes` | Ajustes | ¿Está conectado Satrack? | Usuario de Satrack, contraseña (nunca se muestra la guardada), estado de la conexión, último error y botón "Sincronizar vehículos". Cerrar sesión |

### Estados del viaje (siempre color + icono + texto)

| Estado | Texto | Color | Icono |
|---|---|---|---|
| `registrado` | Sin verificar | warning | `Clock3` |
| `programado` | Programado | info | `CalendarClock` |
| `en_ruta` | En ruta | primary | `Truck` |
| `entregado` | Entregado | success | `CheckCircle2` |
| `cancelado` | Cancelado | neutro | `XCircle` |

### Acciones del detalle

| Estado actual | Acción | Confirmación |
|---|---|---|
| programado | "Iniciar ruta" | Diálogo simple |
| en_ruta | "Marcar entregado" | Diálogo simple |
| registrado / programado / en_ruta | "Cancelar viaje" | Diálogo con **motivo obligatorio** |
| registrado | "Verificar placa" | Lanza la sincronización con Satrack |

## 5. Flujo de usuario

```
/login ──(ok)──▶ /  Panel
                 ├─▶ "Nuevo viaje" ─▶ formulario ─(guardado)─▶ /viajes/:id  (estado Sin verificar o Programado)
                 ├─▶ Viajes ─▶ detalle ─▶ Iniciar ruta ─▶ el mapa se actualiza cada 60 s ─▶ Marcar entregado
                 ├─▶ Flota ─▶ mapa de vehículos
                 └─▶ Ajustes ─▶ conectar Satrack (primer uso)
```

**Primer uso:** si la transportadora no tiene cuenta Satrack, el panel muestra una tarjeta de aviso "Conecta tu cuenta de Satrack para empezar a ver tus camiones" con botón a Ajustes.

## 6. Integración con el backend

- **Mismo origen:** en desarrollo Vite hace proxy de `/api` a `http://localhost:8000`; en producción nginx hace proxy de `/api` al servicio `api`. Así no hay CORS ni URLs distintas por ambiente.
- **Sesión:** `login()` guarda el token en `localStorage` y el cliente lo envía como `Authorization: Bearer`. Cualquier `401` limpia la sesión y redirige a `/login` conservando la ruta a la que se quería ir.
- **Errores:** `client.ts` convierte la respuesta en `ApiError { status, detail, errores[] }`. El formulario de viaje pinta cada error junto a su campo (`conductor.telefono` → campo Teléfono) y el resto se muestra en una `AlertCard`.
- **Refresco:** `refetchInterval` de 60 s en panel, flota y detalle de viajes activos (el scheduler consulta cada 5 min, así que no hace falta más). Se pausa cuando la pestaña no está visible.
- **Validación en el cliente:** solo la necesaria para ayudar al usuario (campos obligatorios, formato de placa y celular mientras escribe). La validación real es la del backend.

## 7. Diseño y responsive

Se siguen los fundamentos de `liquida-design` (§2) adaptados a una bandeja de escritorio:

- Fondo papel `#FAF8F4`, primario azul ruta `#1A4F8B`, Inter (UI) + Inter Tight (títulos y cifras), tarjetas con radio 28 px y sombras suaves, sin gradientes ni ilustraciones.
- **Ámbar solo para "la acción humana pendiente"**: en este MVP, el CTA "Conecta tu cuenta de Satrack" del primer uso.
- Copy en español colombiano, tuteo, sentence case, placas en mayúsculas (`ABC 123`), pesos en formato es-CO (`12.000 kg`), sin emoji.

| Ancho | Navegación | Layout |
|---|---|---|
| < 768 px (móvil) | Barra inferior fija con 5 destinos: Panel, Viajes, Nuevo, Flota, Ajustes | Una columna, gutter 20 px, mapa de 280 px de alto |
| 768–1279 px | Barra inferior | Dos columnas en el panel (mapa + lista) |
| ≥ 1280 px | Barra lateral izquierda | Contenido máx. 1200 px; detalle en dos columnas (mapa a la izquierda, datos a la derecha) |

El design system es mobile-first (520 px máx.); aquí se mantiene la estética pero se amplía el ancho porque el coordinador trabaja sobre todo en computador. Tap targets mínimos de 44 px y foco visible con el anillo azul de la marca.

## 8. Estados de carga, vacío y error

- **Carga:** esqueletos con fondo `cloud-soft` en listas; spinner en botones mientras se envía.
- **Vacíos con siguiente acción:** "Aún no tienes viajes. Registra el primero para empezar a monitorearlo." / "Este viaje todavía no tiene posiciones. Llegan cuando el viaje está en ruta."
- **Errores:** `AlertCard` con botón "Reintentar". Si Satrack está con `credenciales_invalidas`, aviso persistente en el panel con enlace a Ajustes.

## 9. Despliegue

`Dockerfile` multi-etapa: `node:22-alpine` ejecuta `npm ci && npm run build`; `nginx:alpine` sirve `dist/` con fallback a `index.html` para las rutas del SPA y proxy de `/api` a `http://api:8000`. Expuesto en el puerto 8080 del docker compose.

## 10. Pruebas

- **Vitest + Testing Library** para lo que tiene lógica: cliente de API (401 → logout, mapeo de errores), formateadores y el formulario de viaje (agregar remesas, total de peso, errores por campo).
- **Prueba manual guiada** con el `seed-demo` del backend y el proveedor `simulator`: login → crear viaje → ver el camión moverse en el mapa → marcar entregado.
