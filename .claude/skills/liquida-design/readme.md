# Rumbo Design System

**Rumbo** — *Tu camión y tu plata, al día.*

Rumbo es una app mobile-first para conductores, repartidores, taxistas y pequeños transportistas en Colombia que necesitan ordenar caja, cobros y estado del vehículo desde una foto. El usuario fotografía un recibo, remesa, cuenta de cobro o documento del vehículo y Rumbo lo convierte en un registro claro de gastos, ingresos, cartera o alertas operativas. No es software contable: es una herramienta simple de orden y cobro. *"Toma una foto y tu negocio se ordena solo."*

**Producto:** PWA React + Vite (app móvil vía Capacitor, backend FastAPI con OCR). Un solo producto/superficie: la app móvil.

**Usuario:** conductores independientes, pequeños transportistas, repartidores, taxis, motocarros. Sus necesidades: saber cuánto queda en caja este mes, registrar gastos (gasolina, peajes, mantenimiento), controlar cobros pendientes, y mantener SOAT/tecnomecánica/mantenimientos al día.

**Fuentes** (el lector puede explorarlas para mejorar diseños):
- Repo GitHub: https://github.com/Marcosespa/fleteControl — la verdad de diseño vive en `frontend/src/index.css` (tokens `@theme`) y `docs/14-marca-rumbo.md`. `docs/13-guia-estilo-sobrio.md` es contexto histórico (dirección verde antigua, ya reemplazada por azul + ámbar).
- Copias locales de los docs del repo en `docs/` de este proyecto.
- Logos subidos por el usuario en `assets/logos/`.

## Principios de diseño

1. **Una pregunta principal por pantalla.** El panel responde "¿cuánto te queda?"; Vehículos responde "¿está todo al día?".
2. **Cifras y estados visibles de inmediato** — la cifra protagonista va en un panel oscuro al tope, a 38px.
3. **CTA grande y claro**, especialmente "Tomar foto" (el único uso del ámbar).
4. **Estados siempre con color + icono + texto.** Nunca solo color.
5. **Lenguaje cotidiano**, no jerga contable.
6. **Navegación inferior** con 5 destinos máximo y etiqueta siempre visible.
7. Primera pantalla útil, no promocional: dashboards operativos, flujos de captura, formularios de verificación.

## CONTENT FUNDAMENTALS

- **Idioma:** español colombiano, tuteo directo ("Te queda", "Revisa el monto antes de guardar"). La app le habla al usuario de "tú"; el usuario es dueño de los datos ("Tus vehículos", "Tus gastos").
- **Vocabulario operativo, nunca contable:** «Te queda», «Entró», «Salió», «Te deben», «Ya me pagaron», «Toma una foto y listo». PROHIBIDO: "balance neto", "ingresos brutos", "cuentas por cobrar", "flujo de caja", "conciliación".
- **Casing:** sentence case en todo (títulos, botones, labels). MAYÚSCULAS solo en overlines con tracking 0.2em ("ESTE MES", "DASHBOARD") y placas ("WLN 482").
- **Botones = verbo + objeto, cortos:** "Tomar foto", "Guardar registro", "Entrar al panel", "Resolver", "Marcar como pagado".
- **Subtítulos = una frase que explica qué responde la sección:** "Lo que realmente te queda después de ingresos y gastos."
- **Estados canónicos de vehículo:** «Urgente», «Pendiente», «Al día». Pagos: «Pagado», «Por vencer», «Revisar».
- **Placeholders con patrón "Ej. …":** "Ej. marcos o tu correo", "Ej. Tanqueada completa para el viaje a Medellín."
- **Vacíos siempre sugieren la próxima acción:** "Aún no hay gastos guardados. Sube una foto para empezar."
- **Sin emoji.** Tono claro, sobrio y confiable; directo sin ser corporativo ni decorativo. Montos siempre formato es-CO sin decimales: `$ 1.250.000`.

## VISUAL FOUNDATIONS

- **Colores:** fondo papel cálido `#FAF8F4`, tinta `#1C1C1A`. Primario **azul ruta** `#1A4F8B` (confianza, señalización vial) para acciones y links. Acento **ámbar señal** `#F5A623` reservado al CTA de foto (texto oscuro `#3D2A05` encima, nunca blanco). Superficies suaves cloud `#F1EDE4`/`#EAE5DA`, líneas `#E7E2D7`. Semánticos: success `#0F6E56`, warning `#BA7517`, error `#D8432F`, cada uno con su versión "subtle" para fondos. Dark mode existe vía `[data-theme="dark"]`.
- **Tipografía:** Inter para UI (cuerpo 16px mínimo, controles 14px). **Inter Tight** para display: headings y cifras. Cifra protagonista 38px/600, título de pantalla 28px, sección 22px, tracking -0.01em. Overlines 11px/600 uppercase tracking 0.2em.
- **Fondos:** planos, color papel. SIN gradientes, SIN imágenes de fondo, SIN texturas ni ilustraciones decorativas. El contraste viene de paneles oscuros (ink/primary) sobre papel.
- **Tarjetas:** papel con borde `--color-line` 1px, radio 28px, sombra baja cálida (`0 6px 24px rgba(0,0,0,0.04)`). Subtarjetas internas cloudSoft translúcido al 70%, radio 24px. Panel héroe oscuro radio 32px con sombra profunda. Evitar paneles anidados del mismo color.
- **Radios:** controles 16px · chips internos 14px · subtarjetas 24px · tarjetas 28px · paneles 32px · pills 999px. Generosos siempre.
- **Sombras:** sistema de 4 niveles, siempre suaves y de baja opacidad (0.04–0.18). Nada de inner shadows.
- **Animación:** una sola curva ease-out, 300ms, `transition: all`. Entrada de pantalla: slide-up 12px + fade 250ms. Spinner para loading. Sin bounces, sin loops decorativos.
- **Hover:** lift `translateY(-2px)` + sombra más profunda + color un paso más claro (primary→primary-soft) o fondo cloudSoft en ghosts. **Press/focus:** anillo `0 0 0 4px rgba(26,79,139,0.1)`.
- **Bordes:** 1px sólidos color línea; dashed solo para empty states. En paneles oscuros: blanco al 12–20%.
- **Transparencia y blur:** solo en cromo fijo — header (`paper/90` + blur 24px) y nav inferior (`paper/95` + blur 24px). No en contenido.
- **Layout:** una columna, gutter 20px, gap 16px entre secciones, contenido máx 520px centrado. Header sticky arriba; nav flotante fija abajo (con safe-area). Tap target mínimo 44px.
- **Imaginería:** sin fotografías en la UI. El único arte es el logo del cóndor. Color cálido, nunca frío.

## ICONOGRAPHY

- **Sistema único: [Lucide](https://lucide.dev)** (el código del producto importa `lucide-react`). Trazo 2px, `currentColor`, tamaño base 16px (18px en CTAs grandes). Sin icon font propio, sin PNGs de iconos, sin emoji, sin caracteres unicode como iconos.
- En este design system se consume vía CDN UMD (`https://unpkg.com/lucide@0.469.0/dist/umd/lucide.min.js`) + el componente `Icon` (`components/icons/Icon.jsx`): `<Icon name="Camera" />`.
- **Iconos canónicos por destino:** Panel=ChartColumn · Vehículos=CarFront · Alertas=Bell · Foto=Camera · Nuevo=PlusCircle. Otros frecuentes: Fuel, Wrench, ShieldCheck, TriangleAlert, CheckCircle2, Clock3, WalletCards, CircleDollarSign, ArrowRight, RefreshCw, LogOut, Sparkles, FileUp.
- **Logos** en `assets/logos/`: `condor.png` (principal alta resolución), `condor-sm.png` (header/login), `icon.png` (ícono PWA), `logo_exacto_sin_cambios.svg` y `logo_vectorizado_editable.svg` (vectores). El cóndor andino de perfil con collar ámbar siempre acompaña al wordmark "Rumbo".

## Índice

| Ruta | Contenido |
|---|---|
| `styles.css` | Entrada global (solo @imports) |
| `tokens/` | `colors.css` (paleta + dark), `typography.css`, `spacing.css`, `effects.css`, `fonts.css`, `base.css` |
| `components/rumbo-ui.css` | Clases CSS compartidas (`.r-btn`, `.r-card`, `.r-pill`, `.r-navbar`…) |
| `components/buttons/` | `Button`, `IconButton` |
| `components/forms/` | `Field`, `SelectField`, `TextAreaField`, `SegmentedControl` |
| `components/feedback/` | `StatusPill`, `FilterChip`, `AlertCard`, `EmptyState` |
| `components/layout/` | `SectionCard`, `HeroPanel` (+`Metric`), `StatTile`, `ListRow` |
| `components/navigation/` | `AppHeader` (+`BrandChip`), `BottomNav` |
| `components/icons/` | `Icon` (adaptador Lucide) |
| `guidelines/` | Tarjetas de especímenes (colores, tipo, espaciado, marca) |
| `ui_kits/rumbo-app/` | App móvil interactiva: login → panel → foto → verificar → vehículos → alertas |
| `assets/logos/` | Logos del cóndor (PNG + SVG) |
| `docs/` | Docs originales del repo (producto, marca, guías) |

Cada componente trae `<Name>.d.ts` (contrato de props) y `<Name>.prompt.md` (uso + ejemplo). Namespace del bundle: `window.RumboDesignSystem_252059`.

## Caveats

- **Tipografía display:** el doc de marca original mencionaba Neue Haas Grotesk Display (licenciada). Rumbo no tiene licencia, así que **Inter Tight** (Google Fonts) es la fuente display oficial desde junio 2026.
- El dark mode está tokenizado pero el producto actual es light-first; úsalo con criterio.
