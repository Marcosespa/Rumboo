"""Errores de negocio. Los servicios los lanzan sin saber de HTTP; core.web los traduce a respuestas.

Así un mismo caso de uso funciona igual desde un router, una tarea de fondo o un agente.
"""


class ErrorDominio(Exception):
    def __init__(self, mensaje):
        super().__init__(mensaje)
        self.mensaje = mensaje


class NoEncontrado(ErrorDominio):
    """El recurso no existe o pertenece a otra transportadora."""


class Conflicto(ErrorDominio):
    """La operación choca con el estado actual."""


class Invalido(ErrorDominio):
    """Los datos no cumplen una regla de negocio."""


class NoAutorizado(ErrorDominio):
    """Credenciales o sesión inválidas."""
