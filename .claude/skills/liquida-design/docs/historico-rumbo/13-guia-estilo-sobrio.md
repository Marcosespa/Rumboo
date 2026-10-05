# Guia de estilo visual sobrio (referencia Nivo)

Esta guia define la base visual de Rumbo para el MVP: estilo editorial, limpio, sobrio y con alto contraste.

## Principios visuales

- Estilo editorial, limpio y sobrio.
- Contraste alto para lectura clara en mobile.
- Verde `forest` como acento primario de marca.
- Componentes suaves con bordes redondeados y jerarquias tipograficas simples.
- Soporte dual de modo `light` y `dark`.

## Tipografia oficial

- Familia principal: `Inter`.
- Uso global: toda la interfaz usa `Inter` como base.
- Pesos recomendados:
  - `w600` para titulos y acciones principales.
  - `w500` para feedback destacado (snackbars).
  - Regular para texto de cuerpo.

Escalas de referencia:

- App bar title: `17`, `w600`.
- Filled button text: `14`, `w600`.
- Input hint: `16`.
- Input label: `12`, `w600`.

## Colores de marca

Paleta Light:

- `ink`: `#000000`
- `paper`: `#FFFFFF`
- `stone`: `#4A4A4A`
- `stoneSoft`: `#6B6B6B`
- `mist`: `#9A9A9A`
- `cloud`: `#E5E5E5`
- `cloudSoft`: `#F3F3F3`
- `forest`: `#1A3C34`
- `forestSoft`: `#254F46`
- `line`: `#D4D4D4`

Paleta Dark:

- `ink`: `#F4F4F1`
- `paper`: `#0B0B0B`
- `stone`: `#B8B8B6`
- `stoneSoft`: `#9E9E9C`
- `mist`: `#6F6F6D`
- `cloud`: `#242424`
- `cloudSoft`: `#161616`
- `forest`: `#8FE3C5`
- `forestSoft`: `#5FC1A0`
- `line`: `#2A2A2A`

Color de error:

- `error`: `#E05A4B`

## Tokens UI

- Superficies:
  - Fondo global: `paper`.
  - Cards/campos: `cloudSoft`.
  - Bordes/divisores: `line`.
- Boton primario:
  - Background `forest`, radio `999`, padding `22 x 14`, texto `Inter 14 w600`.
- Boton secundario:
  - Foreground `ink`, borde `1px` `ink`, radio `999`, padding `20 x 14`.
- Inputs:
  - Fill `cloudSoft`, padding `18 x 16`, radio `14`.
  - Borde normal `line`, foco `forest` con `1.5`.
  - Hint `Inter 16` color `mist`.
  - Label `Inter 12 w600` color `stone`.
- App bar:
  - Fondo `paper` alpha `0.92`, titulo `Inter 17 w600`, elevacion `0`.
- Snackbar:
  - Fondo `ink`, texto `paper` `Inter w500`, radio `14`.
- Checkbox:
  - Seleccionado `forest`, no seleccionado `cloudSoft`.
  - Check `paper`, borde `line` ancho `1.5`, radio `5`.

## Forma y espaciado

- Radios principales: `5`, `14`, `16`, `999`.
- Espaciado vertical de controles primarios: `14` a `16`.
- Componentes con baja elevacion para mantener la estetica plana/editorial.

## Implementacion en CSS global

- Variables de color por token (`--nivo-*`) en `:root` y `:root[data-theme='dark']`.
- `Inter` como base tipografica global, con fallback variable (`Inter var`).
- Transiciones suaves para cambio de tema (`260ms`).
- Headings con stack display (`Neue Haas Grotesk Display` -> `Inter Display` -> `Inter`).
- `forest` como acento fuerte del sistema (incluyendo `::selection`).

## Source of truth de estilo

- Tokens globales en el CSS global del frontend.
- Esta guia como estandar para producto, diseno y desarrollo.
- Componentes y pantallas deben respetar estos tokens en version web y version movil.
