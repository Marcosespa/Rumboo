"""Eventos de dominio: un módulo reacciona a otro sin que el que publica sepa quién escucha.

1. El servicio que publica llama `publicar(db, nombre, **datos)` antes de confirmar su transacción.
   El evento queda guardado en la sesión, sin ejecutar nada.
2. Después del commit, quien confirmó (router o tarea) llama `await bus.despachar(db)`.
3. Cada suscriptor abre su propia sesión. Si falla, la transacción original ya está confirmada.

Las suscripciones las hace la raíz de composición (app/main.py), nunca el módulo que publica. Cada app
tiene su propio Bus para que las dependencias enlazadas (sesiones, settings, clientes) no se mezclen.

Las reacciones que deben sobrevivir a un reinicio usan la cola de tareas persistida, no este bus.
"""
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)
_PENDIENTES = "rumboo.eventos"


def publicar(db, nombre, **datos):
    db.info.setdefault(_PENDIENTES, []).append((nombre, datos))


class Bus:
    def __init__(self):
        self._suscriptores = defaultdict(list)

    def suscribir(self, nombre, funcion):
        self._suscriptores[nombre].append(funcion)

    async def despachar(self, db):
        for nombre, datos in db.info.pop(_PENDIENTES, []):
            for funcion in self._suscriptores[nombre]:
                try:
                    await funcion(**datos)
                except Exception:
                    logger.error("Falló un suscriptor de %s; la operación original ya quedó guardada", nombre)
