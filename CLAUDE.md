@AGENTS.md

## Agentes (solo Claude Code)
Las reglas compartidas van en `AGENTS.md`, que Codex también lee. Aquí solo lo propio de Claude Code.

- `arquitecto-critico`: antes de módulos, tablas, integraciones o cambios de contrato.
- `/revisar`: antes de commitear; es parte de Terminado. Lanza `revisor-codigo` + `auditor-seguridad`.
- Verifica cada hallazgo de un agente antes de aplicarlo, incluidos los de Codex (`/codex:review`, `/codex:rescue`).
