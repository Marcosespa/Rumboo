---
name: revisar
description: Puerta de calidad antes de commitear, abrir PR o desplegar. Ejecuta scripts/verificar.sh, lanza revisor-codigo y auditor-seguridad en paralelo y da un veredicto. Úsalo con "revisa", "/revisar", "¿está listo?".
---

1. `git status --short` y `git diff --stat main...HEAD`. Sin cambios → termina.
2. `scripts/verificar.sh`. Un fallo es bloqueante. Si la BD no está disponible, el resultado es "no verificado", nunca "ok".
3. En un solo mensaje, lanza `revisor-codigo` y `auditor-seguridad`. Omite el auditor si solo cambian docs o la landing.
4. Confirma en el código cada hallazgo bloqueante o importante y descarta los falsos.
5. Responde:
```
VEREDICTO: listo | con observaciones | no listo
Puerta: ok | falla | no verificado
Bloqueantes / Importantes / Menores: archivo:línea — arreglo
```
No apliques arreglos ni hagas commit sin que se pida.
