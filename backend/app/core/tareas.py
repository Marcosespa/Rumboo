"""Tareas de fondo, independientes del proceso que las ejecuta.

Cada módulo define sus tareas como funciones async sin argumentos, con sus dependencias ya enlazadas, y la raíz
de composición (app/main.py) las registra. El runner no conoce FastAPI ni los módulos de negocio.

Hoy lo arranca el lifespan de la API. Si mañana se necesita un proceso aparte, un `app/worker.py` crea el mismo
Runner con las mismas tareas y la API usa SCHEDULER_ENABLED=false. La lógica no cambia.

Un advisory lock de PostgreSQL garantiza que un solo proceso ejecute las tareas aunque haya varias réplicas.
El heartbeat (`estado()`) vive en memoria: al separar el worker se debe mover a la base de datos.
"""
import asyncio
import logging
from dataclasses import dataclass
from typing import Awaitable, Callable
from sqlalchemy import text
from app.core.db import now

logger = logging.getLogger(__name__)
LOCK_ID = 7_201_001  # identificador fijo del advisory lock de las tareas


@dataclass(frozen=True)
class TareaPeriodica:
    nombre: str
    intervalo_s: float
    ejecutar: Callable[[], Awaitable[None]]


class Runner:
    def __init__(self, engine, tareas, espera_lock_s=5):
        self.engine = engine
        self.tareas = list(tareas)
        self.espera_lock_s = espera_lock_s
        self.activo = False
        self.ultimo_ciclo = {}
        self._conexion = None

    def estado(self):
        return {"activo": self.activo, "ultimo_ciclo": dict(self.ultimo_ciclo)}

    async def ejecutar(self):
        try:
            while not await asyncio.to_thread(self._tomar_lock):
                await asyncio.sleep(self.espera_lock_s)
            self.activo = True
            await asyncio.gather(*(self._ciclo(tarea) for tarea in self.tareas))
        finally:
            self.activo = False
            self._soltar_lock()

    async def _ciclo(self, tarea):
        while True:
            try:
                await tarea.ejecutar()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.error("Falló la tarea %s; se reintentará", tarea.nombre)
            self.ultimo_ciclo[tarea.nombre] = now()
            await asyncio.sleep(tarea.intervalo_s)

    def _tomar_lock(self):
        if self.engine.dialect.name != "postgresql":
            return True
        try:
            conexion = self.engine.connect()
        except Exception:
            logger.error("No fue posible conectar con la base de datos para iniciar las tareas")
            return False
        # Lock de sesión: sobrevive al commit y se mantiene mientras la conexión siga abierta.
        if conexion.scalar(text("SELECT pg_try_advisory_lock(:id)"), {"id": LOCK_ID}):
            conexion.commit()
            self._conexion = conexion
            return True
        conexion.close()
        return False

    def _soltar_lock(self):
        if self._conexion is None:
            return
        try:
            self._conexion.execute(text("SELECT pg_advisory_unlock(:id)"), {"id": LOCK_ID})
            self._conexion.commit()
        except Exception:
            # Sin unlock confirmado, la conexión no vuelve al pool con el lock tomado.
            self._conexion.invalidate()
        finally:
            self._conexion.close()
            self._conexion = None
