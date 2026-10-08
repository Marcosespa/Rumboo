---
name: revisar
description: Puerta de calidad de Rumboo antes de commitear, abrir PR o desplegar. Ejecuta scripts/verificar.sh, lanza en paralelo los agentes revisor-codigo y auditor-seguridad sobre el diff, verifica sus hallazgos y entrega un veredicto. Úsalo cuando el usuario diga "revisa", "/revisar", "¿está listo?", "antes de commitear" o "antes de desplegar".
---

# /revisar

Argumento opcional: alcance (`main...HEAD` por defecto, un commit, una rama o rutas). Siempre incluye los cambios sin commitear.

## Pasos

1. **Alcance.** `git status --short` y `git diff --stat main...HEAD` + `git diff --stat HEAD`. Si no hay cambios, dilo y termina. Anota qué áreas toca: acceso/sesiones, secretos, webhooks/callbacks, archivos, integraciones externas, migraciones, runner.

2. **Puerta mecánica.** Ejecuta `scripts/verificar.sh`. Si falla, muestra la salida relevante. Los fallos de ruff, lint-imports, alembic check o pytest son bloqueantes; no los reinterpretes como "menores". Si la BD de pruebas no está disponible, repórtalo como **no verificado**, nunca como aprobado.

3. **Revisión en paralelo.** En un solo mensaje lanza:
   - `revisor-codigo` con el alcance.
   - `auditor-seguridad` con el alcance y las áreas sensibles detectadas en el paso 1.
   Si el diff solo toca documentación o la landing, omite el auditor y dilo.

4. **Verifica los hallazgos.** Para cada hallazgo bloqueante o importante, abre el código citado y confirma el escenario. Descarta los que no se sostienen y explica por qué en una línea. No apliques arreglos durante la revisión salvo que el usuario lo pida.

5. **Veredicto.** Responde con:
   ```
   VEREDICTO: listo | listo con observaciones | no listo
   Puerta mecánica: <ok | falla: ... | no verificado: ...>
   Bloqueantes: <lista con archivo:línea y arreglo propuesto>
   Importantes: <lista>
   Menores: <solo los que valen la pena>
   Descartados: <n, con motivo breve>
   Definición de terminado (CLAUDE.md §6): <qué punto falta, si alguno>
   ```
   "listo" exige puerta mecánica ok y cero bloqueantes. Pregunta si quiere que apliques los arreglos; no hagas commit ni push.
