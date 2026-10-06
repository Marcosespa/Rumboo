# Integración: del design system a tu app (web + móvil)

Tu app real ya existe: **fleteControl** (https://github.com/Marcosespa/fleteControl) — una PWA React + Vite que con Capacitor genera la app móvil. **No necesitas exportar código de aquí para "generar" la app**: este proyecto es la referencia de diseño que tu codebase debe seguir. Los archivos HTML/JSX de aquí son *referencias de diseño de alta fidelidad*, no código de producción para copiar tal cual.

## Ruta recomendada: Claude Code + SKILL.md

1. Descarga este proyecto como zip (botón de descarga en el chat).
2. Descomprímelo dentro de tu repo, por ejemplo en `fleteControl/.claude/skills/rumbo-design/` (la carpeta debe contener el `SKILL.md` en su raíz).
3. Abre Claude Code en tu repo y pídele cosas como:
   - *"Usa la skill rumbo-design y alinea frontend/src/index.css con los tokens del design system"*
   - *"Recrea la pantalla de Alertas siguiendo ui_kits/rumbo-app/AlertsScreen.jsx"*
   Claude Code leerá el readme, los tokens y los componentes y trabajará con fidelidad a la marca.

## Ruta manual: qué copiar y a dónde

| De este proyecto | A tu repo | Cómo |
|---|---|---|
| `tokens/*.css` (colores, tipo, espaciado, sombras) | `frontend/src/index.css` (bloque `@theme` de Tailwind 4) | Traduce cada `--color-*`, `--radius-*`, etc. a tu `@theme`. Los valores ya coinciden con tu index.css actual; este proyecto añade dark mode, semánticos subtle y aliases. |
| `tokens/fonts.css` | `frontend/index.html` o CSS global | El `@import` de Google Fonts (Inter + Inter Tight). **Decisión de marca: Inter Tight es la fuente display oficial** (no hay licencia de Neue Haas). |
| `components/*/<Name>.jsx` | `frontend/src/components/ui/` | Úsalos como especificación: tu `Button.jsx` y `SectionCard.jsx` ya existen; los de aquí documentan variantes/estados completos (accent CTA, loading, pills de estado, etc.). En tu repo se estilizan con Tailwind, no con las clases `.r-*`. |
| `components/rumbo-ui.css` | — | Referencia exacta de medidas/estados si prefieres CSS plano en vez de Tailwind. |
| `ui_kits/rumbo-app/*.jsx` | `frontend/src/features/*` | Referencia visual de cada pantalla (Panel, Foto, Verificar, Vehículos, Alertas) con copy y jerarquía finales. |
| `assets/logos/` | `frontend/public/brand/` | Ya los tienes en el repo; aquí están los mismos. |
| `readme.md` | `docs/14-marca-rumbo.md` | Actualiza tu doc de marca con las secciones CONTENT FUNDAMENTALS / VISUAL FOUNDATIONS / ICONOGRAPHY. |

## Web y móvil

- **Web:** `npm run build` en `frontend/` → PWA lista para desplegar.
- **Móvil:** la misma UI vía Capacitor (`npx cap sync && npx cap open android/ios`). No hay diseño separado: el sistema es mobile-first, así que la app móvil hereda todo automáticamente.

## Fidelidad

Alta fidelidad (hifi): colores, radios, sombras, tipografía y copy de este proyecto son finales y salieron de tu propio `index.css` + `docs/14-marca-rumbo.md`. Recrea pixel-perfect usando los patrones existentes de tu codebase (Tailwind 4, lucide-react).
