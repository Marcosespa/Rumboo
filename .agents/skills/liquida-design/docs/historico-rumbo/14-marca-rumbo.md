# Marca Rumbo

Identidad visual del producto (antes "FleteControl", renombrado a **Rumbo** en junio 2026).

> **Rumbo** — Tu camión y tu plata, al día.

## Nombre

"Rumbo" es una palabra que todo conductor usa a diario: corta, fácil de pronunciar
y de recordar. Transmite dirección, propósito y confianza — llevar el negocio por
buen camino.

## Logo

El logo es un **cóndor andino parado de perfil** con el collar característico en
ámbar. El cóndor es el ave del escudo nacional de Colombia y transmite
majestuosidad, vigilancia y dominio del territorio.

Archivos en el repositorio:

| Archivo | Uso |
| --- | --- |
| `frontend/public/brand/condor.png` | Logo original en alta resolución (1192x880). Material impreso, splash, marketing. |
| `frontend/public/brand/condor-sm.png` | Versión 256px. Header de la app, login, tamaños pequeños en UI. |
| `frontend/public/icons/icon.png` | Versión 512px. Favicon, apple-touch-icon, manifest PWA. |

Reglas de uso:

- El logo siempre va acompañado del wordmark "Rumbo" en la primera aparición de cada pantalla.
- No deformar, rotar ni recolorear la silueta.
- El collar ámbar es parte de la identidad: no eliminarlo.

## Paleta de colores

Dos colores de marca sacados de la carretera: **azul ruta** (señalización vial:
confianza, profesionalismo) y **ámbar señal** (línea central y señales
preventivas: acción, alta visibilidad). Fondos cálidos tipo papel.

```json
{
  "brand": {
    "name": "Rumbo",
    "tagline": "Tu camión y tu plata, al día"
  },
  "primary": {
    "default": "#1A4F8B",
    "dark": "#0E3260",
    "light": "#3F77BE",
    "subtle": "#E3EDF8",
    "onPrimary": "#FFFFFF",
    "onPrimaryMuted": "#BAD2EC"
  },
  "accent": {
    "default": "#F5A623",
    "dark": "#C97F0A",
    "subtle": "#FBF1DC",
    "onAccent": "#3D2A05"
  },
  "background": {
    "app": "#FAF8F4",
    "surface": "#FFFFFF",
    "surfaceAlt": "#F1EDE4",
    "inverse": "#1C1C1A"
  },
  "text": {
    "primary": "#1C1C1A",
    "secondary": "#6B6962",
    "muted": "#9B988E",
    "inverse": "#FAF8F4",
    "link": "#1A4F8B"
  },
  "border": {
    "default": "#E7E2D7",
    "strong": "#D8D3C7",
    "focus": "#1A4F8B"
  },
  "semantic": {
    "success": { "default": "#0F6E56", "subtle": "#EAF6F0", "text": "#085041" },
    "warning": { "default": "#BA7517", "subtle": "#FBF1DC", "text": "#633806" },
    "error":   { "default": "#D8432F", "subtle": "#FCEBE8", "text": "#A32D2D" },
    "info":    { "default": "#1A4F8B", "subtle": "#E3EDF8", "text": "#0E3260" }
  }
}
```

### Tokens en el código

Los tokens viven en `frontend/src/index.css` (Tailwind v4, bloque `@theme`) y se
usan como clases (`bg-primary`, `text-mist`, `border-line`, etc.):

| Token | Light | Dark | Rol |
| --- | --- | --- | --- |
| `ink` | `#1C1C1A` | `#F4F2EC` | Texto principal |
| `paper` | `#FAF8F4` | `#141413` | Fondo de la app |
| `mist` / `stoneSoft` | `#6B6962` | `#A5A39A` | Texto secundario |
| `cloud` / `cloudSoft` | `#EAE5DA` / `#F1EDE4` | `#2A2925` / `#1C1B19` | Superficies suaves |
| `primary` | `#1A4F8B` | `#7FB1E8` | Azul ruta: acciones, enlaces, marca |
| `primarySoft` | `#3F77BE` | `#A9CBF1` | Hover del primario |
| `accent` | `#F5A623` | `#F5A623` | Ámbar señal: CTA principal (tomar foto) |
| `line` | `#E7E2D7` | `#2E2D29` | Bordes |
| `success` / `warning` / `error` | `#0F6E56` / `#BA7517` / `#D8432F` | claros | Estados |

> Nota histórica: el token `forest` (verde del diseño anterior) fue renombrado a
> `primary` en todo el frontend.

## Principios de diseño para carretera

1. **Una pregunta por pantalla**: ¿cuánto me queda?, ¿qué hago ahora?, ¿hay algo urgente?
2. **El CTA principal (tomar foto) es grande y ámbar**: usable con guantes, con vibración y con una mano.
3. **Estados con color + ícono + texto**, nunca solo color (sol directo, daltonismo).
4. **Palabras del conductor**: "Te queda", "Entró", "Salió", "Te deben", "Ya me pagaron". Cero jerga contable.
5. **Texto grande**: 16px mínimo en cuerpo; cifras protagonistas a 38px.
6. **Navegación de 4 destinos máximo** con etiqueta visible siempre.

## Identificadores técnicos

El nombre visible del producto es Rumbo, pero los identificadores de
infraestructura conservan `fletecontrol` para no romper volúmenes, imágenes y el
proyecto iOS ya generados:

- `appId` de Capacitor: `com.fletecontrol.app`
- Nombres de servicios/volúmenes en `docker-compose*.yml`
- Carpeta raíz del repositorio
