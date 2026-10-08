"""Acceso: quién eres y a qué transportadora perteneces.

Dueño de: transportadoras, usuarios, sesiones.
Expone: login/me/logout (router), la dependencia `deps.User` para los demás routers y, en `servicio`,
el usuario de un token, la creación de usuarios (CLI) y los parámetros de la transportadora.
Depende de: core, auditoria.
"""
