"""Documentos: el cumplido, núcleo de la tesis. Se implementa en M2.

Será dueño de: archivos_privados, cumplidos (uno por remesa), versiones_cumplido y su tabla de archivos.
Hará: guardar archivos privados (límite de tamaño/MIME, nombre generado, sha256), registrar versiones con datos
declarados por una persona y su procedencia, validar identificación, fecha, firma, sello, peso (tolerancia
0,5 %) y observaciones, aprobar o rechazar UNA versión concreta y llevar `estado_documental` del viaje.

Archivos previstos:
- almacenamiento.py: ÚNICO archivo que toca el disco (LocalFileStorage).
- revision.py: aprobar/rechazar. Acciones solo humanas: import-linter impide que app.agentes las importe.
- models.py, schemas.py, servicio.py, router.py, enlaces.py.

Escuchará (vía app/main.py): `foto_recibida` de mensajeria para crear una versión con origen WhatsApp.
Depende de: core, auditoria, acceso, operacion. No conoce mensajeria ni satelital.
Mientras RNDC esté pendiente, no marca confirmación RNDC ni cierre definitivo del viaje.
"""
