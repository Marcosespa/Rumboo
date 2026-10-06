# web/ — bandeja web de Rumboo

- **Antes de crear o modificar cualquier pantalla, componente, estilo o texto de la interfaz, carga la skill `liquida-design`** (`.claude/skills/liquida-design/`) y sigue su `readme.md` e `INTEGRACION.md`.
- Los tokens de `tokens/*.css` son la única fuente de colores, tipografía, radios y sombras: tradúcelos al `@theme` de `src/index.css` sin inventar valores nuevos.
- Los componentes de `components/*/` (`.jsx` + `.d.ts` + `.prompt.md`) son la especificación de `src/components/ui/`: mismas props, variantes, estados y copy, reescritos en TSX + Tailwind.
- Iconos solo de `lucide-react`. Ámbar solo para la acción humana pendiente. Estados siempre con color + icono + texto. Copy en español colombiano con tuteo y sin emoji.
- El plan de esta carpeta está en [PLAN.md](PLAN.md).
