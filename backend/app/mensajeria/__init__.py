"""Mensajería: conversación con el conductor por WhatsApp (OpenWA). Se implementa en M3, tras un spike de OpenWA.

Será dueño de: canales_whatsapp (sesión OpenWA por transportadora, secretos cifrados), mensajes.
Hará: enviar por la cola de tareas persistida con `Idempotency-Key`, recibir el webhook firmado
(`X-OpenWA-Signature`, sha256 sobre el body original) y deduplicar por id externo, descargar fotos y audios en
segundo plano, bandeja de mensajes sin viaje con asociación humana, verificar consentimiento antes de contactos
automáticos, solicitudes y recordatorios de cumplido (2 h; escalamiento a 6/24 h).

Archivos previstos:
- openwa.py: ÚNICO archivo que conoce OpenWA. Pasar a la API oficial de Meta cambia solo este archivo.
- models.py, schemas.py, servicio.py, router.py, enlaces.py.

Publicará: `foto_recibida`, `mensaje_recibido`. Escuchará: `recordatorio_cumplido` de documentos.
Depende de: core, auditoria, acceso, operacion. No conoce documentos ni monitoreo: se enlazan por eventos.
"""
